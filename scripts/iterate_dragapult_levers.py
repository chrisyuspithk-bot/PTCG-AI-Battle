#!/usr/bin/env python3
"""
Dragapult lever iteration: Test increased weights for boss_orders + gust_setup.

Baseline (session 2026-06-25):
  dragapult_ex_sample: 20.0% WR (10 games)

Hypothesis: boss_orders=700 and gust_setup_pokemon=600 insufficient vs Psychic speed.
Iteration plan:
  1. Increase boss_orders: 700 → 900 (more disruption priority)
  2. Increase gust_setup_pokemon: 600 → 800 (earlier bench targeting)
  3. Keep others stable
  4. Re-gate vs dragapult_ex_sample only (10 games, same config)
  5. Target: >25% WR (+5pp improvement minimum)

Run: python scripts/iterate_dragapult_levers.py
"""

import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, replace

# Prevent cg import errors in sandbox
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Import test utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.matchup_levers import LeverDeltas, detect_archetypes
from scripts.gate_lucario_rules import gate_vs_opponent_deck


@dataclass(frozen=True)
class LeverIteration:
    """Track a single iteration variant."""
    name: str
    boss_orders: float
    gust_setup_pokemon: float

    def apply_to_levers(self, base_deltas: LeverDeltas) -> LeverDeltas:
        """Apply iteration deltas to a LeverDeltas."""
        return replace(
            base_deltas,
            boss_orders=self.boss_orders,
            gust_setup_pokemon=self.gust_setup_pokemon,
        )


def get_baseline_levers() -> LeverDeltas:
    """Current dragapult lever config."""
    return LeverDeltas(
        solrock_vs_single_prize=150.0,
        boss_orders=700.0,
        gust_setup_pokemon=600.0,
        switch_after_mega_brave=300.0,
    )


def run_iteration(iteration: LeverIteration, num_games: int = 10) -> dict:
    """Test a single iteration variant."""
    print(f"\n{'='*70}")
    print(f"ITERATION: {iteration.name}")
    print(f"  boss_orders: {iteration.boss_orders}")
    print(f"  gust_setup_pokemon: {iteration.gust_setup_pokemon}")
    print(f"{'='*70}")

    # Load dragapult deck
    dragapult_path = Path("agent_decks/dragapult_ex_sample.csv")
    if not dragapult_path.exists():
        print(f"ERROR: {dragapult_path} not found")
        return {"iteration": iteration.name, "error": "deck_not_found"}

    # Create modified LeverDeltas
    modified = get_baseline_levers()
    modified = replace(
        modified,
        boss_orders=iteration.boss_orders,
        gust_setup_pokemon=iteration.gust_setup_pokemon,
    )

    # Gate vs dragapult (the weakest matchup)
    print(f"  Gating vs dragapult_ex_sample ({num_games} games, seat-swapped)...")
    try:
        results = gate_vs_opponent_deck(
            opponent_deck_path=str(dragapult_path),
            player_levers=modified,  # Pass modified levers
            num_games=num_games,
            verbose=False,
        )

        wr = results.get("win_rate", 0.0)
        ci_low = results.get("ci_low", 0.0)
        ci_high = results.get("ci_high", 0.0)

        improvement = wr - 0.20  # Baseline is 20%

        result = {
            "iteration": iteration.name,
            "wr": wr,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "improvement_pp": improvement * 100,
            "target_met": wr > 0.25,
        }

        print(f"  ✓ Result: {wr*100:.1f}% WR ({ci_low*100:.1f}%–{ci_high*100:.1f}%)")
        print(f"    Improvement: {improvement*100:+.1f}pp vs baseline (20.0%)")
        print(f"    Target (>25%): {'✅ MET' if wr > 0.25 else '❌ MISSED'}")

        return result
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return {"iteration": iteration.name, "error": str(e)}


def main():
    """Run lever iterations."""
    print("\n" + "="*70)
    print("DRAGAPULT LEVER ITERATION")
    print("="*70)

    baseline = get_baseline_levers()
    print(f"\nBASELINE (session 2026-06-25):")
    print(f"  dragapult_ex_sample: 20.0% WR")
    print(f"  Current levers: boss_orders={baseline.boss_orders}, gust_setup_pokemon={baseline.gust_setup_pokemon}")

    # Test 3 variants
    iterations = [
        LeverIteration(
            name="v1: +200 boss_orders, +200 gust",
            boss_orders=900.0,
            gust_setup_pokemon=800.0,
        ),
        LeverIteration(
            name="v2: +200 boss_orders only",
            boss_orders=900.0,
            gust_setup_pokemon=600.0,
        ),
        LeverIteration(
            name="v3: +200 gust only",
            boss_orders=700.0,
            gust_setup_pokemon=800.0,
        ),
    ]

    results_log = []
    winners = []

    for iteration in iterations:
        result = run_iteration(iteration, num_games=10)
        results_log.append(result)

        if result.get("target_met"):
            winners.append((iteration, result))

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"\nIterations tested: {len(iterations)}")
    print(f"Winners (>25% WR): {len(winners)}")

    for it, res in winners:
        print(f"\n  ✅ {it.name}")
        print(f"     WR: {res['wr']*100:.1f}% ({res['ci_low']*100:.1f}%–{res['ci_high']*100:.1f}%)")
        print(f"     Improvement: {res['improvement_pp']:+.1f}pp")

    # Save results
    out_file = Path("eval/dragapult_lever_iteration_20260626.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump({
            "baseline_wr": 0.20,
            "iterations_tested": len(iterations),
            "target_threshold": 0.25,
            "results": results_log,
            "winners": [
                {
                    "name": it.name,
                    "boss_orders": it.boss_orders,
                    "gust_setup_pokemon": it.gust_setup_pokemon,
                    **res,
                }
                for it, res in winners
            ],
        }, f, indent=2)

    print(f"\nResults saved to {out_file}")

    return 0 if winners else 1


if __name__ == "__main__":
    sys.exit(main())
