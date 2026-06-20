"""Tests for Kaggle replay parsing and per-episode agent_index resolution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from episode_stats import (  # noqa: E402
    infer_result_reason,
    load_json,
    parse_replay,
    resolve_agent_index,
    winner_from_rewards,
)


def test_winner_from_rewards():
    assert winner_from_rewards([1, -1]) == 0
    assert winner_from_rewards([-1, 1]) == 1
    assert winner_from_rewards([0, 0]) == 2


def test_infer_result_reason_prize():
    players = [
        {"prize": [1, 2], "deckCount": 3, "active": [{"id": 1}]},
        {"prize": [1, 2, 3, 4, 5, 6], "deckCount": 10, "active": [{"id": 2}]},
    ]
    assert infer_result_reason(0, players) == "prize"


def test_resolve_agent_index_manifest_wins():
    data = {"info": {"TeamNames": ["alpha", "beta"]}}
    assert resolve_agent_index(data, manifest_index=1, team_name="alpha") == 1


def test_resolve_agent_index_team_name():
    data = {"info": {"TeamNames": ["TrustHub hiroingk", "foo"]}}
    idx = resolve_agent_index(data, team_name="TrustHub hiroingk")
    assert idx == 0


def test_parse_replay_53869254_sample():
    replay = ROOT / "report" / "replays" / "episode-80902314-replay.json"
    if not replay.exists():
        replay = ROOT / "report" / "replays" / "80902314.json"
    if not replay.exists():
        return
    data = load_json(replay)
    row_wrong = parse_replay(data, our_agent_index=0)
    row_right = parse_replay(data, our_agent_index=1)
    assert row_wrong is not None and row_right is not None
    assert row_wrong.outcome == "win"
    assert row_right.outcome == "loss"
    assert row_right.result_reason == "prize"
    assert row_right.turn_count == 11
