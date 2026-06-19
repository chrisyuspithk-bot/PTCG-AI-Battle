"""Tests for rl/env_factory.py (no GPU required)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_load_benchmark_opponents():
    from rl.env_factory import load_opponent_decks

    decks = load_opponent_decks("benchmark")
    assert len(decks) >= 6
    for d in decks:
        assert len(d) == 60
        assert all(isinstance(c, int) for c in d)


def test_load_pool_opponents():
    from rl.env_factory import load_opponent_decks

    decks = load_opponent_decks("pool")
    assert len(decks) == 6


def test_deck_slug():
    from rl.env_factory import deck_slug

    assert "kyogre" in deck_slug("agent_decks/a2_kyogre_33_energy.csv")


def test_masked_env_reset_smoke():
    pytest = __import__("pytest")
    try:
        import gymnasium  # noqa: F401
    except ImportError:
        pytest.skip("gymnasium not installed")

    from rl.env_factory import make_masked_cabt_env

    env = make_masked_cabt_env(ROOT / "agent" / "deck.csv", opponents="pool", seed=0)
    obs, info = env.reset()
    assert "action_mask" in info
    assert obs.ndim == 1
    env.close()
