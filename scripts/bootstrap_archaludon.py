#!/usr/bin/env python3
"""Bootstrap agent/archaludon_agent.py from community public reference v5."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "notebooks" / "archaludon_ex_cinderace" / "archaludon_agent_public.py"
AGENT_OUT = ROOT / "agent" / "archaludon_agent.py"

WRAPPER_HEAD = '''"""Archaludon ex / Cinderace — community rule pilot + R7 bench guard.

Deck: env ARCHALUDON_DECK, deck.csv in cwd, or repo default.
Built by scripts/bootstrap_archaludon.py — re-run after reference updates.
"""

'''

WRAPPER_TAIL = '''

def _resolve_deck_path() -> str:
    env = os.environ.get("ARCHALUDON_DECK")
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
        repo_default = os.path.join(here, "..", "agent_decks", "archaludon_ex_cinderace.csv")
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


try:
    from agent.archaludon_bench_guard import apply_bench_guard
except ImportError:
    from archaludon_bench_guard import apply_bench_guard


def agent(obs_dict: dict) -> list[int]:
    try:
        raw = _agent_impl(obs_dict)
        bench_on = os.environ.get("ARCHALUDON_BENCH_GUARD", "1") != "0"
        out = apply_bench_guard(obs_dict, raw) if bench_on else raw
        if not _is_legal(out, obs_dict):
            return _legal_fallback(obs_dict)
    except Exception:
        return _legal_fallback(obs_dict)
    return out
'''


def main() -> int:
    if not SRC.is_file():
        print(f"Missing reference: {SRC}", file=sys.stderr)
        return 1
    body = SRC.read_text(encoding="utf-8")
    body = re.sub(
        r'^"""Archaludon ex \+ Cinderace.*?"""\n\n',
        "",
        body,
        count=1,
        flags=re.DOTALL,
    )
    body = re.sub(r"^def agent\s*\(", "def _agent_impl(", body, count=1, flags=re.M)

    # Deck select returns my_deck (set in wrapper).
    body = body.replace("return read_deck_csv()", "return my_deck")

    AGENT_OUT.write_text(WRAPPER_HEAD + body + WRAPPER_TAIL, encoding="utf-8")
    print(f"OK   {AGENT_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
