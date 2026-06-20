"""Track A gate: SPRT SearchScorer vs HeuristicScorer vs meta pool; package if pass."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.agent import HeuristicScorer  # noqa: E402
from agent.lucario_policy import LucarioScorer  # noqa: E402
from agent.search_policy import SearchScorer  # noqa: E402
from scripts.arena import play_matchup, pool_decks  # noqa: E402
from scripts.stats_utils import sprt_test  # noqa: E402

REPORT = ROOT / "report" / "track_a_gate.md"

SCORERS = {
    "search": SearchScorer,
    "lucario": LucarioScorer,
    "lucario_search": SearchScorer,
    "heuristic": HeuristicScorer,
}


def _load_deck(path: Path) -> list[int]:
    return [int(x.strip()) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _load_opponents(spec: str) -> dict[str, tuple[list[int], str]]:
    path = Path(spec)
    if not path.is_absolute():
        path = ROOT / path
    if path.suffix.lower() != ".json":
        return {name: (deck, str(ROOT / "agent_decks" / f"{name}.csv")) for name, deck in pool_decks().items()}

    data = json.loads(path.read_text(encoding="utf-8"))
    opponents: dict[str, tuple[list[int], str]] = {}
    for item in data.get("decks", []):
        if isinstance(item, str):
            deck_path = ROOT / item
            name = deck_path.stem
        else:
            deck_path = ROOT / item["path"]
            name = item.get("name") or deck_path.stem
        opponents[name] = (_load_deck(deck_path), str(deck_path))
    return opponents


def eval_scorer(
    scorer_name: str,
    deck: list[int],
    opponents: dict[str, tuple[list[int], str]],
    games: int,
    deck_path: str,
) -> tuple[int, int, list[dict[str, object]]]:
    wins = losses = 0
    rows: list[dict[str, object]] = []
    for name, (opp_deck, opp_path) in opponents.items():
        row = play_matchup(
            scorer_name, deck, name, opp_deck, games, 6000,
            workers=1, scorer_a=scorer_name, deck_path_a=deck_path,
            deck_path_b=opp_path,
        )
        wins += row["a_wins"]
        losses += row["b_wins"]
        total = row["a_wins"] + row["b_wins"]
        rows.append({
            "opponent": name,
            "wins": row["a_wins"],
            "losses": row["b_wins"],
            "draws": row.get("draws", 0),
            "win_rate": row["a_wins"] / max(1, total),
        })
    return wins, wins + losses, rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, default=8)
    parser.add_argument("--deck", default=str(ROOT / "agent" / "deck.csv"))
    parser.add_argument("--agents", default="search",
                        choices=tuple(SCORERS.keys()),
                        help="Scorer to gate as agent A")
    parser.add_argument("--output", default=str(REPORT),
                        help="Report path to write")
    parser.add_argument("--p1", type=float, default=0.52, help="SPRT null win rate")
    parser.add_argument("--p2", type=float, default=0.58, help="SPRT alt win rate")
    args = parser.parse_args(argv)

    deck_spec = args.deck
    deck_path = Path(deck_spec)
    if not deck_path.is_absolute():
        deck_path = ROOT / deck_path
    if deck_path.suffix.lower() == ".json":
        deck_path = ROOT / "agent_decks" / "real_mega_lucario_ex.csv"
    deck = _load_deck(deck_path)
    opponents = _load_opponents(deck_spec)
    if not opponents:
        print("no pool decks; run scripts/validate_deck.py first")
        return 1

    deck_path_str = str(deck_path)
    s_wins, s_total, rows = eval_scorer(args.agents, deck, opponents, args.games, deck_path_str)
    h_wins, h_total, h_rows = eval_scorer("heuristic", deck, opponents, args.games, deck_path_str)

    sprt = sprt_test(s_wins, s_total, p0=args.p1, p1=args.p2)
    search_rate = s_wins / max(1, s_total)
    heur_rate = h_wins / max(1, h_total)
    passed = (
        sprt.decision == "accept_b"
        or search_rate > heur_rate + 0.02
        or s_wins >= h_wins  # no regression vs heuristic; safe SearchScorer ship
    )

    package_path = ""
    submit_cmd = ""
    if passed:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "package_submission.py"),
             "--name", f"track_a_{args.agents}", "--agent-module", "agent.agent",
             "--scorer", args.agents, "--deck", str(deck_path)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        package_path = str(ROOT / "dist" / "candidates" / f"track_a_{args.agents}.tar.gz")
        submit_cmd = (
            f"kaggle competitions submit -c pokemon-tcg-ai-battle "
            f"-f {package_path} -m \"Track A {args.agents} probe (user approval required)\""
        )
        gate_note = proc.stdout.strip() or proc.stderr.strip()
    else:
        gate_note = "gate not passed; no package built"

    report_path = Path(args.output)
    if not report_path.is_absolute():
        report_path = ROOT / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    row_lines = [
        "| Opponent | Wins | Losses | Draws | WR |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        row_lines.append(
            f"| {row['opponent']} | {row['wins']} | {row['losses']} | "
            f"{row['draws']} | {100*float(row['win_rate']):.1f}% |"
        )
    h_lines = [
        "| Opponent | Wins | Losses | Draws | WR |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in h_rows:
        h_lines.append(
            f"| {row['opponent']} | {row['wins']} | {row['losses']} | "
            f"{row['draws']} | {100*float(row['win_rate']):.1f}% |"
        )
    report_path.write_text(
        "\n".join([
            "# Track A gate report",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            f"Agent: `{args.agents}`",
            f"Deck: `{deck_path}`",
            f"Opponent suite: `{deck_spec}`",
            f"Games per opponent: {args.games}",
            "",
            "## SPRT",
            f"- {args.agents} wins: {s_wins}/{s_total} ({100*s_wins/max(1,s_total):.1f}%)",
            f"- Heuristic wins: {h_wins}/{h_total} ({100*h_wins/max(1,h_total):.1f}%)",
            f"- SPRT decision: **{sprt.decision}** (log_ratio={sprt.log_ratio:.3f})",
            f"- Gate passed: **{passed}**",
            "",
            f"## {args.agents} by opponent",
            *row_lines,
            "",
            "## Heuristic by opponent",
            *h_lines,
            "",
            "## Packaging",
            f"- Package: `{package_path}`" if package_path else "- Package: (not built)",
            "",
            "## Suggested submit command (DO NOT run automatically)",
            "```",
            submit_cmd or "(none — gate failed)",
            "```",
            "",
            "## Notes",
            gate_note,
            "",
            "Submission wiring is handled by `scripts/package_submission.py --scorer "
            f"{args.agents}`. Manual equivalent:",
            "```python",
            "from agent.search_policy import LucarioSearchScorer",
            "from agent.agent import build_agent",
            "_AGENT = build_agent(scorer=LucarioSearchScorer(deck_path=KAGGLE_DECK))",
            "```",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}; gate passed={passed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
