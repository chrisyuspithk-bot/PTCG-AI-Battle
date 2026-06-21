"""Rank candidate decks against the robust gauntlet.

This is a deck-selection filter before expensive RL: evaluate known deck files
against benchmark + mined ladder decks, then report mean/CVaR/maximin.

Example:
    python scripts/evaluate_robust_deck_pool.py --games 2 --scorer search
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_DECKS = [
    "agent_decks/real_mega_lucario_ex.csv",
    "agent_decks/top_mined_alakazam.csv",
    "agent_decks/top_mined_trevenant.csv",
    "agent_decks/a2_kyogre_33_energy.csv",
    "agent_decks/a3_starmie_spread_33_energy.csv",
    "agent_decks/deck_rl/gen19_fast_basic.csv",
    "agent_decks/deck_rl/gen19_spread_control.csv",
    "report/robust_deck_rl/best_deck.csv",
    "report/robust_deck_rl/search_scorer_stable_20260620/best_deck.csv",
]


def _read_deck(path: Path) -> list[int]:
    return [int(x.strip()) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def _label(path: Path) -> str:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        rel = path
    parts = rel.parts
    if len(parts) >= 3 and parts[-1] == "best_deck.csv":
        return f"{parts[-2]}/best_deck"
    return path.stem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decks", default=",".join(DEFAULT_DECKS),
                        help="Comma-separated deck CSV paths")
    parser.add_argument("--games", type=int, default=2)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--scorer", default="search", choices=("heuristic", "search", "learned"))
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--cvar-q", type=float, default=0.3)
    parser.add_argument("--output", default="report/robust_deck_rl/pool_eval_20260620")
    args = parser.parse_args(argv)

    from rl.gauntlet import load_gauntlet, materialize_deck, winrate_vs
    from rl.robust_fitness import MatchupResult, summarize
    from scripts.validate_deck import load_card_pool, validate_deck

    out_base = _resolve(args.output)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    out_base.mkdir(parents=True, exist_ok=True)
    pool = load_card_pool()
    opponents = load_gauntlet()
    candidates = [_resolve(x.strip()) for x in args.decks.split(",") if x.strip()]

    summary_rows: list[dict[str, object]] = []
    detail_rows: list[dict[str, object]] = []
    for ci, path in enumerate(candidates):
        if not path.exists():
            print(f"skip missing {path}")
            continue
        deck = _read_deck(path)
        errors, _ = validate_deck(deck, pool)
        if errors:
            print(f"skip invalid {path}: {errors}")
            continue
        label = _label(path)
        deck_path = materialize_deck(deck, out_base / "_decks" / path.name)
        matchups: list[MatchupResult] = []
        for oi, opp in enumerate(opponents):
            rate, games_played = winrate_vs(
                deck,
                deck_path,
                opp,
                games=args.games,
                workers=args.workers,
                scorer=args.scorer,
                seed=1000 + ci * 100003 + oi * 7919,
            )
            matchups.append(MatchupResult(opp.name, rate, opp.weight, games_played))
            detail_rows.append({
                "deck": label,
                "deck_path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
                "opponent": opp.name,
                "opponent_source": opp.source,
                "opponent_weight": opp.weight,
                "win_rate": rate,
                "games": games_played,
            })
        sc = summarize(matchups, alpha=args.alpha, cvar_q=args.cvar_q)
        summary_rows.append({
            "deck": label,
            "deck_path": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
            "robust_score": sc["robust_score"],
            "mean": sc["mean"],
            "cvar": sc["cvar"],
            "maximin": sc["maximin"],
            "worst": sc["worst"],
            "n_opponents": sc["n_opponents"],
            "total_games": sc["total_games"],
        })
        print(
            f"{path.stem}: robust={sc['robust_score']:.3f} mean={sc['mean']:.3f} "
            f"cvar={sc['cvar']:.3f} maximin={sc['maximin']:.3f} worst={sc['worst']}"
        )

    summary_rows.sort(key=lambda r: float(r["robust_score"]), reverse=True)
    summary_csv = out_base / "summary.csv"
    details_csv = out_base / "details.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()) if summary_rows else [])
        if summary_rows:
            writer.writeheader()
            writer.writerows(summary_rows)
    with details_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(detail_rows[0].keys()) if detail_rows else [])
        if detail_rows:
            writer.writeheader()
            writer.writerows(detail_rows)

    lines = [
        "# Robust deck pool evaluation",
        "",
        f"Scorer: `{args.scorer}`",
        f"Games per matchup: {args.games}",
        f"Opponents: {len(opponents)}",
        "",
        "| Rank | Deck | Robust | Mean | CVaR | Maximin | Worst |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(summary_rows, 1):
        lines.append(
            f"| {idx} | `{row['deck']}` | {float(row['robust_score']):.3f} | "
            f"{float(row['mean']):.3f} | {float(row['cvar']):.3f} | "
            f"{float(row['maximin']):.3f} | `{row['worst']}` |"
        )
    lines += [
        "",
        "Low game counts are for triage only; re-run top decks at higher games before promotion.",
        f"CSV: `{summary_csv.relative_to(ROOT)}` and `{details_csv.relative_to(ROOT)}`",
    ]
    (out_base / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_base / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
