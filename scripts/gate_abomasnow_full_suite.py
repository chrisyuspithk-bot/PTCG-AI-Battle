#!/usr/bin/env python3
"""
Full suite gate after abomasnow_water lever iteration (Session 45).
Applies winning abomasnow variant; tests vs 3-opponent field.

Run:
  python scripts/gate_abomasnow_full_suite.py
  python scripts/gate_abomasnow_full_suite.py --variant v1
"""

import argparse
import math
import sys
from dataclasses import replace
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
from agent.native_opponent import make_opponent_brain  # noqa: E402
from agent import matchup_levers  # noqa: E402


OPPONENTS = [
    "dragapult_ex_sample",
    "real_mega_abomasnow_ex",
    "real_iono",
]

# Post-dragapult-R2 full suite (session 44j)
POST_R2_BASELINES = {
    "dragapult_ex_sample": 30.0,
    "real_mega_abomasnow_ex": 50.0,
    "real_iono": 50.0,
}
POST_R2_OVERALL = 43.3

ABOMASNOW_VARIANTS = {
    "baseline": {"boss_orders": 1000.0, "gust_setup_pokemon": 800.0},
    "v1": {"boss_orders": 1200.0, "gust_setup_pokemon": 1000.0},
    "v2": {"boss_orders": 1200.0, "gust_setup_pokemon": 800.0},
    "v3": {"boss_orders": 1000.0, "gust_setup_pokemon": 1000.0},
}


def apply_abomasnow_variant(variant_key: str) -> None:
    variant = ABOMASNOW_VARIANTS.get(variant_key)
    if not variant:
        raise ValueError(f"Unknown variant: {variant_key}")
    base = matchup_levers.LUCARIO_LEVERS.get("abomasnow_water")
    if not base:
        raise RuntimeError("abomasnow_water levers not found")
    modified = replace(
        base,
        boss_orders=variant["boss_orders"],
        gust_setup_pokemon=variant["gust_setup_pokemon"],
    )
    new_dict = dict(matchup_levers.LUCARIO_LEVERS)
    new_dict["abomasnow_water"] = modified
    matchup_levers.LUCARIO_LEVERS = new_dict


def load_deck(path: Path) -> list[int]:
    return [int(x) for x in path.read_text().splitlines() if x.strip()][:60]


def _select_player() -> int:
    return lib.GetBattleData(Battle.battle_ptr).selectPlayer


def _wilson(wins: int, n: int) -> tuple[float, tuple[float, float]]:
    if n == 0:
        return 0.0, (0.0, 0.0)
    z = 1.96
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    wr = 100 * p
    lo = 100 * max(0.0, center - half)
    hi = 100 * min(100.0, center + half)
    return wr, (lo, hi)


def run_game(deck0: list[int], deck1: list[int], pol0, pol1, max_steps: int = 8000) -> int:
    obs, start = game.battle_start(deck0, deck1)
    if obs is None:
        raise RuntimeError("battle_start failed")
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


def gate_vs(opp_name: str, games: int = 10) -> dict:
    opp_path = str(DECKS_DIR / f"{opp_name}.csv")
    deck_o = load_deck(Path(opp_path))
    deck_l = load_deck(LUCARIO_DECK)
    lucario = LucarioScorer(deck_path=str(LUCARIO_DECK))

    from agent.agent import build_agent

    def lucario_act(obs):
        return build_agent(deck_path=str(LUCARIO_DECK), scorer=lucario).act(obs)

    opp_move, _brain = make_opponent_brain(
        "native",
        opp_path,
        deck_o,
        opp_name=opp_name,
    )

    wins = losses = draws = unfinished = 0
    for i in range(games):
        if i % 2 == 0:
            r = run_game(deck_l, deck_o, lucario_act, opp_move)
            if r == 0:
                wins += 1
            elif r == 1:
                losses += 1
            elif r == 2:
                draws += 1
            else:
                unfinished += 1
        else:
            r = run_game(deck_o, deck_l, opp_move, lucario_act)
            if r == 1:
                wins += 1
            elif r == 0:
                losses += 1
            elif r == 2:
                draws += 1
            else:
                unfinished += 1
        if (i + 1) % max(1, games // 4) == 0:
            print(f"    {i+1}/{games}...")

    wr, ci = _wilson(wins, wins + losses + draws)
    return {
        "opponent": opp_name,
        "wr": wr,
        "ci": ci,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "unfinished": unfinished,
        "total": wins + losses + draws,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", default="baseline", choices=list(ABOMASNOW_VARIANTS.keys()))
    ap.add_argument("--games", type=int, default=10)
    args = ap.parse_args()

    apply_abomasnow_variant(args.variant)
    v = ABOMASNOW_VARIANTS[args.variant]

    print("\n" + "=" * 70)
    print("FULL SUITE GATE — Abomasnow R2 Lever Iteration (Session 45)")
    print("=" * 70)
    print(f"\nVariant: {args.variant} (boss_orders={v['boss_orders']}, gust={v['gust_setup_pokemon']})")
    print("Opponents: dragapult_ex_sample, real_mega_abomasnow_ex, real_iono")
    print(f"Games per opponent: {args.games} (seat-swapped)")
    print(f"Regression baselines (post-dragapult-R2): {POST_R2_BASELINES}")

    results = []
    for opp_name in OPPONENTS:
        print(f"\n  Testing vs {opp_name}...")
        try:
            result = gate_vs(opp_name, games=args.games)
            results.append(result)
            wr = result["wr"]
            lo, hi = result["ci"]
            baseline_wr = POST_R2_BASELINES.get(opp_name, 0)
            delta = wr - baseline_wr
            print(f"    {wr:.1f}% WR (CI: {lo:.1f}–{hi:.1f}%)")
            print(f"      Record: {result['wins']}W–{result['losses']}L–{result['draws']}D")
            print(f"      vs post-R2 baseline ({baseline_wr:.1f}%): {delta:+.1f}pp")
        except Exception as e:
            print(f"    Error: {e}")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")

    if not results:
        return 1

    overall_wins = sum(r["wins"] for r in results)
    overall_total = sum(r["total"] for r in results)
    overall_wr, overall_ci = _wilson(overall_wins, overall_total)
    delta_overall = overall_wr - POST_R2_OVERALL

    regressions = 0
    for r in results:
        baseline_wr = POST_R2_BASELINES.get(r["opponent"], 0)
        delta = r["wr"] - baseline_wr
        status = "OK" if delta >= -5.0 else "REGRESS"
        if delta < -5.0:
            regressions += 1
        print(f"  {status} {r['opponent']:30s}: {r['wr']:5.1f}% ({delta:+5.1f}pp vs {baseline_wr:.1f}%)")

    print(f"\nOverall: {overall_wr:.1f}% WR (CI: {overall_ci[0]:.1f}–{overall_ci[1]:.1f}%)")
    print(f"vs post-R2 overall ({POST_R2_OVERALL}%): {delta_overall:+.1f}pp")
    print(f"Material regressions (>5pp): {regressions}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
