"""Shared episode / replay statistics for local and Kaggle JSON."""

from __future__ import annotations

import json
import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Match scripts/eval_matrix.py
RESULT_REASONS = {
    1: "prize",
    2: "deck_out",
    3: "no_active",
    4: "card_effect",
}

FAST_LOSS_TURN_THRESHOLD = 15


@dataclass
class EpisodeRow:
    episode_id: str
    source: str
    agent_index: int
    opponent_index: int
    reward: float
    outcome: str
    turn_count: int
    result_reason: str
    episode_type: str = ""


@dataclass
class SubmissionStats:
    ref: str = ""
    episodes_total: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_rate: float = 0.0
    avg_turns: float = 0.0
    median_turns: float = 0.0
    fast_loss_pct: float = 0.0
    top_loss_reason: str = ""
    loss_reason_counts: Counter = field(default_factory=Counter)
    rows: list[EpisodeRow] = field(default_factory=list)

    def aggregate(self) -> None:
        decided = self.wins + self.losses
        self.win_rate = round(100.0 * self.wins / decided, 2) if decided else 0.0
        turns = [r.turn_count for r in self.rows if r.turn_count > 0]
        self.avg_turns = round(statistics.mean(turns), 2) if turns else 0.0
        self.median_turns = round(statistics.median(turns), 2) if turns else 0.0
        loss_turns = [
            r.turn_count
            for r in self.rows
            if r.outcome == "loss" and r.turn_count > 0
        ]
        fast = sum(1 for t in loss_turns if t < FAST_LOSS_TURN_THRESHOLD)
        self.fast_loss_pct = round(100.0 * fast / len(loss_turns), 2) if loss_turns else 0.0
        if self.loss_reason_counts:
            self.top_loss_reason = self.loss_reason_counts.most_common(1)[0][0]
        self.episodes_total = len(self.rows)


def team_names_from_replay(data: dict[str, Any]) -> list[str]:
    info = data.get("info") or {}
    names = info.get("TeamNames") or info.get("teamNames") or info.get("teams") or []
    if isinstance(names, list):
        return [str(n) for n in names]
    return []


def winner_from_rewards(rewards: list[Any]) -> int | None:
    numeric: list[tuple[int, float]] = []
    for i, reward in enumerate(rewards):
        try:
            numeric.append((i, float(reward)))
        except (TypeError, ValueError):
            continue
    if not numeric:
        return None
    best = max(numeric, key=lambda x: x[1])
    if sum(1 for _i, reward in numeric if reward == best[1]) > 1:
        return 2
    return best[0]


def resolve_agent_index(
    data: dict[str, Any],
    *,
    manifest_index: int | None = None,
    team_name: str | None = None,
    default: int = 0,
) -> int:
    """Pick our agent seat for one episode (manifest > team name > default)."""
    if manifest_index is not None:
        return manifest_index
    if team_name:
        needle = team_name.strip().casefold()
        for i, name in enumerate(team_names_from_replay(data)):
            if name.strip().casefold() == needle:
                return i
    return default


def _terminal_players(data: dict[str, Any]) -> tuple[int, list[dict]]:
    """Return (turn_count, players) from the latest step exposing player state."""
    steps = data.get("steps")
    if not isinstance(steps, list):
        return 0, []
    best_turn = 0
    best_players: list[dict] = []
    for step in steps:
        if not isinstance(step, list):
            continue
        for player_state in step:
            if not isinstance(player_state, dict):
                continue
            obs = player_state.get("observation") or player_state
            if not isinstance(obs, dict):
                continue
            current = obs.get("current") or {}
            players = current.get("players") or []
            if len(players) < 2:
                continue
            turn = int(current.get("turn", 0) or 0)
            if turn >= best_turn:
                best_turn = turn
                best_players = players
    return best_turn, best_players


def infer_result_reason(winner: int, players: list[dict]) -> str:
    if winner in (0, 1) and winner < len(players):
        loser = 1 - winner
        if loser < len(players):
            lp = players[loser]
            wp = players[winner]
            if int(lp.get("deckCount", 1) or 0) <= 0:
                return "deck_out"
            w_prizes = len(wp.get("prize") or [])
            l_prizes = len(lp.get("prize") or [])
            if w_prizes < l_prizes or w_prizes == 0:
                return "prize"
            if not (lp.get("active") or []):
                return "no_active"
        return "prize"
    return "draw" if winner == 2 else "unknown"


def _turn_from_obs(obs: dict) -> int:
    current = obs.get("current") or {}
    return int(current.get("turn", 0) or 0)


