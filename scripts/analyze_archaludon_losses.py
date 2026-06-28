"""Offline DS on Archaludon ladder episodes — loss patterns for brain refinement."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = [
    ("54083197", "champion R7", "archaludon"),
    ("54088877", "R8a+R8b", "archaludon_r8"),
    ("54089078", "R8+R9", "archaludon_r9"),
]


def wr_by_arch(idx: dict) -> list[tuple]:
    by: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for e in idx["episodes"]:
        a = e.get("opponent_archetype") or "unknown"
        if e["outcome"] == "win":
            by[a][0] += 1
        else:
            by[a][1] += 1
    rows = []
    for a, (w, l) in by.items():
        n = w + l
        rows.append((a, w, l, 100 * w / n, n))
    return sorted(rows, key=lambda x: -x[4])


def prize_patterns(deck_dir: Path, prize_ids: list[str]) -> Counter:
    c: Counter = Counter()
    for eid in prize_ids:
        p = deck_dir / f"{eid}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        turns = d.get("turns") or []
        if not turns:
            continue
        us_p = turns[-1]["us"].get("prize_remaining")
        opp_p = turns[-1]["opponent_visible"].get("prize_remaining")
        if us_p is not None and opp_p is not None:
            if us_p > opp_p:
                c["behind_in_prize_race"] += 1
            elif us_p == opp_p:
                c["tied_at_loss"] += 1
            else:
                c["ahead_but_lost"] += 1
        for t in reversed(turns[-10:]):
            ctx = (t.get("select") or {}).get("context")
            chosen = t.get("chosen_options") or []
            if ctx != 0 or not chosen:
                continue
            t0 = chosen[0].get("type")
            if t0 == 14:
                c["ended_turn_late"] += 1
            elif t0 == 13:
                c["attacked_late"] += 1
            elif t0 == 1:
                c["played_card_late"] += 1
            break
    return c


def main() -> None:
    print("=" * 70)
    print("ARCHALUDON LOSS ANALYSIS")
    print("=" * 70)
    for ref, label, pkg in REFS:
        idx = json.loads((ROOT / "report/submission_replays" / pkg / "index.json").read_text())
        losses = json.loads((ROOT / "report/submission_replays" / pkg / "losses.json").read_text())["losses"]
        n = idx["episodes_total"]
        lr = idx.get("loss_reasons", {})
        print(f"\n## {ref} {label}  WR={idx['win_rate_pct']}%  n={n}")
        print(f"   Loss reasons: {lr}")
        print(f"   no_active: {100*lr.get('no_active',0)/n:.1f}%   prize: {100*lr.get('prize',0)/n:.1f}%")
        print("   WR by archetype (n>=3):")
        for a, w, l, wr, n2 in wr_by_arch(idx):
            if n2 < 3:
                continue
            flag = "  <<< weak" if wr < 50 else ""
            print(f"     {a:12} {w}W {l}L  {wr:5.1f}%  n={n2}{flag}")

    losses = json.loads((ROOT / "report/submission_replays/archaludon/losses.json").read_text())["losses"]
    prize_ids = [x["episode_id"] for x in losses if x["result_reason"] == "prize"]
    pat = prize_patterns(ROOT / "report/deck_logs/archaludon", prize_ids)
    print("\n" + "=" * 70)
    print("CHAMPION PRIZE-LOSS PATTERNS (n=10)")
    print("=" * 70)
    for k, v in pat.most_common():
        print(f"  {k}: {v}")

    print("\nCHAMPION no_active (n=4):")
    for x in losses:
        if x["result_reason"] != "no_active":
            continue
        eid = x["episode_id"]
        d = json.loads((ROOT / f"report/deck_logs/archaludon/{eid}.json").read_text())
        turns = d.get("turns") or []
        bench0 = sum(1 for t in turns if t.get("us", {}).get("bench_count") == 0)
        print(f"  {eid} vs {x.get('opponent_archetype','?')} t={x['turn_count']} "
              f"bench0_steps={bench0} terminal_bench={x.get('terminal_bench')}")


def prize_loss_decisions(deck_dir: Path, prize_ids: list[str]) -> None:
    print("\nPRIZE LOSS — last 5 our-turn snapshots:")
    for eid in prize_ids:
        d = json.loads((deck_dir / f"{eid}.json").read_text())
        meta = next(
            (x for x in json.loads((deck_dir / "losses.json").read_text())["losses"]
             if x["episode_id"] == eid),
            {},
        )
        print(f"\n  {eid} vs {meta.get('opponent_archetype', '?')} t={meta.get('turn_count')}")
        for t in (d.get("turns") or [])[-5:]:
            sel = t.get("select") or {}
            chosen = t.get("chosen_options") or []
            us = t.get("us") or {}
            opp = t.get("opponent_visible") or {}
            c0 = chosen[0].get("type") if chosen else None
            print(
                f"    step={t['step']} ctx={sel.get('context')} "
                f"us_p={us.get('prize_remaining')} opp_p={opp.get('prize_remaining')} "
                f"bench={us.get('bench_count')} chosen={c0}"
            )


def alakazam_games(idx_path: Path) -> None:
    idx = json.loads(idx_path.read_text())
    print("\nALAKAZAM MATCHUP (champion):")
    for e in idx["episodes"]:
        if e.get("opponent_archetype") != "alakazam":
            continue
        print(
            f"  {e['episode_id']} {e['outcome']:4} "
            f"reason={e.get('result_reason', '?')} t={e.get('turn_count')}"
        )


if __name__ == "__main__":
    main()
    losses = json.loads(
        (ROOT / "report/submission_replays/archaludon/losses.json").read_text()
    )["losses"]
    prize_ids = [x["episode_id"] for x in losses if x["result_reason"] == "prize"]
    prize_loss_decisions(ROOT / "report/deck_logs/archaludon", prize_ids)
    alakazam_games(ROOT / "report/submission_replays/archaludon/index.json")
