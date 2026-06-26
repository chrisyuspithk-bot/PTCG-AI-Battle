"""Measure eval losses: clock forfeit vs board loss (mirrors train_lucario_field_mcts.eval_matchup)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch

import agent.lucario_mcts_runtime as rt
from agent.native_opponent import make_opponent_brain

DECK_PATH = ROOT / "agent_decks/real_mega_lucario_ex.csv"
OPPONENTS = [
    ("real_dragapult_ex", ROOT / "agent_decks/real_dragapult_ex.csv"),
    ("real_mega_abomasnow_ex", ROOT / "agent_decks/real_mega_abomasnow_ex.csv"),
    ("real_iono", ROOT / "agent_decks/real_iono.csv"),
]


def load_deck(p: Path) -> list[int]:
    return [int(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def eval_instrumented(
    deck,
    opp_deck,
    opp_move,
    model,
    games: int,
    *,
    opp_name: str,
    use_clock: bool,
    device,
) -> dict:
    stats = {
        "wins": 0,
        "board_losses": 0,
        "we_timeout": 0,
        "opp_timeout": 0,
        "draws": 0,
        "max_clock_us": 0.0,
        "max_clock_opp": 0.0,
        "max_plies": 0,
        "max_our_mcts_sec": 0.0,
        "total_our_mcts_sec": 0.0,
        "our_turns": 0,
    }
    model.eval()
    with torch.inference_mode():
        for i in range(games):
            your_index = i % 2
            decks = (deck, opp_deck) if your_index == 0 else (opp_deck, deck)
            obs, start = rt.battle_start(*decks)
            if start.errorPlayer >= 0:
                raise ValueError(f"deck error {start.errorType}")
            clock = rt.PlayerClock() if use_clock else None
            forfeit_result = None
            plies = 0
            while obs["current"]["result"] < 0 and forfeit_result is None:
                yi = obs["current"]["yourIndex"]
                if yi == your_index:
                    t0 = time.perf_counter()
                    if clock is not None:
                        selected, _, forfeit_result = rt.timed_mcts(
                            rt.mcts_agent, obs, clock, yi, deck, model, opp_deck=opp_deck,
                        )
                    else:
                        selected, _ = rt.mcts_agent(obs, deck, model, opp_deck=opp_deck)
                    dt = time.perf_counter() - t0
                    stats["total_our_mcts_sec"] += dt
                    stats["our_turns"] += 1
                    stats["max_our_mcts_sec"] = max(stats["max_our_mcts_sec"], dt)
                else:
                    if clock is not None:
                        selected, forfeit_result = rt.timed_act(opp_move, obs, clock, yi)
                    else:
                        selected = opp_move(obs)
                if forfeit_result is None:
                    obs = rt.battle_select(selected)
                plies += 1
            rt.battle_finish()
            if clock is not None:
                stats["max_clock_us"] = max(stats["max_clock_us"], clock.used[your_index])
                stats["max_clock_opp"] = max(
                    stats["max_clock_opp"], clock.used[1 - your_index],
                )
            stats["max_plies"] = max(stats["max_plies"], plies)

            if forfeit_result is not None:
                if forfeit_result == your_index:
                    stats["we_timeout"] += 1
                else:
                    stats["opp_timeout"] += 1
                    stats["wins"] += 1
            else:
                r = obs["current"]["result"]
                if r == 2:
                    stats["draws"] += 1
                elif r == your_index:
                    stats["wins"] += 1
                else:
                    stats["board_losses"] += 1
    return stats


def main() -> None:
    deck = load_deck(DECK_PATH)
    rt.set_field_training_flags(player_clock=True, deck_scope=True)
    rt.set_lucario_lever_teaching(str(DECK_PATH), blend=0.45)
    rt.SEARCH_COUNT = 20

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = rt.MyModel(rt.D_MODEL, rt.NUM_HEADS, rt.D_FF, rt.ENC_LAYERS, rt.DEC_LAYERS).to(device)
    model.eval()
    print(f"device={device} clock={rt.PLAYER_CLOCK_LIMIT_SEC}s enabled={rt.PLAYER_CLOCK_ENABLED}")
    print(f"search={rt.SEARCH_COUNT} games_per_opp=20 (same as eval)\n")

    for opp_name, opp_path in OPPONENTS:
        opp_deck = load_deck(opp_path)
        opp_move, label = make_opponent_brain(
            "native", str(opp_path), opp_deck, opp_name=opp_name,
        )
        for clock_on in (True, False):
            s = eval_instrumented(
                deck, opp_deck, opp_move, model, 20,
                opp_name=opp_name, use_clock=clock_on, device=device,
            )
            wr = 100.0 * s["wins"] / 20
            tag = "CLOCK ON" if clock_on else "CLOCK OFF"
            avg_mcts = (
                s["total_our_mcts_sec"] / s["our_turns"] if s["our_turns"] else 0.0
            )
            est_our_turns_to_cliff = (
                rt.PLAYER_CLOCK_LIMIT_SEC / avg_mcts if avg_mcts > 0 else float("inf")
            )
            print(f"--- {opp_name} ({label}) [{tag}] ---")
            print(
                f"  W={s['wins']} board_L={s['board_losses']} "
                f"we_timeout={s['we_timeout']} opp_timeout={s['opp_timeout']} D={s['draws']} "
                f"-> WR={wr:.0f}%"
            )
            print(
                f"  max_clock us/opp={s['max_clock_us']:.1f}/{s['max_clock_opp']:.1f}s "
                f"max_plies={s['max_plies']} avg_mcts={avg_mcts*1000:.0f}ms "
                f"max_mcts={s['max_our_mcts_sec']*1000:.0f}ms "
                f"est_our_turns_to_599s={est_our_turns_to_cliff:.0f}"
            )
            print()


if __name__ == "__main__":
    main()
