"""Deprecated: use rl/train_rl.py (Track B entry point)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(argv: list[str] | None = None) -> int:
    print("NOTE: rl/train_ppo.py is deprecated; use rl/train_rl.py or scripts/train_track_b_deck.py")
    from rl.train_rl import main as train_main

    return train_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
