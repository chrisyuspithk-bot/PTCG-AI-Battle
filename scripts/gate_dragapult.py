"""Local gate for the standalone Dragapult ex agent (agent/dragapult_agent.py).

Drives the real cg engine with ASYMMETRIC decks: our Dragapult agent on its own
deck vs a baseline pilot (HeuristicScorer / SearchScorer) on each real-field
opponent deck. Seats swap every game to cancel first-player advantage. Reports
win-rate + a Wilson 95% interval per opponent and overall.

This is a LOCAL FILTER, not ladder truth (RULINGS R2/R1): it tells us whether the
agent is broadly competent and lets us compare versions; the Kaggle ladder is the
final judge. The opponent pilot is the strongest brain we can run locally, not the
real ladder agents.

Usage:
  python scripts/gate_dragapult.py --games 30 \
      --opponents real_mega_lucario_ex top_mined_alakazam top_mined_trevenant \
      --opp-scorer heuristic
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from collections import Counter

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE_DIR = os.path.join(PROJ, "data", "sim", "sample_submission")
sys.path.insert(0, ENGINE_DIR)   # import cg
sys.path.insert(0, PROJ)         # import agent.*

from cg import game             # noqa: E402
from cg.sim import lib, Battle   # noqa: E402

DECKS_DIR = os.path.join(PROJ, "agent_decks")
DRAGAPULT_DECK = os.path.join(DECKS_DIR, "dragapult_ex_sample.csv")

RESULT_REASONS = {1: "prize", 2: "deck_out", 3: "no_active", 4: "card_effect"}
MIN_OVERALL_WR = 85.0


def load_deck(path: str) -> list[int]:
    return [int(x) for x in open(path).read().split("\n") if x.strip()][:60]


def _select_player() -> int:
    return lib.GetBattleData(Battle.battle_ptr).selectPlayer


def _wilson(wins: int, n: int) -> tuple[float, float, float]:
    """Return (point%, lo%, hi%) Wilson 95% interval."""
    if n == 0:
        return 0.0, 0.0, 0.0
    z = 1.96
    p = wins / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return 100 * p, 100 * max(0.0, center - half), 100 * min(1.0, center + half)


def make_dragapult():
    # ensure the agent loads the same deck we pass to the engine
    os.environ["DRAGAPULT_DECK"] = DRAGAPULT_DECK
    from agent.dragapult_agent import agent as fn
    return lambda obs: fn(obs)


def make_pilot(scorer_name: str, deck_path: str, seed: int):
    from agent.agent import Agent
    if scorer_name == "search":
        from agent.search_policy import SearchScorer
        ag = Agent(seed=seed, deck_path=deck_path, scorer=SearchScorer())
    else:
        ag = Agent(seed=seed, deck_path=deck_path)
    return lambda obs: ag.act(obs)


def _loss_reason(obs: dict, loser: int) -> str:
    """Infer terminal loss reason for loser seat from final observation."""
    for log in obs.get("logs") or []:
        if log.get("type") == 5:
            reason = int(log.get("reason", 0) or 0)
            return RESULT_REASONS.get(reason, f"reason_{reason}")
    cur = obs.get("current") or {}
    players = cur.get("players") or []
    if loser not in (0, 1) or len(players) < 2:
        return "unknown"
    winner = 1 - loser
    lp = players[loser]
    wp = players[winner]
    if int(lp.get("deckCount", 1) or 0) <= 0:
        return "deck_out"
    w_prizes = len(wp.get("prize") or [])
    l_prizes = len(lp.get("prize") or [])
    if w_prizes < l_prizes or w_prizes == 0:
        return "prize"
    if not (lp.get("active") or []):
        return "no_active"
    return "prize"


def run_game(
    deck0: list[int],
    deck1: list[int],
    pol0,
    pol1,
    max_steps: int = 8000,
) -> tuple[int, str | None]:
    """Return (winner index 0/1/2, loss_reason for loser or None)."""
    obs, start = game.battle_start(deck0, deck1)
    if obs is None:
        raise RuntimeError(f"battle_start failed: err={getattr(start, 'errorType', '?')}")
    policies = (pol0, pol1)
    try:
        for _ in range(max_steps):
            cur = obs["current"]
            if cur is not None and cur.get("result", -1) != -1:
                winner = cur["result"]
                if winner in (0, 1):
                    return winner, _loss_reason(obs, 1 - winner)
                return winner, None
            if obs["select"] is None:
                return -1, None
            p = _select_player()
            choice = policies[p](obs)
            obs = game.battle_select(choice)
        return -1, None
    finally:
        game.battle_finish()


def gate_vs(
    opp_name: str,
    games: int,
    opp_scorer: str,
    loss_reasons: Counter | None = None,
) -> tuple[int, int, int, int]:
    opp_deck_path = os.path.join(DECKS_DIR, opp_name + ".csv")
    deckD = load_deck(DRAGAPULT_DECK)
    deckO = load_deck(opp_deck_path)
    drag = make_dragapult()
    wins = losses = draws = unfinished = 0
    for i in range(games):
        opp = make_pilot(opp_scorer, opp_deck_path, seed=1000 + i)
        if i % 2 == 0:  # Dragapult is player 0
            res, reason = run_game(deckD, deckO, drag, opp)
            d_win, d_loss = (res == 0), (res == 1)
        else:           # Dragapult is player 1
            res, reason = run_game(deckO, deckD, opp, drag)
            d_win, d_loss = (res == 1), (res == 0)
        if res == 2:
            draws += 1
        elif res == -1:
            unfinished += 1
        elif d_win:
            wins += 1
        elif d_loss:
            losses += 1
            if loss_reasons is not None and reason:
                loss_reasons[reason] += 1
    return wins, losses, draws, unfinished


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20, help="games per opponent (seat-swapped)")
    ap.add_argument("--opponents", nargs="+",
                    default=["real_mega_lucario_ex", "top_mined_alakazam", "top_mined_trevenant"],
                    help="opponent deck basenames in agent_decks/")
    ap.add_argument("--opp-scorer", choices=("heuristic", "search"), default="heuristic")
    ap.add_argument(
        "--min-overall-wr",
        type=float,
        default=MIN_OVERALL_WR,
        help=f"Fail if overall win%% below this (default {MIN_OVERALL_WR})",
    )
    ap.add_argument(
        "--allow-no-active",
        action="store_true",
        help="Do not fail when Dragapult loses by no_active (debug only)",
    )
    args = ap.parse_args()

    print(f"Dragapult baseline gate — {args.games} games/opp vs {args.opp_scorer} pilot "
          f"(LOCAL FILTER, not ladder truth)\n")
    tot_w = tot_d = tot_n = 0
    decided_total = 0
    loss_reasons: Counter = Counter()
    for opp in args.opponents:
        w, l, d, u = gate_vs(opp, args.games, args.opp_scorer, loss_reasons)
        decided = w + l
        pt, lo, hi = _wilson(w, decided)
        print(f"  vs {opp:<26} {w:>3}-{l:<3} ({pt:5.1f}%  CI {lo:4.1f}-{hi:4.1f})"
              f"  draws {d} unfinished {u}")
        tot_w += w
        decided_total += decided
        tot_d += d
        tot_n += u
    pt, lo, hi = _wilson(tot_w, decided_total)
    print(f"\n  OVERALL {tot_w}/{decided_total} decided = {pt:.1f}%  (Wilson95 {lo:.1f}-{hi:.1f})"
          f"  | draws {tot_d} unfinished {tot_n}")
    if loss_reasons:
        print(f"  Dragapult loss reasons: {dict(loss_reasons)}")
    no_active = loss_reasons.get("no_active", 0)
    if no_active and not args.allow_no_active:
        print(f"\nGATE FAIL: {no_active} no_active loss(es) — bench guard regression", file=sys.stderr)
        return 1
    if decided_total and pt < args.min_overall_wr:
        print(f"\nGATE FAIL: overall {pt:.1f}% < {args.min_overall_wr}%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
