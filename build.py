#!/usr/bin/env python3
"""Validate the cards and build the site (and optionally the PDF).

    python build.py --check      validate only
    python build.py              validate, then build site/
    python build.py --pdf        also print the_cards.pdf and facilitator_guide.pdf (needs playwright)
    python build.py --drafts     list the cards still marked as drafts
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
CARDS = ROOT / "cards"
IMAGES = ROOT / "images"
OUT = ROOT / "site"

CARD_TYPES = ["technology", "trend", "social", "nature", "worldview"]
LENS_FIELDS = {
    "celebrates": "Celebrates",
    "fears": "Fears",
    "would_do": "Would do",
    "blind_spot": "Blind spot",
}
FACILITATOR_FIELDS = {"prompts", "pairs_with", "watch_for", "going_further"}
STATUSES = {"draft", "reviewed"}
SHORTENERS =re.compile(r"https?://(goo\.gl|bit\.ly|t\.co)/")
SUSPICIOUS = [
    (re.compile(r'\\"'), "literal backslash-quote"),
    (re.compile(r"&amp;"), "double-escaped &amp;"),
    (re.compile(r"[ 	]{2,}"), "repeated spaces"),
]
REF = re.compile(r"\[\^([^\]]+)\]")
PLACEHOLDER = re.compile(r"^[\s.]*$")


def md_inline(text):
    """Markdown for a fragment, without the wrapping <p>."""
    text = re.sub(r"^(https?://\S+)$", r"<\1>", str(text or "").strip())
    html = markdown.markdown(text, extensions=["sane_lists"])
    return re.sub(r"^<p>(.*)</p>$", r"\1", html, flags=re.S)


def load_cards():
    cards = []
    for path in sorted(CARDS.glob("*.y*ml"), key=lambda p: p.name.lower()):
        data = yaml.safe_load(path.read_text(encoding="utf8")) or {}
        data["slug"] = path.stem
        data["path"] = path
        cards.append(data)
    return cards


def texts(card):
    """Every string on a card that may contain footnote references."""
    body = (card.get("body") or {}).get("paragraphs") or []
    consider = card.get("consider") or []
    caption = (card.get("image") or {}).get("caption") or ""
    lens = (card.get("lens") or {}).values()
    return [str(t) for t in [*body, *consider, caption, *lens]]


def validate(cards):
    errors, warnings = [], []
    seen = {}
    titles = {(c.get("title") or "").strip() for c in cards}
    for c in cards:
        name = c["path"].name
        live = bool(c.get("live"))
        # Problems on live cards are errors; on stubs they're only warnings.
        problem = errors if live else warnings

        def err(msg, sink=problem):
            sink.append(f"{name}: {msg}")

        title = (c.get("title") or "").strip()
        if not title:
            err("no title", errors)
        elif title.lower() in seen:
            err(f"duplicate title (also {seen[title.lower()]})", errors)
        else:
            seen[title.lower()] = name
        if "&amp;" in name or "'" in name:
            err("odd characters in filename", warnings)
        if c.get("card_type") not in CARD_TYPES:
            err(f"card_type {c.get('card_type')!r} is not one of {CARD_TYPES}", errors)

        paras = (c.get("body") or {}).get("paragraphs") or []
        if not isinstance(paras, list):
            err("body.paragraphs must be a list", errors)
            continue
        if live and not paras:
            err("no body paragraphs")
        if any(PLACEHOLDER.match(str(p)) for p in paras):
            err("placeholder '.' paragraph")
        lens = c.get("lens") or {}
        if c.get("card_type") == "worldview":
            for key in LENS_FIELDS:
                if not str(lens.get(key) or "").strip():
                    err(f"worldview card needs a 'lens' entry for {key!r}")
        elif lens:
            err("only worldview cards have a 'lens'", errors)
        consider = c.get("consider") or []
        if live and not consider:
            err("no 'consider' prompts")
        if any(PLACEHOLDER.match(str(p)) for p in consider):
            err("placeholder '.' consider prompt")

        src = (c.get("image") or {}).get("source")
        if src and not (IMAGES / src).exists():
            err(f"image {src!r} not found in images/")
        if live and not src:
            err("no image", warnings)

        everything = [*texts(c), *map(str, (c.get("footnotes") or {}).values()), title]
        for text in everything:
            if SHORTENERS.search(text):
                err("link shortener (may be dead, and hides the source)", warnings)
            for rx, what in SUSPICIOUS:
                if rx.search(text):
                    err(f"{what}: {text[:50]!r}", warnings)
        for text in [*paras, *consider]:
            if str(text)[:1].islower() and not str(text).startswith("co-"):
                err(f"starts with a lowercase letter: {str(text)[:40]!r}", warnings)

        fac = c.get("facilitator") or {}
        for k in set(fac) - FACILITATOR_FIELDS:
            err(f"unknown facilitator field {k!r} (expected one of {sorted(FACILITATOR_FIELDS)})", errors)
        for k in ("prompts", "pairs_with", "going_further"):
            if k in fac and not isinstance(fac[k], list):
                err(f"facilitator.{k} must be a list", errors)
        for other in fac.get("pairs_with") or []:
            if other not in titles:
                err(f"facilitator.pairs_with: no card is titled {other!r}", errors)
        status = (c.get("meta") or {}).get("status")
        if status is not None and status not in STATUSES:
            err(f"meta.status {status!r} is not one of {sorted(STATUSES)}", errors)
        image = c.get("image") or {}
        if live and image.get("source") and not image.get("citation"):
            err("image has no credit (image.citation)", warnings)

        notes = c.get("footnotes") or {}
        refs = {k for t in texts(c) for k in REF.findall(t)}
        for k in sorted(refs - {str(k) for k in notes}):
            err(f"footnote [^{k}] is referenced but not defined")
        for k in sorted({str(k) for k in notes} - refs):
            err(f"footnote {k!r} is defined but never referenced", warnings)
        for k, v in notes.items():
            if "TODO" in str(v):
                err(f"footnote {k!r} is a TODO")
    return errors, warnings


def render_card(c):
    """Turn a card into HTML fragments, with footnotes numbered per card."""
    notes = {str(k): v for k, v in (c.get("footnotes") or {}).items()}
    order = []

    def number(m):
        key = m.group(1)
        if key not in notes:
            return m.group(0)
        if key not in order:
            order.append(key)
        n = order.index(key) + 1
        return f'<sup class="fn"><a href="#fn-{c["slug"]}-{key}">{n}</a></sup>'

    def fmt(t):
        return md_inline(REF.sub(number, str(t)))

    image = c.get("image") or {}
    return {
        "slug": c["slug"],
        "title": c["title"],
        "card_type": c["card_type"],
        "image": image.get("source"),
        "caption": fmt(image.get("caption") or ""),
        "citation": image.get("citation") or "",
        "link": image.get("link") or "",
        "paragraphs": [markdown.markdown(REF.sub(number, str(p))) for p in c["body"]["paragraphs"]],
        "lens": [(label, fmt(c["lens"][k])) for k, label in LENS_FIELDS.items() if (c.get("lens") or {}).get(k)],
        "consider": [fmt(p) for p in c.get("consider") or []],
        "sources": [
            {"id": f"fn-{c['slug']}-{k}", "n": i + 1, "html": md_inline(notes[k])}
            for i, k in enumerate(order)
        ],
        "status": (c.get("meta") or {}).get("status"),
        "provenance": [provenance(s) for s in (c.get("meta") or {}).get("sources") or []],
    }


def provenance(source):
    """One line of a card's history, from a meta.sources entry."""
    parts = [str(source.get("source_comment") or "").strip()]
    if source.get("source_link"):
        parts.append(f"<{source['source_link']}>")
    if source.get("update_date"):
        parts.append(f"({source['update_date']})")
    return md_inline(" ".join(p for p in parts if p))


