"""Benchmark LearnedScorer on a deck spread and package each candidate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.arena import play_matchup, pool_decks  # noqa: E402

REPORT = ROOT / "report" / "track_b_deck_spread.md"
CANDIDATES = ROOT / "dist" / "candidates"

# Meta pool proxies (wmh ladder field) + local high-performer decks.
DECK_SPREAD = [
    ("bellibolt", "agent_decks/pool_bellibolt.csv", "meta"),
    ("crustle", "agent_decks/pool_crustle.csv", "meta"),
    ("alakazam", "agent_decks/pool_alakazam_dudunsparce.csv", "meta"),
    ("dragapult", "agent_decks/pool_dragapult.csv", "meta"),
    ("mega_greninja", "agent_decks/pool_mega_greninja.csv", "meta"),
    ("greninja", "agent_decks/pool_greninja.csv", "meta"),
    ("kyogre", "agent_decks/a2_kyogre_33_energy.csv", "high_performer"),
    ("big_basic", "agent_decks/a2_big_basic_29_energy.csv", "high_performer"),
    ("starmie", "agent_decks/a3_starmie_spread_33_energy.csv", "high_performer"),
]


def eval_learned(deck_path: Path, games: int) -> tuple[int, int]:
    deck = [int(x) for x in deck_path.read_text().splitlines() if x.strip()]
    opponents = pool_decks()
    wins = total = 0
    dp = str(deck_path.resolve())
    for _name, opp in opponents.items():
        row = play_matchup(
            "learned", deck, _name, opp, games, 6000,
            workers=1, scorer_a="learned", deck_path_a=dp,
        )
        wins += row["a_wins"]
        total += row["a_wins"] + row["b_wins"]
    return wins, total


def package_one(slug: str, deck_path: Path) -> str:
    name = f"track_b_learned_{slug}"
    proc = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "package_submission.py"),
            "--name", name, "--scorer", "learned", "--deck", str(deck_path),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return proc.stderr.strip() or "package failed"
    return proc.stdout.strip().splitlines()[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=12, help="Games per pool opponent")
    parser.add_argument("--skip-bench", action="store_true")
    parser.add_argument("--skip-package", action="store_true")
    args = parser.parse_args(argv)

    opponents = pool_decks()
    results: list[tuple[float, int, int, str, str, Path, str]] = []

    for slug, rel, group in DECK_SPREAD:
        deck_path = ROOT / rel
        if not deck_path.exists():
            print(f"skip {slug}: missing {deck_path}")
            continue
        if not args.skip_bench:
            wins, total = eval_learned(deck_path, args.games)
            rate = wins / max(1, total)
            print(f"{slug:14s} {wins:3d}/{total:3d} ({100 * rate:5.1f}%) [{group}]")
        else:
            wins, total, rate = 0, 0, 0.0

        pkg_note = ""
        if not args.skip_package:
            pkg_note = package_one(slug, deck_path)
            print(f"  packaged: {pkg_note}")

        if not args.skip_bench:
            results.append((rate, wins, total, slug, group, deck_path, pkg_note))

    if args.skip_bench:
        return 0

    results.sort(key=lambda r: r[0], reverse=True)
    lines = [
        "# Track B deck spread — LearnedScorer vs meta pool",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Games per opponent: {args.games} | Pool opponents: {len(opponents)}",
        "",
        "| Rank | Deck | Group | Wins | Rate | Source | Package |",
        "|-----:|------|-------|-----:|-----:|--------|---------|",
    ]
    for i, (rate, w, t, slug, group, deck_path, pkg) in enumerate(results, 1):
        pkg_name = f"`track_b_learned_{slug}.tar.gz`"
        lines.append(
            f"| {i} | `{slug}` | {group} | {w}/{t} | {100 * rate:.1f}% "
            f"| `{deck_path.relative_to(ROOT).as_posix()}` | {pkg_name} |"
        )
    lines += [
        "",
        "## Ladder probe order (diverse archetypes)",
        "",
        "Use up to 5 Simulation submits/day. Kyogre heuristic already live (#53854707).",
        "Probe one meta + one high-performer per day; fetch logs after each:",
        "",
        "```bash",
        "python scripts/track_ladder.py --fetch-logs",
        "```",
        "",
        "## Submit command (user approval required)",
        "",
        "```bash",
        "kaggle competitions submit -c pokemon-tcg-ai-battle \\",
        "  -f dist/candidates/track_b_learned_<slug>.tar.gz \\",
        '  -m "Track B LearnedScorer + <slug> deck probe"',
        "```",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
