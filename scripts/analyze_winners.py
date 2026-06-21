#!/usr/bin/env python3
"""Why do the winning agents win? Daily ladder-field analysis.

Reads downloaded episode replays (report/replays/*.json) and answers, with
evidence, what separates winners from losers on the real ladder:

  1. Win-condition mix   — ko_race vs board_wipe vs deck_out
  2. Game length         — turn-count distribution (fast aggro vs grind control)
  3. Archetype win rates — which decks actually win, and by how much
  4. First-player edge   — does going first matter on this field
  5. Archetype matchups  — head-to-head win rates (the meta triangle)

This is the daily lens: we don't copy decks, we learn *why* the field wins and
fold it into the pilot. Run after downloading a daily dump:

    python scripts/analyze_winners.py --replays report/replays --sample 3000
    python scripts/analyze_winners.py            # all files, default dir

Writes a dated report to report/winner_analysis_<YYYYMMDD>.md.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from scripts.mine_episode_replays import _card_names, _archetype  # noqa: E402


def _final_current(data: dict, seat: int):
    try:
        return data["steps"][-1][seat]["observation"]["current"]
    except (KeyError, IndexError, TypeError):
        return None


def _initial_deck(data: dict, seat: int) -> list[int]:
    try:
        action = data["steps"][0][0]["visualize"][0]["action"]
        deck = action[seat]
        return [int(c) for c in deck] if len(deck) == 60 else []
    except (KeyError, IndexError, TypeError, ValueError):
        return []


def _seat_players(cur: dict):
    """Return (winner_self, loser_opp) dicts from the winner-seat's final view."""
    pls = cur.get("players") if isinstance(cur, dict) else None
    if not (isinstance(pls, list) and len(pls) == 2):
        return {}, {}
    yi = cur.get("yourIndex", 0)
    yi = yi if yi in (0, 1) else 0
    return pls[yi], pls[1 - yi]


def _win_condition(win_cur: dict, lose_cur: dict) -> str:
    """Classify how the loser lost, from the winner-seat's final board state.

    prize is an unreliable list (never resolves to 0), so we key off the two
    clean, unambiguous terminal states and treat the rest as the KO/prize race.
    """
    _w, l = _seat_players(win_cur)
    l_deck = l.get("deckCount", -1) if isinstance(l, dict) else -1
    l_active = l.get("active") if isinstance(l, dict) else None
    l_bench = l.get("bench") if isinstance(l, dict) else None
    if isinstance(l_deck, int) and l_deck == 0:
        return "deck_out"           # loser ran out of cards on draw
    if not l_active and not l_bench:
        return "board_wipe"         # loser had no Pokemon left to promote (last KO)
    return "ko_race"                # winner won the prize/KO race (most games)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--replays", default=str(ROOT / "report" / "replays"))
    p.add_argument("--sample", type=int, default=0, help="random subset for speed (0=all)")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)

    files = sorted(Path(args.replays).glob("*.json"))
    if not files:
        print(f"No replays under {args.replays}. Download a daily dump first.")
        return 0
    if args.sample and len(files) > args.sample:
        files = random.Random(args.seed).sample(files, args.sample)

    names = _card_names()
    n = 0
    wincond = Counter()
    turns_all: list[int] = []
    turns_by_cond = defaultdict(list)
    first_wins = 0
    decided = 0
    arch_games = Counter()       # times an archetype appeared
    arch_wins = Counter()        # times it won
    matchup = defaultdict(lambda: [0, 0])  # (archA,archB)->[A_wins, total]

    for fp in files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        rewards = data.get("rewards")
        if not (isinstance(rewards, list) and len(rewards) == 2):
            continue
        try:
            r0, r1 = float(rewards[0]), float(rewards[1])
        except (TypeError, ValueError):
            continue
        if r0 == r1:
            continue  # tie/undecided
        n += 1
        win, lose = (0, 1) if r0 > r1 else (1, 0)
        wc, lc = _final_current(data, win), _final_current(data, lose)
        # archetypes
        dw, dl = _initial_deck(data, win), _initial_deck(data, lose)
        aw = _archetype(dw, names) if dw else "unknown"
        al = _archetype(dl, names) if dl else "unknown"
        arch_games[aw] += 1; arch_games[al] += 1
        arch_wins[aw] += 1
        # symmetric matchup key: track wins for the alphabetically-first archetype.
        # Skip mirrors (a==b): no directional winner, would read a trivial 100%.
        if aw != al:
            a, b = sorted((aw, al))
            m = matchup[(a, b)]
            m[1] += 1                # total games in this pairing
            if aw == a:
                m[0] += 1            # the alphabetically-first archetype won
        # turn count + first-player edge
        cur = wc or lc
        turn = cur.get("turn") if isinstance(cur, dict) else None
        first = cur.get("firstPlayer") if isinstance(cur, dict) else None
        if isinstance(turn, int):
            turns_all.append(turn)
        if first is not None:
            decided += 1
            if first == win:
                first_wins += 1
        # win condition
        cond = _win_condition(wc, lc) if wc and lc else "other"
        wincond[cond] += 1
        if isinstance(turn, int):
            turns_by_cond[cond].append(turn)

    def pct(a, b): return f"{100*a/b:.1f}%" if b else "n/a"
    def med(xs): return sorted(xs)[len(xs)//2] if xs else 0
    def mean(xs): return sum(xs)/len(xs) if xs else 0

    lines = [f"# Why winners win — ladder field analysis ({datetime.now(timezone.utc):%Y-%m-%d})",
             "", f"Decided games analyzed: **{n}** (from {len(files)} replays)", ""]

    lines += ["## 1. Win-condition mix (how the loser lost)", ""]
    for c, k in wincond.most_common():
        lines.append(f"- **{c}**: {pct(k, n)} ({k})  — median {med(turns_by_cond[c])} turns")
    st = sorted(turns_all)
    lines += ["", "## 2. Game length", "",
              f"- median **{med(turns_all)}** turns, mean **{mean(turns_all):.1f}**, "
              f"p10 {st[len(st)//10] if st else 0} / p90 {st[9*len(st)//10] if st else 0}"]

    lines += ["", "## 3. First-player edge", "",
              f"- winner went first in **{pct(first_wins, decided)}** of decided games "
              f"({first_wins}/{decided})"]

    lines += ["", "## 4. Archetype win rates (appearances >= 20)", "",
              "| archetype | games | win rate |", "|---|---|---|"]
    for a, g in arch_games.most_common():
        if g >= 20:
            lines.append(f"| {a} | {g} | {pct(arch_wins[a], g)} |")

    lines += ["", "## 5. Archetype matchups (>= 15 games)", "",
              "| archetype A | vs B | games | A win rate |", "|---|---|---|---|"]
    big = sorted(((k, v) for k, v in matchup.items() if v[1] >= 15),
                 key=lambda kv: -kv[1][1])[:18]
    for (a, b), (w, t) in big:
        tag = "  <-- skew" if t and abs(w / t - 0.5) > 0.15 else ""
        lines.append(f"| {a} | {b} | {t} | {pct(w, t)}{tag} |")

    out = ROOT / "report" / f"winner_analysis_{datetime.now(timezone.utc):%Y%m%d}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