def render_facilitator(c, slugs):
    """The facilitator notes for a card, or None if it has none."""
    fac = c.get("facilitator") or {}
    if not fac:
        return None
    return {
        "slug": c["slug"],
        "title": c["title"],
        "card_type": c["card_type"],
        "status": (c.get("meta") or {}).get("status"),
        "prompts": [md_inline(p) for p in fac.get("prompts") or []],
        "pairs_with": [(t, slugs.get(t)) for t in fac.get("pairs_with") or []],
        "watch_for": md_inline(fac.get("watch_for")) if fac.get("watch_for") else "",
        "going_further": [md_inline(p) for p in fac.get("going_further") or []],
    }


def build(cards):
    live = [c for c in cards if c.get("live")]
    worldviews = [c for c in live if c["card_type"] == "worldview"]
    live = [c for c in live if c["card_type"] != "worldview"]
    stubs = [c for c in cards if not c.get("live")]
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=False)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(IMAGES, OUT / "images")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    for css in (ROOT / "templates").glob("*.css"):
        shutil.copy(css, OUT / css.name)

    howto = (ROOT / "how-to-play.md").read_text(encoding="utf8")
    howto = env.from_string(howto).render(live_cards=live, worldview_cards=worldviews, stub_cards=stubs)
    howto_html = markdown.markdown(
        howto, extensions=["footnotes", "md_in_html", "sane_lists"]
    )
    (OUT / "index.html").write_text(
        env.get_template("page.html").render(content=howto_html, title="A Game About Possible Futures"),
        encoding="utf8",
    )
    deck = [*live, *worldviews]
    (OUT / "cards.html").write_text(
        env.get_template("cards.html").render(cards=[render_card(c) for c in deck]),
        encoding="utf8",
    )
    slugs = {c["title"]: c["slug"] for c in deck}
    notes = [n for n in (render_facilitator(c, slugs) for c in sorted(deck, key=lambda c: c["title"].lower())) if n]
    (OUT / "facilitator.html").write_text(
        env.get_template("facilitator.html").render(notes=notes, total=len(deck)),
        encoding="utf8",
    )
    print(f"built site/ with {len(live)} cards and {len(worldviews)} worldviews ({len(stubs)} stubs left out)")


