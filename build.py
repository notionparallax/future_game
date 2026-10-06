#!/usr/bin/env python3
"""Validate the cards and build the site (and optionally the PDF).

    python build.py --check      validate only
    python build.py              validate, then build site/
    python build.py --pdf        also print site/the_cards.pdf (needs playwright)
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

CARD_TYPES = ["technology", "trend", "social", "nature"]
REF = re.compile(r"\[\^([^\]]+)\]")
PLACEHOLDER = re.compile(r"^[\s.]*$")


def md_inline(text):
    """Markdown for a fragment, without the wrapping <p>."""
    html = markdown.markdown(str(text or ""), extensions=["sane_lists"])
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
    return [str(t) for t in [*body, *consider, caption]]


def validate(cards):
    errors, warnings = [], []
    seen = {}
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
        if live and not paras:
            err("no body paragraphs")
        if any(PLACEHOLDER.match(str(p)) for p in paras):
            err("placeholder '.' paragraph")
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
        "consider": [fmt(p) for p in c.get("consider") or []],
        "sources": [
            {"id": f"fn-{c['slug']}-{k}", "n": i + 1, "html": md_inline(notes[k])}
            for i, k in enumerate(order)
        ],
    }


def build(cards):
    live = [c for c in cards if c.get("live")]
    stubs = [c for c in cards if not c.get("live")]
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=False)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(IMAGES, OUT / "images")
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copy(ROOT / "templates" / "style.css", OUT / "style.css")

    howto = (ROOT / "how-to-play.md").read_text(encoding="utf8")
    howto = env.from_string(howto).render(live_cards=live, stub_cards=stubs)
    howto_html = markdown.markdown(
        howto, extensions=["footnotes", "md_in_html", "sane_lists"]
    )
    (OUT / "index.html").write_text(
        env.get_template("page.html").render(content=howto_html, title="A Game About Possible Futures"),
        encoding="utf8",
    )
    (OUT / "cards.html").write_text(
        env.get_template("cards.html").render(cards=[render_card(c) for c in live]),
        encoding="utf8",
    )
    print(f"built site/ with {len(live)} cards ({len(stubs)} stubs left out)")


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
        browser.close()
    print("wrote site/the_cards.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--pdf", action="store_true", help="also write the PDF")
    args = ap.parse_args()

    cards = load_cards()
    errors, warnings = validate(cards)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        sys.exit(f"{len(errors)} error(s)")
    if args.check:
        return
    build(cards)
    if args.pdf:
        print_pdf()


if __name__ == "__main__":
    main()