def _parse_result_from_obs(obs: dict) -> tuple[int, str]:
    current = obs.get("current") or {}
    winner = int(current.get("result", -1))
    reason = "unknown"
    for log in obs.get("logs") or []:
        if log.get("type") == 5:  # LogType.RESULT
            winner = int(log.get("result", winner))
            reason = RESULT_REASONS.get(int(log.get("reason", 0) or 0), reason)
    if reason == "unknown" and winner in (0, 1, 2):
        players = current.get("players") or []
        reason = infer_result_reason(winner, players)
    return winner, reason


def parse_replay(data: dict[str, Any], our_agent_index: int = 0) -> EpisodeRow | None:
    """Parse one Kaggle replay JSON blob into stats for our agent."""
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        return None
    rewards = data.get("rewards") or []
    episode_id = str(
        (data.get("info") or {}).get("EpisodeId")
        or data.get("episodeId")
        or data.get("episode_id")
        or data.get("id")
        or ""
    )

    turn_count = 0
    winner = -1
    reason = "unknown"
    terminal_players: list[dict] = []
    for step in reversed(steps):
        if not isinstance(step, list):
            continue
        for player_state in step:
            if not isinstance(player_state, dict):
                continue
            obs = player_state.get("observation") or player_state
            if not isinstance(obs, dict):
                continue
            t = _turn_from_obs(obs)
            if t > turn_count:
                turn_count = t
            cur = obs.get("current") or {}
            players = cur.get("players") or []
            if len(players) >= 2:
                terminal_players = players
            if int(cur.get("result", -1)) != -1:
                winner, reason = _parse_result_from_obs(obs)
                break
        if winner != -1:
            break

    if winner == -1:
        inferred = winner_from_rewards(rewards)
        if inferred is not None:
            winner = inferred
            term_turn, terminal_players = _terminal_players(data)
            if term_turn > turn_count:
                turn_count = term_turn
            if terminal_players:
                reason = infer_result_reason(winner, terminal_players)
            elif winner in (0, 1):
                reason = "prize"

    if turn_count <= 0:
        turn_count, terminal_players = _terminal_players(data)

    try:
        reward = float(rewards[our_agent_index]) if our_agent_index < len(rewards) else 0.0
    except (TypeError, ValueError):
        reward = 0.0

    if reward > 0:
        outcome = "win"
    elif reward < 0:
        outcome = "loss"
    else:
        outcome = "draw"

    if winner == our_agent_index:
        outcome = "win"
    elif winner in (0, 1):
        outcome = "loss"
    elif winner == 2:
        outcome = "draw"

    if outcome == "win" and reason in ("unknown", "draw"):
        reason = "prize"
    if outcome == "loss" and reason == "unknown" and terminal_players:
        winner_idx = 1 - our_agent_index if winner in (0, 1) else winner
        if winner_idx in (0, 1):
            reason = infer_result_reason(winner_idx, terminal_players)

    return EpisodeRow(
        episode_id=episode_id,
        source="replay",
        agent_index=our_agent_index,
        opponent_index=1 - our_agent_index,
        reward=reward,
        outcome=outcome,
        turn_count=turn_count,
        result_reason=reason if outcome == "loss" else ("prize" if outcome == "win" else reason),
    )


def parse_local_recording(data: dict[str, Any], our_agent_index: int = 0) -> EpisodeRow:
    """Parse output from record_local_battle.py."""
    games = data.get("games") or []
    if games:
        g = games[0]
        outcome = g.get("outcome", "unknown")
        reason = g.get("result_reason", "unknown")
        return EpisodeRow(
            episode_id=str(g.get("game_index", 0)),
            source="local",
            agent_index=our_agent_index,
            opponent_index=1 - our_agent_index,
            reward=float(g.get("reward", 0) or 0),
            outcome=outcome,
            turn_count=int(g.get("turn_count", 0) or 0),
            result_reason=reason if outcome == "loss" else reason,
        )
    return EpisodeRow(
        episode_id="0",
        source="local",
        agent_index=our_agent_index,
        opponent_index=1 - our_agent_index,
        reward=0.0,
        outcome="unknown",
        turn_count=int(data.get("turn_count", 0) or 0),
        result_reason=str(data.get("result_reason", "unknown")),
    )


def aggregate_rows(ref: str, rows: list[EpisodeRow]) -> SubmissionStats:
    stats = SubmissionStats(ref=ref, rows=rows)
    for row in rows:
        if row.outcome == "win":
            stats.wins += 1
        elif row.outcome == "loss":
            stats.losses += 1
            stats.loss_reason_counts[row.result_reason] += 1
        else:
            stats.draws += 1
    stats.aggregate()
    return stats


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
