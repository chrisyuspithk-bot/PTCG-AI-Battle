"""Smoke tests for eval/harness (requires Python >=3.11 and cg engine)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _clear_harness_cache():
    from eval.harness import clear_caches

    clear_caches()
    yield
    clear_caches()


def test_l0_registry_loads():
    from eval.gates import gate_l0_import_smoke

    ok, msg = gate_l0_import_smoke()
    assert ok, msg


def test_run_match_legal_two_games():
    from eval.harness import DEFAULT_LUCARIO_DECK, clear_caches, gate_vs_opponent, load_deck, make_lucario_brain

    clear_caches()
    deck = load_deck(DEFAULT_LUCARIO_DECK)
    brain = make_lucario_brain(DEFAULT_LUCARIO_DECK)
    result = gate_vs_opponent(brain, deck, "dragapult_ex_sample", games=2)
    assert result is not None
    assert result.games == 2
    assert result.wins + result.losses + result.draws + result.unfinished == 2
    assert result.unfinished == 0


def test_alakazam_agent_deck_select():
    from eval.harness import make_alakazam_brain

    brain = make_alakazam_brain()
    out = brain({"select": None, "current": None})
    assert isinstance(out, list) and len(out) == 60
    assert all(isinstance(c, int) for c in out)


def test_starmie_agent_deck_select():
    from eval.harness import make_starmie_brain

    brain = make_starmie_brain()
    out = brain({"select": None, "current": None})
    assert isinstance(out, list) and len(out) == 60
    assert all(isinstance(c, int) for c in out)


def test_lever_override_param():
    from agent.matchup_levers import LUCARIO_LEVERS, LeverDeltas
    from dataclasses import replace

    from eval.harness import DEFAULT_LUCARIO_DECK, clear_caches, gate_vs_opponent, load_deck, make_lucario_brain

    clear_caches()
    base = LUCARIO_LEVERS["dragapult_psychic"]
    overrides = {"dragapult_psychic": replace(base, boss_orders=9999.0)}
    deck = load_deck(DEFAULT_LUCARIO_DECK)
    brain = make_lucario_brain(DEFAULT_LUCARIO_DECK, lever_overrides=overrides)
    result = gate_vs_opponent(brain, deck, "dragapult_ex_sample", games=1)
    assert result is not None
