"""Repro: cycle-2 collect vs real_mega_abomasnow_ex after checkpoint (matches crash site)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch

import agent.lucario_mcts_runtime as rt
from agent.native_opponent import make_opponent_brain
from scripts.train_lucario_field_mcts import collect_vs_opponent

WORK = ROOT / "rl_mcts_field/lucarioex_v5_field"
DECK_PATH = ROOT / "agent_decks/real_mega_lucario_ex.csv"
OPP_PATH = ROOT / "agent_decks/real_mega_abomasnow_ex.csv"


def main() -> None:
    deck = [int(x) for x in DECK_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    opp_deck = [int(x) for x in OPP_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    rt.set_field_training_flags(player_clock=True, deck_scope=True)
    rt.set_lucario_lever_teaching(str(DECK_PATH), blend=0.45)
    rt.SEARCH_COUNT = 20

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = rt.MyModel(rt.D_MODEL, rt.NUM_HEADS, rt.D_FF, rt.ENC_LAYERS, rt.DEC_LAYERS).to(device)
    ckpt = WORK / "model_latest.pth"
    model.load_state_dict(torch.load(ckpt, map_location=device, weights_only=True))
    model.eval()

    opp_move, label = make_opponent_brain(
        "native", str(OPP_PATH), opp_deck, opp_name="real_mega_abomasnow_ex",
    )
    print(f"repro collect vs {label} from {ckpt.name} (30g)...")
    got = collect_vs_opponent(
        deck, opp_deck, opp_move, model, 30, opp_name="real_mega_abomasnow_ex",
    )
    print(f"OK samples={len(got)}")


if __name__ == "__main__":
    main()
