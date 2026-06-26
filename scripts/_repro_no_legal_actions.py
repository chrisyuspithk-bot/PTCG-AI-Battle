"""Find states where all search_step probes fail (options=2)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch

import agent.lucario_mcts_runtime as rt
from agent.native_opponent import make_opponent_brain
from cg.api import search_begin, search_end, search_release, search_step, to_observation_class

DECK_PATH = ROOT / "agent_decks/real_mega_lucario_ex.csv"
OPP_PATH = ROOT / "agent_decks/real_mega_abomasnow_ex.csv"


def main() -> None:
    deck = [int(x) for x in DECK_PATH.read_text().splitlines() if x.strip()]
    aboma = [int(x) for x in OPP_PATH.read_text().splitlines() if x.strip()]
    opp = make_opponent_brain("native", str(OPP_PATH), aboma, opp_name="x")[0]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = rt.MyModel(rt.D_MODEL, rt.NUM_HEADS, rt.D_FF, rt.ENC_LAYERS, rt.DEC_LAYERS).to(device)
    model.load_state_dict(
        torch.load(ROOT / "rl_mcts_field/lucarioex_v5_field/model_latest.pth", map_location=device, weights_only=True)
    )
    model.eval()
    rt.SEARCH_COUNT = 20

    for attempt in range(500):
        obs, _ = rt.battle_start(deck, aboma)
        for _ply in range(300):
            if obs["current"]["result"] >= 0:
                break
            yi = obs["current"]["yourIndex"]
            if yi != 0:
                obs = rt.battle_select(opp(obs))
                continue
            try:
                sel, _ = rt.mcts_agent(obs, deck, model, opp_deck=aboma)
            except RuntimeError as exc:
                o = to_observation_class(obs)
                print(f"CRASH attempt={attempt} ply={_ply} err={exc}")
                print(f"  context={o.select.context} deck={o.select.deck is not None}")
                print(f"  opts={len(o.select.option)} min={o.select.minCount} max={o.select.maxCount}")
                if o.select.deck:
                    print(f"  deck_ids={[c.id for c in o.select.deck[:4]]}")
                return
            obs = rt.battle_select(sel)
    print("no crash in 500 attempts")


if __name__ == "__main__":
    main()
