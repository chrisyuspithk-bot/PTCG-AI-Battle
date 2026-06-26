"""Unit tests for agent/prize_tracker.py (no cg engine required)."""

from __future__ import annotations

from collections import Counter
from types import SimpleNamespace

from agent.prize_tracker import PrizeTracker


def _card(cid: int, serial: int = 1, player_index: int = 0):
    return SimpleNamespace(id=cid, serial=serial, playerIndex=player_index)


def _player(
    hand=[],
    prize_count=6,
    deck_count=46,
    active=[],
    bench=[],
    discard=[],
):
    return SimpleNamespace(
        hand=hand,
        prize=[_card(0, serial=i) for i in range(prize_count)],
        deckCount=deck_count,
        active=active,
        bench=bench,
        discard=discard,
    )


def _obs(player, deck_cards, effect=None, your_index=0):
    select = SimpleNamespace(deck=deck_cards, effect=effect)
    current = SimpleNamespace(
        yourIndex=your_index,
        players=[player, _player()],
        stadium=[],
    )
    return SimpleNamespace(select=select, current=current)


def test_deduce_prize_when_deck_fully_visible():
    decklist = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    tracker = PrizeTracker(decklist)
    # Deck search shows non-prized cards still in deck; prized cards stay hidden.
    player = _player(
        hand=[_card(10, 1), _card(20, 2)],
        prize_count=3,
        deck_count=3,
        discard=[_card(30, 3)],
    )
    obs = _obs(player, [_card(40, 4), _card(50, 5), _card(60, 6)])
    tracker.update(obs)
    prized = tracker.prized_cards()
    assert prized == Counter({70: 1, 80: 1, 90: 1})


def test_returns_unknown_when_counts_inconsistent():
    decklist = [10, 20, 30]
    tracker = PrizeTracker(decklist)
    player = _player(hand=[_card(10, 1)], prize_count=2, deck_count=2)
    obs = _obs(player, [_card(20, 2), _card(30, 3)])
    tracker.update(obs)
    assert tracker.prized_cards() is None


def test_subtracts_in_flight_effect_card():
    decklist = [100, 200, 300, 400, 500, 600]
    tracker = PrizeTracker(decklist)
    player = _player(hand=[], prize_count=2, deck_count=2, discard=[_card(100, 1)])
    effect = _card(200, 2, player_index=0)
    obs = _obs(player, [_card(300, 3), _card(400, 4)], effect=effect)
    tracker.update(obs)
    assert tracker.prized_cards() == Counter({500: 1, 600: 1})


def test_is_prized_query():
    tracker = PrizeTracker([1, 2, 3])
    assert tracker.is_prized(1) is None
    tracker._prized = Counter({2: 1})
    assert tracker.is_prized(2) is True
    assert tracker.is_prized(1) is False
