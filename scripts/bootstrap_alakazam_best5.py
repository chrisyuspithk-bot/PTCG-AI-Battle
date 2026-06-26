#!/usr/bin/env python3
"""Bootstrap agent/alakazam_agent.py + deck from ryotasueyoshi best5 notebook."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "ryotasueyoshi_rule_based_alakazam_best5" / "rule-based-not-psychic-alakazam-best-5th.ipynb"
DECK_OUT = ROOT / "agent_decks" / "ryotasueyoshi_alakazam_best5.csv"
AGENT_OUT = ROOT / "agent" / "alakazam_agent.py"

WRAPPER_HEAD = '''"""Alakazam best5 (ryotasueyoshi) — community rule pilot (never-crash wrapper).

Not a kiyotah organizer sample. Deck: env ALAKAZAM_DECK, deck.csv in cwd, or repo default.
Built by scripts/bootstrap_alakazam_best5.py — re-run after notebook updates.
"""

'''

WRAPPER_TAIL = '''

def _resolve_deck_path() -> str:
    env = os.environ.get("ALAKAZAM_DECK")
    if env and os.path.exists(env):
        return env
    if os.path.exists("deck.csv"):
        return "deck.csv"
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        here = None
    if here:
        packaged = os.path.join(here, "deck.csv")
        if os.path.exists(packaged):
            return packaged
        repo_default = os.path.join(here, "..", "agent_decks", "ryotasueyoshi_alakazam_best5.csv")
        if os.path.exists(repo_default):
            return repo_default
    return "/kaggle_simulations/agent/deck.csv"


with open(_resolve_deck_path(), "r", encoding="utf-8") as file:
    _csv = file.read().split("\\n")
my_deck = [int(_csv[i]) for i in range(60)]


def _legal_fallback(obs_dict: dict) -> list[int]:
    sel = obs_dict.get("select")
    if sel is None:
        return my_deck
    n = len(sel.get("option", []))
    min_c = int(sel.get("minCount") or 0)
    max_c = int(sel.get("maxCount") or 0)
    if n == 0 or max_c == 0:
        return []
    k = min_c if min_c > 0 else min(1, max_c)
    k = min(k, max_c, n)
    return list(range(k))


def _is_legal(out, obs_dict: dict) -> bool:
    sel = obs_dict.get("select")
    if sel is None:
        return isinstance(out, list) and len(out) == 60
    if not isinstance(out, list):
        return False
    n = len(sel.get("option", []))
    min_c = int(sel.get("minCount") or 0)
    max_c = int(sel.get("maxCount") or 0)
    if len(out) != len(set(out)):
        return False
    if not all(isinstance(i, int) and 0 <= i < n for i in out):
        return False
    return min_c <= len(out) <= max_c


def agent(obs_dict: dict) -> list[int]:
    try:
        out = _agent_impl(obs_dict)
        if not _is_legal(out, obs_dict):
            return _legal_fallback(obs_dict)
    except Exception:
        return _legal_fallback(obs_dict)
    return out
'''


def _cells(nb_path: Path) -> list[str]:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    return ["".join(c.get("source", [])) for c in nb.get("cells", []) if c.get("cell_type") == "code"]


def _extract_deck_csv(srcs: list[str]) -> list[int]:
    for src in srcs:
        if src.lstrip().startswith("%%writefile deck.csv"):
            lines = src.split("\n")[1:]
            ids = [int(x.strip()) for x in lines if x.strip()]
            if len(ids) != 60:
                raise ValueError(f"deck cell has {len(ids)} cards, expected 60")
            return ids
    raise ValueError("no %%writefile deck.csv cell")


def _extract_main_py(srcs: list[str]) -> str:
    for src in srcs:
        if src.lstrip().startswith("%%writefile main.py"):
            return src.split("\n", 1)[1] if "\n" in src else ""
    raise ValueError("no %%writefile main.py cell")


def _rename_impl(main_py: str) -> str:
    if re.search(r"^def agent\s*\(", main_py, flags=re.M):
        return re.sub(r"^def agent\s*\(", "def _agent_impl(", main_py, count=1, flags=re.M)
    raise ValueError("main.py has no def agent(...)")


def _strip_embedded_deck_load(main_py: str) -> str:
    pat = re.compile(
        r"# Load deck\.csv in the dataset\s*\n"
        r'file_path = "deck\.csv"\s*\n'
        r"if not os\.path\.exists\(file_path\):\s*\n"
        r'    file_path = "/kaggle_simulations/agent/" \+ file_path\s*\n'
        r'with open\(file_path, "r"\) as file:\s*\n'
        r'    csv = file\.read\(\)\.split\("\\n"\)\s*\n'
        r"my_deck = \[\]\s*\n"
        r"for i in range\(60\):\s*\n"
        r"    my_deck\.append\(int\(csv\[i\]\)\)\s*\n",
        re.MULTILINE,
    )
    stripped, n = pat.subn("", main_py, count=1)
    if n == 0:
        raise ValueError("could not strip embedded deck load from main.py")
    return stripped


def main() -> int:
    if not NB.is_file():
        print(f"Missing notebook: {NB}", file=sys.stderr)
        return 1
    srcs = _cells(NB)
    deck_ids = _extract_deck_csv(srcs)
    DECK_OUT.write_text("\n".join(str(x) for x in deck_ids) + "\n", encoding="utf-8")
    body = _strip_embedded_deck_load(_rename_impl(_extract_main_py(srcs)))
    AGENT_OUT.write_text(WRAPPER_HEAD + body + WRAPPER_TAIL, encoding="utf-8")
    print(f"OK   {DECK_OUT.relative_to(ROOT)} ({len(deck_ids)} cards)")
    print(f"OK   {AGENT_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
