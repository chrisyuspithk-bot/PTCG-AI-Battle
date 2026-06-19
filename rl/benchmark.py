"""Benchmark suite for deck fitness and RL league training.

Uses meta pool decks as championship-field proxies until real Worlds lists are
added under agent_decks/benchmark/.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / "agent_decks" / "benchmark" / "suite.json"


@dataclass(frozen=True)
class BenchmarkDeck:
    name: str
    path: Path
    tag: str
    weight: float

    def load(self) -> list[int]:
        return [int(x) for x in self.path.read_text().splitlines() if x.strip()]


def load_suite(path: Path | None = None) -> list[BenchmarkDeck]:
    path = path or SUITE_PATH
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[BenchmarkDeck] = []
    for row in data.get("decks", []):
        p = ROOT / row["path"]
        if not p.exists():
            continue
        out.append(
            BenchmarkDeck(
                name=row["name"],
                path=p,
                tag=row.get("tag", "meta"),
                weight=float(row.get("weight", 1.0)),
            )
        )
    if not out:
        raise FileNotFoundError(f"no benchmark decks found via {path}")
    return out


def evaluate_deck_vs_benchmark(
    deck: list[int],
    *,
    games_per_opponent: int = 8,
    workers: int = 4,
    scorer: str | None = None,
    deck_path: str | None = None,
    seed: int = 42,
) -> dict:
    """Weighted win rate vs the full benchmark suite."""
    import sys

    sys.path.insert(0, str(ROOT))
    from scripts.arena import play_matchup

    suite = load_suite()
    total_w = 0.0
    weighted_wins = 0.0
    weighted_games = 0.0
    per_opponent: dict[str, dict] = {}

    path = deck_path or str(ROOT / "agent" / "deck.csv")
    for opp in suite:
        row = play_matchup(
            "candidate",
            deck,
            opp.name,
            opp.load(),
            games_per_opponent,
            6000,
            workers=workers,
            scorer_a=scorer,
            deck_path_a=path,
            seed=seed,
        )
        wins = row["a_wins"]
        total = row["a_wins"] + row["b_wins"]
        rate = wins / max(1, total)
        per_opponent[opp.name] = {"wins": wins, "total": total, "rate": rate, "tag": opp.tag}
        weighted_wins += opp.weight * wins
        weighted_games += opp.weight * total
        total_w += opp.weight

    fitness = weighted_wins / max(1e-9, weighted_games)
    return {
        "fitness": fitness,
        "weighted_win_rate": fitness,
        "opponents": per_opponent,
        "suite_size": len(suite),
    }


if __name__ == "__main__":
    deck = load_suite()[0].load()
    print(f"benchmark suite: {len(load_suite())} decks")
    print("smoke eval on first opponent deck only — use train_deck_campaign for full run")
