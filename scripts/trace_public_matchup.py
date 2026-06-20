"""Trace one candidate-vs-public-agent game at decision checkpoints.

This is for diagnosis, not scoring. It prints compact board state whenever the
candidate is asked to choose, then reports the final simulator result.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.gate_vs_public import load_agent  # noqa: E402

ENGINE_DIR = ROOT / "data" / "sim" / "sample_submission"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from cg.api import AreaType, OptionType, SelectContext, to_observation_class  # noqa: E402
from cg.game import battle_finish, battle_select, battle_start  # noqa: E402


def _pokemon_summary(p) -> str:
    if p is None:
        return "-"
    return f"{p.id}:hp{p.hp}:e{len(p.energies)}"


def _player_summary(player) -> str:
    active = _pokemon_summary(player.active[0]) if player.active else "-"
    bench = ",".join(_pokemon_summary(p) for p in player.bench) or "-"
    hand = len(player.hand) if player.hand is not None else getattr(player, "handCount", "?")
    prize = len(player.prize) if player.prize is not None else "?"
    return f"A[{active}] B[{bench}] hand={hand} deck={player.deckCount} prize={prize}"


def _context_name(ctx) -> str:
    try:
        return SelectContext(ctx).name
    except Exception:
        return str(ctx)


def _option_summary(obc, opt) -> str:
    try:
        typ = OptionType(opt.type).name
    except Exception:
        typ = str(opt.type)
    bits = [typ]
    if opt.type == OptionType.ATTACK:
        bits.append(f"attack={opt.attackId}")
    if opt.type in (OptionType.PLAY, OptionType.DISCARD):
        card = obc.current.players[obc.current.yourIndex].hand[opt.index]
        bits.append(f"hand[{opt.index}]={card.id}")
    if opt.type in (OptionType.ATTACH, OptionType.EVOLVE):
        card = obc.current.players[obc.current.yourIndex].hand[opt.index]
        area = "A" if opt.inPlayArea == AreaType.ACTIVE else "B"
        bits.append(f"hand[{opt.index}]={card.id}->{area}{opt.inPlayIndex}")
    if opt.type == OptionType.CARD:
        bits.append(f"area={opt.area} idx={opt.index} p={opt.playerIndex}")
        card = _card_for_option(obc, opt)
        if card is not None:
            bits.append(f"card={card.id}")
    return " ".join(bits)


def _card_for_option(obc, opt):
    pidx = opt.playerIndex if opt.playerIndex is not None else obc.current.yourIndex
    if not (0 <= pidx < len(obc.current.players)):
        return None
    player = obc.current.players[pidx]
    idx = opt.index or 0
    if opt.area == AreaType.HAND:
        return player.hand[idx] if 0 <= idx < len(player.hand) else None
    if opt.area == AreaType.ACTIVE:
        return player.active[idx] if 0 <= idx < len(player.active) else None
    if opt.area == AreaType.BENCH:
        return player.bench[idx] if 0 <= idx < len(player.bench) else None
    if opt.area == AreaType.DISCARD:
        return player.discard[idx] if 0 <= idx < len(player.discard) else None
    if opt.area == AreaType.DECK and obc.select.deck:
        return obc.select.deck[idx] if 0 <= idx < len(obc.select.deck) else None
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent", required=True)
    ap.add_argument("--opponent", required=True)
    ap.add_argument("--candidate-seat", type=int, choices=(0, 1), default=0)
    ap.add_argument("--max-steps", type=int, default=6000)
    ap.add_argument("--max-lines", type=int, default=120)
    args = ap.parse_args(argv)

    stack: list[str] = []
    candidate, candidate_deck, candidate_label = load_agent(Path(args.agent), stack)
    opponent, opponent_deck, opponent_label = load_agent(Path(args.opponent), stack)

    if args.candidate_seat == 0:
        agents = [candidate, opponent]
        decks = [candidate_deck, opponent_deck]
    else:
        agents = [opponent, candidate]
        decks = [opponent_deck, candidate_deck]

    obs = None
    lines = 0
    try:
        obs, start = battle_start(decks[0], decks[1])
        if obs is None or start.errorPlayer >= 0:
            print(f"battle_start failed: errorPlayer={getattr(start, 'errorPlayer', '?')}")
            return 1

        for step in range(args.max_steps + 1):
            obc = to_observation_class(obs)
            if obc.current.result >= 0:
                print(f"FINAL result={obc.current.result} step={step}")
                print(f"candidate={candidate_label} seat={args.candidate_seat}; opponent={opponent_label}")
                return 0

            current_player = obc.current.yourIndex
            is_candidate = current_player == args.candidate_seat
            if is_candidate and lines < args.max_lines:
                me = obc.current.players[args.candidate_seat]
                opp = obc.current.players[1 - args.candidate_seat]
                sel = obc.select
                print(
                    f"step={step} turn={obc.current.turn} ctx={_context_name(sel.context)} "
                    f"type={sel.type} opts={len(sel.option)}"
                )
                print(f"  us : {_player_summary(me)}")
                print(f"  opp: {_player_summary(opp)}")
                lines += 3

            action = agents[current_player](obs)
            if is_candidate and lines < args.max_lines:
                chosen = []
                for idx in action:
                    if 0 <= idx < len(obc.select.option):
                        chosen.append(f"{idx}:{_option_summary(obc, obc.select.option[idx])}")
                    else:
                        chosen.append(f"{idx}:OUT_OF_RANGE")
                print(f"  action={action} {'; '.join(chosen)}")
                lines += 1
            obs = battle_select(action)

        print(f"FINAL unfinished step>{args.max_steps}")
        return 1
    finally:
        if obs is not None:
            battle_finish()
        for tmp in stack:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