def print_pdf():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto((OUT / "cards.html").resolve().as_uri())
        page.wait_for_load_state("networkidle")
        # Cards use fixed-height columns; text that overflows spills sideways.
        for title in page.eval_on_selector_all(
            "section.card",
            "els => els.filter(e => e.scrollWidth > e.clientWidth + 1)"
            ".map(e => e.querySelector('h2').textContent)",
        ):
            print(f"warning: card text overflows the card: {title}")
        page.pdf(path=str(OUT / "the_cards.pdf"), prefer_css_page_size=True, print_background=True)
        page.goto((OUT / "facilitator.html").resolve().as_uri())
        page.wait_for_load_state("networkidle")
        page.pdf(path=str(OUT / "facilitator_guide.pdf"), prefer_css_page_size=True, print_background=True)
        browser.close()
    print("wrote site/the_cards.pdf and site/facilitator_guide.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--pdf", action="store_true", help="also write the PDFs")
    ap.add_argument("--drafts", action="store_true", help="list cards still marked as drafts")
    args = ap.parse_args()

    cards = load_cards()
    if args.drafts:
        drafts = [c["title"] for c in cards if c.get("live") and (c.get("meta") or {}).get("status") == "draft"]
        print(f"{len(drafts)} draft cards:")
        for title in drafts:
            print(" ", title)
        return
    errors, warnings = validate(cards)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    n_drafts = sum(1 for c in cards if c.get("live") and (c.get("meta") or {}).get("status") == "draft")
    if n_drafts:
        print(f"{n_drafts} live cards are still marked as drafts (python build.py --drafts lists them)")
    if errors:
        sys.exit(f"{len(errors)} error(s)")
    if args.check:
        return
    build(cards)
    if args.pdf:
        print_pdf()


if __name__ == "__main__":
    main()
