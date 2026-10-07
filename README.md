# A Game About Possible Futures

A card game that helps teams think about the future. The cards are YAML files in
[`cards/`](cards), and the how-to-play text is [`how-to-play.md`](how-to-play.md).

## Building

    pip install -r requirements.txt
    python build.py --check     # validate the cards
    python build.py             # build site/ (index.html, cards.html)
    python build.py --pdf       # also print site/the_cards.pdf (needs: python -m playwright install chromium)

`build.py` fails on problems with a live card (missing text or prompts, undefined
footnotes, missing images, duplicate titles, unknown card type) and warns about
smaller ones, including stubs, missing images, and cards whose text overflows the
printed card. Pushes to `main` build and deploy to GitHub Pages
(see [`.github/workflows/build.yml`](.github/workflows/build.yml)).

## Layout

| Path         | What it is                                             |
|--------------|--------------------------------------------------------|
| `cards/`     | One YAML file per card. `live: true` cards are printed |
| `images/`    | Card images, referenced by `image.source`              |
| `assets/`    | The canvas used in the final round                     |
| `templates/` | Page templates and the print stylesheet                |
| `build.py`   | Validation and build                                   |
| `tools/`     | Helpers, such as `commons_image.py` for finding images |

## What gets built

| Output                                      | What it |
|---------------------------------------------|---------|
| `index.html`                                | How to play                                                                       |
| `cards.html`, `the_cards.pdf`               | The cards, then a credits and sources section                                     |
| `facilitator.html`, `facilitator_guide.pdf` | Extra prompts and notes for the facilitator, from each card's `facilitator` block |

The card face only carries the picture, a short caption and the numbered footnote
markers (the numbers restart on every card). Image credits, sources and each card's
history are printed in the credits section instead, so a card's metadata can be as
long as it needs to be. `python build.py --drafts` lists cards whose `meta.status`
is still `draft`.

## Images

Card images are freely licensed pictures. Most of the newer ones come from
[Wikimedia Commons](https://commons.wikimedia.org), and each card's `image` block
carries the author, licence and a link to the source page, which the licences
(CC BY, CC BY-SA) require. To add one:

    python tools/commons_image.py search "wildlife overpass" --preview some-folder
    python tools/commons_image.py use "File:Example.jpg" "Card name" --caption "What it shows"

The tool refuses files that aren't CC BY, CC BY-SA, CC0 or public domain.
