"""Trace bench guard on no_active repro (seed 2025 vs Abomasnow, Dragapult seat 1)."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "sim", "sample_submission"))
sys.path.insert(0, ROOT)
os.environ["DRAGAPULT_DECK"] = os.path.join(ROOT, "agent_decks", "dragapult_ex_sample.csv")

from cg import game  # noqa: E402
from cg.api import to_observation_class  # noqa: E402
from cg.sim import Battle, lib  # noqa: E402
from agent.agent import Agent  # noqa: E402
from agent.dragapult_agent import _agent_impl, agent as drag  # noqa: E402
from agent.dragapult_bench_guard import (  # noqa: E402
    apply_bench_guard,
    bench_count,
    mandatory_bench_indices,
)
from agent.search_policy import SearchScorer  # noqa: E402


def load(path: str) -> list[int]:
    return [int(x) for x in open(path).read().splitlines() if x.strip()][:60]


def main() -> None:
    deck_d = load(os.path.join(ROOT, "agent_decks", "dragapult_ex_sample.csv"))
    deck_o = load(os.path.join(ROOT, "agent_decks", "real_mega_abomasnow_ex.csv"))
    opp = Agent(
        seed=2025,
        deck_path=os.path.join(ROOT, "agent_decks", "real_mega_abomasnow_ex.csv"),
        scorer=SearchScorer(),
    )
    obs, _ = game.battle_start(deck_d, deck_o)
    drag_seat = 0
    for step in range(200):
        cur = obs["current"]
        if cur and cur.get("result", -1) != -1:
            print("END", cur["result"], "turn", cur.get("turn"))
            break
        p = lib.GetBattleData(Battle.battle_ptr).selectPlayer
        if p == drag_seat:
            o = to_observation_class(obs)
            bc = bench_count(o, drag_seat)
            raw = _agent_impl(obs)
            guarded = apply_bench_guard(obs, raw)
            mand = mandatory_bench_indices(o)
            sel = obs["select"]
            active = o.current.players[drag_seat].active
            aid = active[0].id if active and active[0] else None
            print(
                f"step={step} turn={cur.get('turn')} ctx={sel.get('context')} "
                f"bench={bc} active={aid} raw={raw} guard={guarded} mand={mand}"
            )
        choice = drag(obs) if p == drag_seat else opp.act(obs)
        obs = game.battle_select(choice)
    game.battle_finish()


if __name__ == "__main__":
    main()
