"""Run Track A deck grid and package two ladder probe submissions.

Scores deck variants (multi-base energy grid) with SearchScorer vs the meta pool,
selects the top two distinct configs, builds dry-run validated tarballs, and
writes a probe manifest. NEVER submits to Kaggle.

Usage:
    python scripts/prepare_track_a_probes.py
    python scripts/prepare_track_a_probes.py --games 12 --dry-run-search
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TRACK_A_DIR = ROOT / "report" / "track_a"
PROBE_DECK_DIR = ROOT / "agent_decks" / "track_a_probes"

DEFAULT_BASES = (
    "agent/deck.csv,"
    "agent_decks/a2_kyogre_33_energy.csv,"
    "agent_decks/a2_big_basic_29_energy.csv,"
    "agent_decks/a4_basic_water_33_energy.csv"
)
ENERGY_GRID = "-4,-2,0,2,4"


def _deck_signature(path: Path) -> tuple[int, ...]:
    return tuple(sorted(int(x) for x in path.read_text().splitlines() if x.strip()))


def pick_top_two(results: list[dict]) -> list[dict]:
    """Return best overall plus best from a different base archetype."""
    ranked = sorted(results, key=lambda r: r["score"], reverse=True)
    chosen: list[dict] = []
    seen_sigs: set[tuple[int, ...]] = set()
    seen_bases: set[str] = set()

    def _add(row: dict) -> bool:
        path = Path(row["path"])
        if not path.exists():
            return False
        sig = _deck_signature(path)
        if sig in seen_sigs:
            return False
        seen_sigs.add(sig)
        chosen.append(row)
        base = Path(row.get("base", "")).stem
        if base:
            seen_bases.add(base)
        return True

    for row in ranked:
        if _add(row):
            break
    if not chosen:
        return []

    for row in ranked:
        base_stem = Path(row.get("base", "")).stem
        if base_stem and base_stem in seen_bases:
            continue
        if _add(row):
            break

    if len(chosen) < 2:
        for row in ranked:
            if row in chosen:
                continue
            if _add(row):
                break
    return chosen[:2]


def package_probe(name: str, deck_path: Path) -> Path:
    archive = ROOT / "dist" / "candidates" / f"{name}.tar.gz"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "package_submission.py"),
            "--name", name,
            "--deck", str(deck_path),
            "--scorer", "search",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    if not archive.exists():
        raise RuntimeError(f"missing archive after package: {archive}")
    return archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--games", type=int, default=12,
                        help="Games per pool matchup when scoring decks.")
    parser.add_argument("--bases", default=DEFAULT_BASES)
    parser.add_argument("--energy-grid", default=ENERGY_GRID)
    parser.add_argument("--dry-run-search", action="store_true",
                        help="Skip deck grid; use existing report/deck_search/grid_results.csv")
    args = parser.parse_args(argv)

    TRACK_A_DIR.mkdir(parents=True, exist_ok=True)
    PROBE_DECK_DIR.mkdir(parents=True, exist_ok=True)

    if not args.dry_run_search:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "deck_search.py"),
                "--games", str(args.games),
                "--scorer", "search",
                "--bases", args.bases,
                f"--energy-grid={args.energy_grid}",
            ],
            cwd=str(ROOT),
        )
        if proc.returncode != 0:
            return proc.returncode

    checkpoint = ROOT / "report" / "deck_search" / "checkpoint.json"
    if not checkpoint.exists():
        print("no deck search checkpoint; run deck_search first")
        return 1
    data = json.loads(checkpoint.read_text(encoding="utf-8"))
    results = data.get("results") or []
    if not results:
        print("empty deck search results")
        return 1

    top_two = pick_top_two(results)
    if len(top_two) < 2:
        print("need at least two distinct deck configs in grid results")
        return 1

    probes = []
    for i, row in enumerate(top_two, start=1):
        src = Path(row["path"])
        deck_copy = PROBE_DECK_DIR / f"probe_{i}_{row['label']}.csv"
        deck_copy.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        name = f"track_a_probe_{i}"
        archive = package_probe(name, deck_copy)
        probes.append({
            "slot": f"A{i}",
            "name": name,
            "archive": str(archive.relative_to(ROOT)).replace("\\", "/"),
            "deck": str(deck_copy.relative_to(ROOT)).replace("\\", "/"),
            "label": row["label"],
            "base": row.get("base", ""),
            "base_stem": Path(row.get("base", "")).stem,
            "energy_delta": row.get("delta"),
            "pool_win_rate": row["score"],
            "scorer": "SearchScorer",
            "purpose": (
                "Best Kyogre + SearchScorer (deck-tuned +2 energy)"
                if i == 1
                else "Second archetype: Abomasnow pilot + SearchScorer (+4 energy)"
                if "deck_e" in row["label"]
                else f"Alt base {Path(row.get('base', '')).stem} + SearchScorer"
            ),
        })

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "games_per_matchup": args.games,
        "scorer": "search",
        "probes": probes,
        "submit_commands": [
            (
                f"kaggle competitions submit -c pokemon-tcg-ai-battle "
                f"-f {ROOT / p['archive']} "
                f"-m \"Track A probe {p['slot']}: {p['label']} SearchScorer (user approval required)\""
            )
            for p in probes
        ],
    }
    manifest_path = TRACK_A_DIR / "ladder_probes.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    md_lines = [
        "# Track A ladder probes (two submissions)",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        f"Deck grid: SearchScorer vs meta pool @ {args.games} games/matchup.",
        f"Energy grid: `{args.energy_grid}` on bases: `{args.bases}`",
        "",
        "## Probe pair",
        "",
        "| Slot | Archive | Deck | Label | Pool win % | Agent | Purpose |",
        "|---|---|---|---|---:|---|---|",
    ]
    for p in probes:
        md_lines.append(
            f"| {p['slot']} | `{p['archive']}` | `{p['deck']}` | "
            f"{p['label']} | {100 * p['pool_win_rate']:.1f}% | SearchScorer | {p['purpose']} |"
        )
    md_lines.extend([
        "",
        "## Submit (DO NOT run without explicit user OK)",
        "",
    ])
    for cmd in manifest["submit_commands"]:
        md_lines.extend(["```", cmd, "```", ""])
    md_lines.extend([
        "After each submit:",
        "```",
        "python scripts/track_ladder.py --fetch-logs",
        "```",
        "",
        "Compare ladder μ after ~40 min matchmaking (600 = validation baseline only).",
    ])
    md_path = TRACK_A_DIR / "ladder_probes.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"wrote {manifest_path} and {md_path}")
    for p in probes:
        print(f"  {p['slot']} {p['archive']} — {p['label']} @ {100*p['pool_win_rate']:.1f}%")
    print("No Kaggle submission was attempted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
