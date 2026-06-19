"""Track B gate: LearnedScorer vs SearchScorer vs meta pool (SPRT + packaging)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.arena import play_matchup, pool_decks  # noqa: E402
from scripts.stats_utils import sprt_test  # noqa: E402

REPORT = ROOT / "report" / "track_b_gate.md"
DEFAULT_MODEL = ROOT / "agent" / "models" / "distilled_v1.npz"


def eval_learned(
    deck: list[int],
    opponents: dict[str, list[int]],
    games: int,
    deck_path: str,
    model_path: Path,
) -> tuple[int, int]:
    wins = losses = 0
    for name, opp_deck in opponents.items():
        row = play_matchup(
            "learned", deck, name, opp_deck, games, 6000,
            workers=1, scorer_a="learned", deck_path_a=deck_path,
            model_path_a=str(model_path),
        )
        wins += row["a_wins"]
        losses += row["b_wins"]
    return wins, wins + losses


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=8)
    parser.add_argument("--deck", default=str(ROOT / "agent" / "deck.csv"))
    parser.add_argument("--model", default=str(DEFAULT_MODEL), help="Distilled npz for LearnedScorer")
    parser.add_argument("--name", default="track_b_learned", help="Package basename if gate passes")
    parser.add_argument("--no-package", action="store_true")
    args = parser.parse_args(argv)

    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = ROOT / model_path
    if not model_path.exists():
        print(f"missing distilled model: {model_path}; run scripts/distill_policy.py first")
        return 1

    deck_path = Path(args.deck)
    if not deck_path.is_absolute():
        deck_path = ROOT / deck_path
    deck = [int(x) for x in deck_path.read_text().splitlines() if x.strip()]
    deck_path_str = str(deck_path.resolve())
    opponents = pool_decks()
    l_wins, l_total = eval_learned(deck, opponents, args.games, deck_path_str, model_path)

    from scripts.gate_track_a import eval_scorer

    s_wins, s_total = eval_scorer("search", deck, opponents, args.games, deck_path_str)
    sprt = sprt_test(l_wins, l_total)
    passed = l_wins >= s_wins or sprt.decision == "accept_b"

    report_path = REPORT
    if args.name != "track_b_learned":
        report_path = ROOT / "report" / "track_b_gates" / f"{args.name}_gate.md"

    package_note = ""
    if passed and not args.no_package:
        proc = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "package_submission.py"),
                "--name", args.name, "--scorer", "learned",
                "--deck", deck_path_str, "--model", str(model_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        package_note = proc.stdout.strip() or proc.stderr.strip()

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "\n".join([
            "# Track B gate report",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            f"- Deck: `{deck_path}`",
            f"- Model: `{model_path}`",
            f"- Learned wins vs pool: {l_wins}/{l_total}",
            f"- Search baseline: {s_wins}/{s_total}",
            f"- SPRT: {sprt.decision}",
            f"- Gate passed: **{passed}**",
            "",
            package_note,
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}; gate passed={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
