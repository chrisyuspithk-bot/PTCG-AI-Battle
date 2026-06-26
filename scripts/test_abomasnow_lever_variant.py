#!/usr/bin/env python3
"""
Quick gate test for abomasnow_water lever variants.
Monkey-patch LUCARIO_LEVERS to test iteration values.

Usage:
  python scripts/test_abomasnow_lever_variant.py --variant v1 --games 10
  python scripts/test_abomasnow_lever_variant.py --all-variants --games 10
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


VARIANTS = {
    "v1": {
        "name": "+200 boss_orders, +200 gust",
        "boss_orders": 1200.0,
        "gust_setup_pokemon": 1000.0,
    },
    "v2": {
        "name": "+200 boss_orders only",
        "boss_orders": 1200.0,
        "gust_setup_pokemon": 800.0,
    },
    "v3": {
        "name": "+200 gust only",
        "boss_orders": 1000.0,
        "gust_setup_pokemon": 1000.0,
    },
    "baseline": {
        "name": "baseline (no change)",
        "boss_orders": 1000.0,
        "gust_setup_pokemon": 800.0,
    },
}

OPP_NAME = "real_mega_abomasnow_ex"


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
    wr = 100 * p
    lo = 100 * max(0.0, center - half)
    hi = 100 * min(100.0, center + half)
    return wr, lo, hi


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


def apply_variant(variant_key: str) -> None:
    """Monkey-patch LUCARIO_LEVERS abomasnow_water for this variant."""
    variant = VARIANTS.get(variant_key, {})
    if not variant:
        return

    base = matchup_levers.LUCARIO_LEVERS.get("abomasnow_water")
    if not base:
        return

    modified = replace(
        base,
        boss_orders=variant.get("boss_orders", base.boss_orders),
        gust_setup_pokemon=variant.get("gust_setup_pokemon", base.gust_setup_pokemon),
    )

    new_dict = dict(matchup_levers.LUCARIO_LEVERS)
    new_dict["abomasnow_water"] = modified
    matchup_levers.LUCARIO_LEVERS = new_dict


def test_variant(variant_key: str, num_games: int = 10, baseline_wr: float | None = None) -> dict:
    """Test a single variant vs real_mega_abomasnow_ex."""
    variant = VARIANTS.get(variant_key, {})
    if not variant:
        return {"error": f"Unknown variant: {variant_key}"}

    print(f"\n{'='*70}")
    print(f"VARIANT: {variant_key} — {variant['name']}")
    print(f"  boss_orders: {variant['boss_orders']}")
    print(f"  gust_setup_pokemon: {variant['gust_setup_pokemon']}")
    print(f"  opponent: {OPP_NAME}")
    print(f"{'='*70}")

    apply_variant(variant_key)

    opp_path = str(DECKS_DIR / f"{OPP_NAME}.csv")
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
        opp_name=OPP_NAME,
    )

    wins = losses = draws = unfinished = 0
    print(f"  Playing {num_games} games (seat-swapped)...")
    for i in range(num_games):
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
        if (i + 1) % max(1, num_games // 5) == 0:
            print(f"    {i+1}/{num_games}...")

    wr, lo, hi = _wilson(wins, wins + losses + draws)
    total = wins + losses + draws
    ref_wr = baseline_wr if baseline_wr is not None else wr
    improvement = wr - ref_wr

    result = {
        "variant": variant_key,
        "wr": wr / 100.0,
        "wr_pct": wr,
        "ci_low": lo / 100.0,
        "ci_high": hi / 100.0,
        "improvement_pp": improvement,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "unfinished": unfinished,
        "total": total,
        "target_met": improvement > 5.0 if baseline_wr is not None else wr > 35.0,
    }

    print(f"  Result: {wr:.1f}% WR (CI: {lo:.1f}–{hi:.1f}%)")
    print(f"    Record: {wins}W–{losses}L–{draws}D (unfinished={unfinished})")
    if baseline_wr is not None:
        print(f"    vs baseline ({baseline_wr:.1f}%): {improvement:+.1f}pp")
        print(f"    Target (>5pp): {'MET' if result['target_met'] else 'MISSED'}")

    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=str, default="v1", choices=list(VARIANTS.keys()))
    ap.add_argument("--games", type=int, default=10)
    ap.add_argument("--all-variants", action="store_true")
    args = ap.parse_args()

    results = []

    if args.all_variants:
        baseline_r = test_variant("baseline", args.games)
        baseline_wr = baseline_r.get("wr_pct", 0.0)
        results.append(baseline_r)
        for vk in ["v1", "v2", "v3"]:
            r = test_variant(vk, args.games, baseline_wr=baseline_wr)
            results.append(r)
    else:
        r = test_variant(args.variant, args.games)
        results.append(r)

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    baseline_wr = next((r["wr_pct"] for r in results if r.get("variant") == "baseline"), None)
    winners = [
        r for r in results
        if r.get("variant") != "baseline" and baseline_wr is not None
        and r.get("wr_pct", 0) - baseline_wr > 5.0
    ]

    print(f"\nVariants tested: {len(results)}")
    if baseline_wr is not None:
        print(f"Baseline WR: {baseline_wr:.1f}%")
        print(f"Winners (>5pp vs baseline): {len(winners)}")

    for r in results:
        if "error" in r:
            continue
        v = r["variant"]
        wr = r["wr_pct"]
        if baseline_wr is not None and v != "baseline":
            imp = wr - baseline_wr
            met = "OK" if imp > 5.0 else "--"
            print(f"  {met} {v:10s}: {wr:5.1f}% ({imp:+5.1f}pp vs baseline)")
        else:
            print(f"     {v:10s}: {wr:5.1f}%")

    if winners:
        best = max(winners, key=lambda x: x["wr_pct"])
        print(f"\nBest: {best['variant']} @ {best['wr_pct']:.1f}% (+{best['wr_pct'] - baseline_wr:.1f}pp)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
