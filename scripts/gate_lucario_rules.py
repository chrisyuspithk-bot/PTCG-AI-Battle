"""Phase-2 gate: LucarioScorer (rules only) vs field opponents.

Measures per-matchup win-rate for lever tuning (R11 phase 2). Rules baseline.
Seat-swapped games, Wilson 95% CI. Local filter only — not ladder truth.

  python scripts/gate_lucario_rules.py --games 10
  python scripts/gate_lucario_rules.py --games 20 --opponents dragapult_ex_sample real_mega_abomasnow_ex
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "data" / "sim" / "sample_submission"
DECKS_DIR = ROOT / "agent_decks"
LUCARIO_DECK = DECKS_DIR / "real_mega_lucario_ex.csv"

if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg import game  # noqa: E402
from cg.sim import Battle, lib  # noqa: E402

from agent.lucario_policy import LucarioScorer  # noqa: E402
from agent.native_opponent import make_opponent_brain, native_brain_label  # noqa: E402
from agent.official_registry import official_archetype_for_opponent  # noqa: E402

# Full field (official samples only).
DEFAULT_OPPONENTS = [
    "dragapult_ex_sample",
    "real_mega_abomasnow_ex",
    "real_iono",
    "real_dragapult_ex",
    "real_mega_lucario_ex",
]

_lucario_act = None
_opp_cache: dict[str, tuple[object, str]] = {}


def load_deck(path: Path) -> list[int]:
    return [int(x) for x in path.read_text().splitlines() if x.strip()][:60]


def _select_player() -> int:
    return lib.GetBattleData(Battle.battle_ptr).selectPlayer


def _wilson(wins: int, n: int) -> tuple[float, float, float]:
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.96
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return 100 * p, 100 * max(0.0, center - half), 100 * min(1.0, center + half)


def get_lucario_act():
    global _lucario_act
    if _lucario_act is None:
        from agent.agent import build_agent
        deck_path = str(LUCARIO_DECK)
        agent = build_agent(deck_path=deck_path, scorer=LucarioScorer(deck_path=deck_path))
        _lucario_act = agent.act
    return _lucario_act


def get_opponent_act(opp_name: str, opp_path: str, deck_o: list[int]) -> tuple[object, str]:
    key = f"{opp_name}:native"
    if key in _opp_cache:
        return _opp_cache[key]
    act, brain = make_opponent_brain(
        "native",
        opp_path,
        deck_o,
        opp_name=opp_name,
    )
    _opp_cache[key] = (act, brain)
    return act, brain


def run_game(deck0: list[int], deck1: list[int], pol0, pol1, max_steps: int = 8000) -> int:
    obs, start = game.battle_start(deck0, deck1)
    if obs is None:
        raise RuntimeError(f"battle_start failed: err={getattr(start, 'errorType', '?')}")
    policies = (pol0, pol1)
    try:
        for _ in range(max_steps):
            cur = obs["current"]
            if cur is not None and cur.get("result", -1) != -1:
                return cur["result"]
            if obs["select"] is None:
                return -1
            p = _select_player()
            obs = game.battle_select(policies[p](obs))
        return -1
    finally:
        game.battle_finish()


def gate_vs(opp_name: str, games: int) -> tuple[int, int, int, int, str] | None:
    """Return None if opponent has no official sample."""
    opp_path = str(DECKS_DIR / f"{opp_name}.csv")
    deck_o = load_deck(Path(opp_path))
    arch = official_archetype_for_opponent(opp_name, deck_o)
    if arch is None:
        return None

    deck_l = load_deck(LUCARIO_DECK)
    lucario = get_lucario_act()
    opp_move, brain = get_opponent_act(opp_name, opp_path, deck_o)

    wins = losses = draws = unfinished = 0
    for i in range(games):
        if i % 2 == 0:
            r = run_game(deck_l, deck_o, lucario, opp_move)
            if r == 0:
                wins += 1
            elif r == 1:
                losses += 1
            elif r == 2:
                draws += 1
            else:
                unfinished += 1
        else:
            r = run_game(deck_o, deck_l, opp_move, lucario)
            if r == 1:
                wins += 1
            elif r == 0:
                losses += 1
            elif r == 2:
                draws += 1
            else:
                unfinished += 1
    return wins, losses, draws, unfinished, brain


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--games", type=int, default=20)
    ap.add_argument("--opponents", nargs="*", default=DEFAULT_OPPONENTS)
    args = ap.parse_args()

    print(f"LucarioScorer (rules only) vs field ({args.games} games/opp)\n")

    total_w = total_n = 0
    gated = 0

    for name in args.opponents:
        opp_path = DECKS_DIR / f"{name}.csv"
        if not opp_path.exists():
            print(f"  SKIP {name:32}  (deck not found)")
            continue

        deck_o = load_deck(opp_path)
        label = native_brain_label(deck_o, name)

        try:
            result = gate_vs(name, args.games)
        except (FileNotFoundError, ModuleNotFoundError, ValueError) as exc:
            print(f"  FAIL {name:32}  {exc}")
            return 1

        if result is None:
            print(f"  SKIP {name:32}  (no official sample)")
            continue

        w, l, d, u, brain = result
        n = w + l
        pt, lo, hi = _wilson(w, n)
        total_w += w
        total_n += n
        gated += 1
        flag = " GAP" if pt < 30 else " OK" if pt >= 50 else ""
        print(
            f"  {name:32} ({brain:22})  {pt:5.1f}%  [{lo:4.1f}, {hi:5.1f}]  "
            f"W{w}/L{l}/D{d}/U{u}{flag}",
        )

    if gated == 0:
        print("\nNo opponents gated.")
        return 1

    if total_n:
        pt, lo, hi = _wilson(total_w, total_n)
        print(f"\n  {'OVERALL (gated)':32} {'':22}  {pt:5.1f}%  [{lo:4.1f}, {hi:5.1f}]  n={gated} decks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
