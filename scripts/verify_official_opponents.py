"""Smoke-check: every default field deck loads its official Kaggle rule pilot.

Run before field RL+MCTS training:

  python scripts/verify_official_opponents.py

Exit 0 when all official decks resolve; exit 1 on missing CSV, archetype, or import failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.cg_bootstrap import ensure_cg_engine  # noqa: E402
from agent.official_registry import (  # noqa: E402
    KERNEL_URLS,
    OFFICIAL_FIELD_DECK_STEMS,
    OFFICIAL_PILOT_MODULES,
    RANDOM_ONLY_DECK_STEMS,
    make_official_opponent,
    official_archetype_for_opponent,
)


def load_deck(path: Path) -> list[int]:
    ids = [int(line.strip()) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(ids) != 60:
        raise ValueError(f"{path.name}: {len(ids)} cards, expected 60")
    return ids


def main() -> int:
    ensure_cg_engine()
    decks_dir = ROOT / "agent_decks"
    ok = True
    print(f"Official field decks ({len(OFFICIAL_FIELD_DECK_STEMS)}) — one Kaggle rule pilot each:\n")
    for stem in OFFICIAL_FIELD_DECK_STEMS:
        csv_path = decks_dir / f"{stem}.csv"
        if not csv_path.is_file():
            print(f"  FAIL  {stem:32} missing {csv_path}")
            ok = False
            continue
        deck_ids = load_deck(csv_path)
        arch = official_archetype_for_opponent(stem, deck_ids)
        module = OFFICIAL_PILOT_MODULES.get(arch or "", "?")
        try:
            act, label = make_official_opponent(str(csv_path), deck_ids, opp_name=stem)
            if not callable(act):
                raise TypeError("act is not callable")
            print(f"  OK    {stem:32} {label:20} -> {module}")
            url = KERNEL_URLS.get(label or "", "")
            if url:
                print(f"         kernel: {url}")
        except Exception as exc:
            print(f"  FAIL  {stem:32} {arch or 'none':20} -> {exc}")
            ok = False

    print(f"\nExcluded by default (no official sample; use --include-random-opponents):")
    for stem in RANDOM_ONLY_DECK_STEMS:
        csv_path = decks_dir / f"{stem}.csv"
        present = "present" if csv_path.is_file() else "MISSING csv"
        print(f"  skip  {stem:32} random pilot only ({present})")

    if not ok:
        print("\nFix: powershell -File scripts/fetch_official_rule_samples.ps1")
        print("     python scripts/bootstrap_official_rule_agents.py")
        return 1
    print("\nAll official opponents ready for --opponent-brain native training.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
