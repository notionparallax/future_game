"""Read and write card YAML files in the repo's house style."""
import re
from pathlib import Path

import yaml

CARDS = Path(__file__).resolve().parent.parent / "cards"
ORDER = ["title", "live", "card_type", "image", "body", "lens", "consider", "footnotes", "meta"]


class _Dumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def path_for(name):
    return CARDS / f"{name}.yaml"


def load(name):
    return yaml.safe_load(path_for(name).read_text(encoding="utf8"))


def dump(name, card):
    unknown = set(card) - set(ORDER)
    assert not unknown, f"unknown card fields: {unknown}"
    ordered = {k: card[k] for k in ORDER if k in card}
    text = yaml.dump(ordered, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=90, indent=4)
    path_for(name).write_text(text, encoding="utf8", newline="\n")
