"""Record local cabt battles as JSON for replay analysis and regression tests.

Uses cg.game directly (same as selfplay.py). Output shape is compatible with
analyze_submission / episode_stats parsers.

Usage:
  python scripts/record_local_battle.py --agent-a lucario --agent-b search --games 20
  python scripts/record_local_battle.py --agent-a rulecore --deck-a agent_decks/real_mega_lucario_ex.csv --games 5 --seed 42
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "data" / "sim" / "sample_submission"
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from cg import game  # noqa: E402
from cg.sim import Battle, lib  # noqa: E402
from episode_stats import (  # noqa: E402
    FAST_LOSS_TURN_THRESHOLD,
    RESULT_REASONS,
    aggregate_rows,
    infer_result_reason,
)

OUT_DIR = ROOT / "report" / "local_replays"
DEFAULT_DECK = ENGINE_DIR / "deck.csv"


def load_deck(path: Path) -> list[int]:
    return [int(x) for x in path.read_text().splitlines() if x.strip()][:60]


def select_player() -> int:
    return lib.GetBattleData(Battle.battle_ptr).selectPlayer


def build_policy(name: str, deck_path: Path, seed: int):
    from agent.agent import Agent, build_agent
    from agent.learned_policy import LearnedScorer
    from agent.lucario_policy import LucarioScorer
    from agent.rule_core import RuleCoreScorer
    from agent.search_policy import LucarioSearchScorer, SearchScorer

    dp = str(deck_path)
    if name == "heuristic":
        return Agent(seed=seed, deck_path=dp).act
    if name == "search":
        return build_agent(seed=seed, deck_path=dp, scorer=SearchScorer()).act
    if name == "rulecore":
        return build_agent(seed=seed, deck_path=dp, scorer=RuleCoreScorer(deck_path=dp)).act
    if name == "lucario":
        return build_agent(seed=seed, deck_path=dp, scorer=LucarioScorer(deck_path=dp)).act
    if name == "lucario_search":
        return build_agent(seed=seed, deck_path=dp, scorer=LucarioSearchScorer(deck_path=dp)).act
    if name == "learned":
        return build_agent(seed=seed, deck_path=dp, scorer=LearnedScorer(deck_path=dp)).act
    raise ValueError(f"unknown agent: {name}")


def run_recorded_game(
    pol0,
    pol1,
    deck0: list[int],
    deck1: list[int],
    *,
    record_steps: bool = True,
    max_steps: int = 6000,
) -> dict:
    obs, start = game.battle_start(deck0, deck1)
    if obs is None:
        raise RuntimeError(f"battle_start failed: err={start.errorType}")

    policies = (pol0, pol1)
    steps: list[list[dict]] = []
    turn_count = 0
    winner = -1
    reason = "unknown"

    try:
        for _ in range(max_steps):
            cur = obs.get("current") or {}
            turn_count = max(turn_count, int(cur.get("turn", 0) or 0))
            result = cur.get("result", -1)
            if result != -1:
                winner = int(result)
                players = cur.get("players") or []
                reason = infer_result_reason(winner, players)
                for log in obs.get("logs") or []:
                    if log.get("type") == 5:
                        reason = RESULT_REASONS.get(int(log.get("reason", 0) or 0), reason)
                break
            if obs.get("select") is None:
                break
            p = select_player()
            choice = policies[p](obs)
            if record_steps:
                steps.append([
                    {"observation": obs, "action": choice, "playerIndex": p},
                    {"observation": obs, "action": [], "playerIndex": 1 - p},
                ])
            obs = game.battle_select(choice)
    finally:
        game.battle_finish()

    reward_a = 1.0 if winner == 0 else -1.0 if winner == 1 else 0.0
    reward_b = -reward_a if winner in (0, 1) else 0.0
    outcome_a = "win" if winner == 0 else "loss" if winner == 1 else "draw" if winner == 2 else "unfinished"

    return {
        "turn_count": turn_count,
        "winner": winner,
        "result_reason": reason,
        "rewards": [reward_a, reward_b],
        "steps": steps,
        "games": [{
            "game_index": 0,
            "turn_count": turn_count,
            "winner": winner,
            "result_reason": reason,
            "outcome": outcome_a,
            "reward": reward_a,
        }],
    }


def match_record(
    make_a,
    make_b,
    deck_a: list[int],
    deck_b: list[int],
    n: int,
    *,
    record_steps: bool,
) -> tuple[list[dict], Counter, Counter, object]:
    games: list[dict] = []
    outcomes: Counter = Counter()
    loss_reasons: Counter = Counter()
    rows_for_stats = []

    from episode_stats import EpisodeRow

    for i in range(n):
        pa, pb = make_a(i), make_b(i)
        if i % 2 == 0:
            data = run_recorded_game(pa, pb, deck_a, deck_b, record_steps=record_steps)
            our_winner = data["winner"]
        else:
            data = run_recorded_game(pb, pa, deck_b, deck_a, record_steps=record_steps)
            our_winner = 1 if data["winner"] == 0 else 0 if data["winner"] == 1 else data["winner"]

        g = data["games"][0].copy()
        g["game_index"] = i
        if i % 2 == 1:
            g["outcome"] = "win" if our_winner == 1 else "loss" if our_winner == 0 else "draw"
            g["reward"] = 1.0 if our_winner == 1 else -1.0 if our_winner == 0 else 0.0
        games.append(g)
        outcomes[g["outcome"]] += 1
        if g["outcome"] == "loss":
            loss_reasons[g["result_reason"]] += 1
        rows_for_stats.append(EpisodeRow(
            episode_id=str(i),
            source="local",
            agent_index=0,
            opponent_index=1,
            reward=float(g["reward"]),
            outcome=g["outcome"],
            turn_count=int(g["turn_count"]),
            result_reason=g["result_reason"],
        ))

    stats = aggregate_rows("local", rows_for_stats)
    return games, outcomes, loss_reasons, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent-a", default="lucario",
                        choices=("heuristic", "search", "rulecore", "lucario", "lucario_search", "learned"))
    parser.add_argument("--agent-b", default="search",
                        choices=("heuristic", "search", "rulecore", "lucario", "lucario_search", "learned"))
    parser.add_argument("--deck-a", default=str(DEFAULT_DECK))
    parser.add_argument("--deck-b", default=str(DEFAULT_DECK))
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--name", default="local_battle")
    parser.add_argument("--full-steps", action="store_true",
                        help="Record every obs/action step (large files)")
    args = parser.parse_args(argv)

    deck_a = load_deck(Path(args.deck_a))
    deck_b = load_deck(Path(args.deck_b))
    deck_a_path = Path(args.deck_a)
    deck_b_path = Path(args.deck_b)

    games, outcomes, loss_reasons, stats = match_record(
        lambda i: build_policy(args.agent_a, deck_a_path, args.seed + i),
        lambda i: build_policy(args.agent_b, deck_b_path, args.seed + 9000 + i),
        deck_a,
        deck_b,
        args.games,
        record_steps=args.full_steps,
    )

    payload = {
        "name": args.name,
        "agent_a": args.agent_a,
        "agent_b": args.agent_b,
        "deck_a": str(deck_a_path),
        "deck_b": str(deck_b_path),
        "games": games,
        "summary": {
            "wins": stats.wins,
            "losses": stats.losses,
            "draws": stats.draws,
            "win_rate": stats.win_rate,
            "avg_turns": stats.avg_turns,
            "median_turns": stats.median_turns,
            "fast_loss_pct": stats.fast_loss_pct,
            "top_loss_reason": stats.top_loss_reason,
            "loss_reasons": dict(loss_reasons),
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{args.name}_seed{args.seed}.json"
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    decided = stats.wins + stats.losses
    print(f"{args.agent_a} vs {args.agent_b}  n={args.games}")
    print(f"  W/L/D: {stats.wins}/{stats.losses}/{stats.draws}  win_rate={stats.win_rate}%")
    print(f"  avg_turns={stats.avg_turns}  median={stats.median_turns}")
    print(f"  fast_loss_pct (<{FAST_LOSS_TURN_THRESHOLD})={stats.fast_loss_pct}%")
    print(f"  loss reasons: {dict(loss_reasons)}")
    print(f"wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
