#!/usr/bin/env python3
"""Find a freely licensed image on Wikimedia Commons and attach it to a card.

    python tools/commons_image.py search "humpback whale breaching" [-n 10] [--preview DIR]
    python tools/commons_image.py use "File:Humpback whale.jpg" "Whale rebound" \
        --caption "A humpback whale breaching"

`search` lists candidates with their licence and size. With --preview it also
saves small thumbnails into DIR so that you can look at them before choosing.
`use` downloads a 1000px-wide copy into images/, and writes the card's image
block (source, caption, citation and link), including the author and licence
that Commons asks for. Only CC BY, CC BY-SA, CC0 and public domain files are
accepted.
"""
import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cardfile  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = "FutureGameCards/1.0 (https://github.com/notionparallax/future_game; ben_doherty@bvn.com.au)"
IMAGES = Path(__file__).resolve().parent.parent / "images"
OK_LICENCE = re.compile(r"^(CC BY(-SA)?\b|CC0|Public domain|PD\b)", re.I)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def api(**params):
    params["format"] = "json"
    return json.loads(get(API + "?" + urllib.parse.urlencode(params)))


def plain(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def info(titles=None, search=None, limit=10, width=1000):
    q = dict(action="query", prop="imageinfo", iiprop="url|size|mime|extmetadata", iiurlwidth=width)
    if titles:
        q["titles"] = titles
    else:
        q.update(generator="search", gsrnamespace=6, gsrsearch=search + " filetype:bitmap", gsrlimit=limit)
    pages = (api(**q).get("query") or {}).get("pages") or {}
    out = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        meta = ii.get("extmetadata") or {}
        out.append(dict(
            title=p["title"],
            width=ii["width"], height=ii["height"], mime=ii["mime"],
            thumb=ii["thumburl"], page=ii["descriptionurl"],
            licence=plain((meta.get("LicenseShortName") or {}).get("value")),
            artist=plain((meta.get("Artist") or {}).get("value")),
            description=plain((meta.get("ImageDescription") or {}).get("value")),
        ))
    return out


def slug(title):
    stem = re.sub(r"^File:", "", title)
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", stem)
    return re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()[:60]


def search(args):
    results = info(search=args.query, limit=args.n, width=400 if args.preview else 1000)
    if args.preview:
        Path(args.preview).mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(results, 1):
        ok = "ok " if OK_LICENCE.match(r["licence"]) else "NO "
        print(f"{i:2}. {ok}{r['title']}\n    {r['width']}x{r['height']}  {r['licence']}  by {r['artist'][:50]}")
        if r["description"]:
            print(f"    {r['description'][:110]}")
        if args.preview:
            ext = ".png" if r["mime"] == "image/png" else ".jpg"
            dest = Path(args.preview) / f"{i:02}{ext}"
            dest.write_bytes(get(r["thumb"]))
            print(f"    preview: {dest}")


def use(args):
    title = args.file if args.file.startswith("File:") else "File:" + args.file
    found = info(titles=title, width=args.width)
    if not found:
        sys.exit(f"{title}: not found on Commons")
    r = found[0]
    if not OK_LICENCE.match(r["licence"]):
        sys.exit(f"{title}: licence {r['licence']!r} is not one we can use")
    ext = ".png" if r["mime"] == "image/png" else ".jpg"
    name = f"commons-{slug(r['title'])}{ext}"
    IMAGES.mkdir(exist_ok=True)
    (IMAGES / name).write_bytes(get(r["thumb"]))
    card = cardfile.load(args.card)
    artist = r["artist"] or "Unknown author"
    card["image"] = {
        "source": name,
        "caption": args.caption or "",
        "citation": f"{artist[:80]}, {r['licence']}, via Wikimedia Commons",
        "link": r["page"],
    }
    cardfile.dump(args.card, card)
    print(f"{args.card}: {name} ({r['licence']}, by {artist[:50]})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--preview", help="directory to save small thumbnails into")
    s.set_defaults(fn=search)
    u = sub.add_parser("use")
    u.add_argument("file", help="Commons file title, e.g. 'File:Example.jpg'")
    u.add_argument("card", help="card name (the filename without .yaml)")
    u.add_argument("--caption", help="what the picture shows")
    u.add_argument("--width", type=int, default=1000)
    u.set_defaults(fn=use)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
