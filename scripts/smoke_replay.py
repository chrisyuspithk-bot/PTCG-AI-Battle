"""Golden replay fixtures for bench-guard policy (L0 extension).

Run: python scripts/smoke_replay.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data" / "sim" / "sample_submission"))

from agent.agent import (  # noqa: E402
    CTX_SETUP_BENCH_POKEMON,
    OPT_ATTACK,
    OPT_END,
    OPT_PLAY,
    SEL_CARD,
    SEL_MAIN,
    Agent,
    build_agent,
)
from agent.lucario_policy import LucarioScorer, Mega_Lucario_ex, Riolu
from agent.smart_bench import MAX_VOLUNTARY_BENCH

DECK = str(ROOT / "agent_decks" / "real_mega_lucario_ex.csv")
passed = 0
failed = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))


def _legal(indices, select) -> bool:
    opts = select.get("option") or []
    mc = int(select.get("maxCount", len(opts)) or len(opts))
    mn = int(select.get("minCount", 0) or 0)
    if not isinstance(indices, list):
        indices = [indices]
    if len(set(indices)) != len(indices):
        return False
    if not (mn <= len(indices) <= mc):
        return False
    return all(0 <= i < len(opts) for i in indices)


def _bench_empty_current():
    return {
        "turn": 8,
        "yourIndex": 0,
        "players": [
            {
                "active": [{"id": 673, "hp": 80}],
                "bench": [],
                "benchMax": 5,
                "hand": [
                    {"id": Riolu},
                    {"id": 6},
                    {"id": 1123},
                ],
            },
            {"active": [{"id": 721, "hp": 100}], "bench": [], "hand": []},
        ],
    }


def test_empty_bench_must_play():
    agent = build_agent(seed=0, deck_path=DECK, scorer=LucarioScorer(deck_path=DECK))
    current = _bench_empty_current()
    options = [
        {"type": OPT_PLAY, "index": 0},
        {"type": OPT_ATTACK, "attackId": 1},
        {"type": OPT_END},
    ]
    select = {"type": SEL_MAIN, "option": options, "minCount": 1, "maxCount": 1}
    obs = {"logs": [], "current": current, "select": select}
    out = agent.act(obs)
    idx = out[0] if isinstance(out, list) else out
    chosen = options[idx]
    check(
        "empty_bench_must_play",
        chosen.get("type") == OPT_PLAY,
        f"got type={chosen.get('type')}",
    )


def test_smart_bench_caps_at_2():
    agent = Agent(seed=0)
    options = [{"type": 1, "index": i} for i in range(4)]
    select = {
        "type": SEL_CARD,
        "context": CTX_SETUP_BENCH_POKEMON,
        "option": options,
        "minCount": 0,
        "maxCount": 4,
    }
    obs = {"logs": [], "current": {}, "select": select}
    out = agent.act(obs)
    check(
        "smart_bench_caps_at_2",
        1 <= len(out) <= MAX_VOLUNTARY_BENCH and _legal(out, select),
        f"len={len(out)}",
    )


def test_lucario_search_trainer_scoring():
    """Search items prioritized when Riolu line is missing; Gong when Riolu needs energy."""
    from types import SimpleNamespace

    from agent.lucario_policy import LucarioPlan

    def _ctx(*, riolu_line=0, has_riolu=False, riolu_e=0, has_mega=False, mega_e=0, deck=30):
        fc = {}
        if has_mega:
            fc[Mega_Lucario_ex] = 1
            line = 1
        elif has_riolu or riolu_line:
            fc[Riolu] = max(1, riolu_line)
            line = max(1, riolu_line)
        else:
            line = 0
        line_needs = (has_riolu and riolu_e < 2) or (has_mega and mega_e < 2)
        return {
            "field_counts": fc,
            "deck_count": deck,
            "riolu_line": line,
            "has_riolu_in_play": has_riolu,
            "riolu_min_energy": riolu_e if has_riolu else 0,
            "has_mega_lucario": has_mega,
            "mega_min_energy": mega_e if has_mega else 0,
            "line_needs_energy": line_needs,
        }

    scorer = LucarioScorer(deck_path=DECK)
    state = SimpleNamespace(turn=4, supporterPlayed=False)
    plan = LucarioPlan()
    hand = {Riolu: 0, Mega_Lucario_ex: 0}

    no_line = _ctx()
    dusk_no_line = scorer._score_play_trainer(
        1102, plan, False, hand, 0, state, no_line,
    )
    carmine = scorer._score_play_trainer(
        1192, plan, False, hand, 0, state, no_line,
    )
    check(
        "dusk_ball_prioritized_without_line",
        dusk_no_line > carmine,
        f"dusk={dusk_no_line} carmine={carmine}",
    )

    pad_no_line = scorer._score_play_trainer(
        1152, plan, False, hand, 0, state, no_line,
    )
    check(
        "poke_pad_beats_dusk_without_line",
        pad_no_line > dusk_no_line,
        f"pad={pad_no_line} dusk={dusk_no_line}",
    )

    riolu_needs_e = _ctx(riolu_line=1, has_riolu=True, riolu_e=0)
    gong = scorer._score_play_trainer(
        1142, plan, False, hand, 0, state, riolu_needs_e,
    )
    check(
        "fighting_gong_when_riolu_underpowered",
        gong >= 9200.0,
        f"gong={gong}",
    )

    ppp_hungry = scorer._score_play_trainer(
        1141, plan, False, hand, 0, state,
        _ctx(has_riolu=True, riolu_e=0, riolu_line=1),
    )
    check(
        "ppp_when_line_needs_energy",
        ppp_hungry >= 8700.0,
        f"ppp={ppp_hungry}",
    )

    gravity = scorer._score_play_trainer(
        1252, plan, False, hand, 0, state,
        {**no_line, "op_stage2_count": 2},
    )
    check(
        "gravity_mountain_vs_stage2",
        gravity >= 8900.0,
        f"gravity={gravity}",
    )

    low = _ctx(deck=8)
    check(
        "carmine_blocked_at_low_deck",
        scorer._score_play_trainer(1192, plan, False, hand, 0, state, low) < 0,
        "carmine should be -1 at deck<=10",
    )
    check(
        "lillie_blocked_at_low_deck",
        scorer._score_play_trainer(1227, plan, False, hand, 0, state, low) < 0,
        "lillie should be -1 at deck<=10",
    )
    thin = _ctx(deck=14)
    dusk_thin = scorer._score_play_trainer(1102, plan, False, hand, 0, state, thin)
    carmine_thin = scorer._score_play_trainer(1192, plan, False, hand, 0, state, thin)
    check(
        "carmine_throttled_at_thin_deck",
        carmine_thin < dusk_thin,
        f"carmine={carmine_thin} dusk={dusk_thin}",
    )


def test_lucario_line_energy_scoring():
    """Feed Riolu/Mega early: attach and search beat generic targets."""
    from types import SimpleNamespace

    from agent.lucario_policy import LucarioPlan

    scorer = LucarioScorer(deck_path=DECK)
    state = SimpleNamespace(turn=5, supporterPlayed=False)
    ctx = {
        "field_counts": {Riolu: 1},
        "deck_count": 40,
        "riolu_line": 1,
        "has_riolu_in_play": True,
        "riolu_min_energy": 0,
        "has_mega_lucario": False,
        "mega_min_energy": 0,
        "line_needs_energy": True,
    }
    riolu = SimpleNamespace(id=Riolu, energies=[])
    makuhita = SimpleNamespace(id=673, energies=[])
    riolu_score = scorer._energy_score(
        riolu, False, False, False, state=state, ctx=ctx,
    )
    wall_score = scorer._energy_score(
        makuhita, False, False, False, state=state, ctx=ctx,
    )
    check(
        "riolu_attach_beats_wall",
        riolu_score > wall_score,
        f"riolu={riolu_score} wall={wall_score}",
    )

    mega = SimpleNamespace(id=Mega_Lucario_ex, energies=[])
    mega_score = scorer._energy_score(
        mega, True, False, False, state=state, ctx=ctx,
    )
    check(
        "mega_active_gets_energy_boost",
        mega_score > wall_score,
        f"mega={mega_score} wall={wall_score}",
    )

    plan = LucarioPlan()
    evolve_ready = SimpleNamespace(id=Riolu, energies=[1])
    # Simulated ATTACH path bonus: one energy away from evolve threshold.
    attach_score = float(scorer._energy_score(
        evolve_ready, False, False, False, state=state, ctx=ctx,
    )) + 280.0 + 400.0
    check(
        "riolu_one_from_evolve_high_attach",
        attach_score >= 9000.0,
        f"attach={attach_score}",
    )


def test_lucario_empty_bench_attack_scoring():
    """Empty bench: penalize non-KO attacks; allow KO attacks (Lucario plan logic)."""
    from types import SimpleNamespace

    from agent.lucario_policy import LucarioPlan

    active = SimpleNamespace(
        id=673, hp=80, energies=[], energyCards=[], tools=[],
    )
    opponent = SimpleNamespace(id=721, hp=100, energies=[])
    my_player = SimpleNamespace(
        active=[active], bench=[], hand=[], discard=[], prize=[1] * 6,
    )
    op_player = SimpleNamespace(active=[opponent], bench=[], prize=[1] * 6)
    state = SimpleNamespace(
        turn=8,
        yourIndex=0,
        firstPlayer=0,
        energyAttached=False,
        supporterPlayed=False,
        stadium=[],
        players=[my_player, op_player],
    )
    attack_opt = SimpleNamespace(type=OPT_ATTACK, attackId=983)
    end_opt = SimpleNamespace(type=OPT_END)
    sel = SimpleNamespace(
        type=SEL_MAIN,
        context=0,
        option=[attack_opt, end_opt],
        minCount=1,
        maxCount=1,
    )
    obs = SimpleNamespace(current=state, select=sel)

    scorer = LucarioScorer(deck_path=DECK)
    scorer._plan_turn = state.turn
    ctx = scorer._scan(obs)

    scorer._plan = LucarioPlan(remain_hp=50)
    no_ko_attack = scorer._score_option(obs, ctx, attack_opt)
    no_ko_end = scorer._score_option(obs, ctx, end_opt)
    check(
        "attack_penalized_no_ko_empty_bench",
        no_ko_attack < no_ko_end,
        f"attack={no_ko_attack} end={no_ko_end}",
    )

    scorer._plan = LucarioPlan(remain_hp=-1)
    ko_attack = scorer._score_option(obs, ctx, attack_opt)
    ko_end = scorer._score_option(obs, ctx, end_opt)
    check(
        "attack_allowed_on_ko_empty_bench",
        ko_attack > ko_end,
        f"attack={ko_attack} end={ko_end}",
    )


def test_lucario_search_scorer_instantiates():
    from agent.search_policy import LucarioSearchScorer

    scorer = LucarioSearchScorer(deck_path=DECK)
    check(
        "lucario_search_scorer_instantiates",
        scorer is not None and hasattr(scorer, "choose"),
        "missing choose",
    )


def main() -> int:
    print("bench-guard golden replay tests")
    test_empty_bench_must_play()
    test_smart_bench_caps_at_2()
    test_lucario_search_scorer_instantiates()
    test_lucario_search_trainer_scoring()
    test_lucario_line_energy_scoring()
    test_lucario_empty_bench_attack_scoring()
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
