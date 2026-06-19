"""Grid/mutation deck search scored by arena round-robin vs the meta pool."""

from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.arena import play_matchup, pool_decks  # noqa: E402
from scripts.validate_deck import load_card_pool, validate_deck  # noqa: E402

CHECKPOINT_DIR = ROOT / "report" / "deck_search"
VARIANT_DIR = ROOT / "agent_decks" / "search_variants"


def load_deck(path: Path) -> list[int]:
    return [int(x) for x in path.read_text().splitlines() if x.strip()]


def save_deck(deck: list[int], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(str(c) for c in deck) + "\n", encoding="utf-8")


def mutate_energy(deck: list[int], delta: int, energy_ids: set[int]) -> list[int]:
    counts: dict[int, int] = {}
    for cid in deck:
        counts[cid] = counts.get(cid, 0) + 1
    energies = [cid for cid in deck if cid in energy_ids]
    non_energy = [cid for cid in deck if cid not in energy_ids]
    if delta > 0 and energies:
        non_energy.pop()
        new = non_energy + energies + [energies[0]] * delta
    elif delta < 0 and len(energies) >= abs(delta):
        trim = energies[: abs(delta)]
        keep = energies[abs(delta) :]
        new = non_energy + keep
        _ = trim
    else:
        new = list(deck)
    new.sort(key=lambda c: (c in energy_ids, c))
    random.shuffle(new)
    return new[:60]


def score_deck(
    deck: list[int],
    opponents: dict[str, list[int]],
    games: int,
    scorer: str = "heuristic",
    deck_path: str | None = None,
) -> float:
    wins = 0
    total = 0
    path = deck_path or str(ROOT / "agent" / "deck.csv")
    for name, opp_deck in opponents.items():
        row = play_matchup(
            "candidate", deck, name, opp_deck, games, 6000, workers=1,
            scorer_a=scorer, deck_path_a=path,
        )
        wins += row["a_wins"]
        total += row["a_wins"] + row["b_wins"]
    return wins / max(1, total)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=str(ROOT / "agent" / "deck.csv"))
    parser.add_argument("--games", type=int, default=4)
    parser.add_argument("--energy-grid", default="-2,0,2")
    parser.add_argument(
        "--scorer",
        choices=("heuristic", "search"),
        default="heuristic",
        help="Scorer used when scoring vs the meta pool.",
    )
    parser.add_argument(
        "--bases",
        default="",
        help="Comma-separated base deck CSV paths (default: --base only).",
    )
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint = CHECKPOINT_DIR / "checkpoint.json"

    db = load_card_pool()
    energy_ids = {
        cid for cid, info in db.items() if info.is_basic_energy
    }
    opponents = pool_decks()
    base_paths = [Path(args.base)]
    if args.bases.strip():
        base_paths = [Path(p.strip()) for p in args.bases.split(",") if p.strip()]
        base_paths = [p if p.is_absolute() else ROOT / p for p in base_paths]

    deltas = [int(x) for x in args.energy_grid.split(",") if x.strip()]

    best_deck = load_deck(base_paths[0])
    best_score = -1.0
    best_label = ""
    if args.resume and checkpoint.exists():
        data = json.loads(checkpoint.read_text(encoding="utf-8"))
        best_score = float(data.get("best_score", -1))
        best_path = Path(data.get("best_path", ""))
        best_label = data.get("best_label", "")
        if best_path.exists():
            best_deck = load_deck(best_path)

    results = []
    for base_path in base_paths:
        if not base_path.exists():
            print(f"skip missing base: {base_path}")
            continue
        base_deck = load_deck(base_path)
        base_stem = base_path.stem
        for delta in deltas:
            candidate = mutate_energy(base_deck, delta, energy_ids)
            if len(candidate) != 60:
                continue
            errors, _warnings = validate_deck(candidate, db)
            if errors:
                continue
            label = f"{base_stem}_e{delta:+d}"
            path = VARIANT_DIR / f"{label}.csv"
            save_deck(candidate, path)
            score = score_deck(
                candidate, opponents, args.games,
                scorer=args.scorer, deck_path=str(path),
            )
            results.append({
                "label": label,
                "base": str(base_path),
                "delta": delta,
                "score": score,
                "path": str(path),
                "scorer": args.scorer,
            })
            if score > best_score:
                best_score = score
                best_deck = candidate
                best_label = label
                shutil.copy2(path, CHECKPOINT_DIR / "best_deck.csv")

    results.sort(key=lambda r: r["score"], reverse=True)
    checkpoint.write_text(
        json.dumps({
            "best_score": best_score,
            "best_path": str(CHECKPOINT_DIR / "best_deck.csv"),
            "best_label": best_label,
            "scorer": args.scorer,
            "results": results,
        }, indent=2),
        encoding="utf-8",
    )
    csv_path = CHECKPOINT_DIR / "grid_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["label", "base", "delta", "score", "path", "scorer"],
        )
        writer.writeheader()
        writer.writerows(results)
    print(f"best={best_label} score={best_score:.3f} scorer={args.scorer}; wrote {csv_path}")
    if len(results) >= 2:
        print(f"  #2 {results[1]['label']} score={results[1]['score']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
