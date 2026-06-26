"""One-off analysis for Dragapult ref 53950779 ladder episodes."""
from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = "53950779"
STATS = ROOT / "report" / "submission_stats" / f"{REF}_stats.csv"
REPLAYS = ROOT / "report" / "replays"


def terminal_state(data: dict) -> tuple[int, dict | None]:
    best_turn, best = -1, None
    for step in data.get("steps") or []:
        if not isinstance(step, list):
            continue
        for ps in step:
            obs = (ps.get("observation") or ps) if isinstance(ps, dict) else {}
            cur = obs.get("current") or {}
            t = int(cur.get("turn", 0) or 0)
            if t >= best_turn and int(cur.get("result", -1)) != -1:
                best_turn, best = t, cur
    return best_turn, best


def opp_agent(data: dict, opp_idx: int) -> dict:
    agents = (data.get("info") or {}).get("Agents") or []
    return agents[opp_idx] if opp_idx < len(agents) else {}


def main() -> None:
    rows = list(csv.DictReader(STATS.open(encoding="utf-8")))
    print("=== NO_ACTIVE LOSSES ===")
    for s in rows:
        if s["result_reason"] != "no_active":
            continue
        data = json.loads((REPLAYS / f"{s['episode_id']}.json").read_text(encoding="utf-8"))
        turn, cur = terminal_state(data)
        our = int(s["agent_index"])
        ps = (cur or {}).get("players", [{}, {}])[our]
        oa = opp_agent(data, 1 - our)
        print(
            s["episode_id"],
            f"turn={turn}",
            f"bench={len(ps.get('bench') or [])}",
            f"hand={len(ps.get('hand') or [])}",
            f"prize={len(ps.get('prize') or [])}",
            f"deck={ps.get('deckCount')}",
        )
        print(f"  opp: {oa.get('Name', oa)}")

    print("\n=== OPPONENT AGENTS ===")
    for s in rows:
        data = json.loads((REPLAYS / f"{s['episode_id']}.json").read_text(encoding="utf-8"))
        info = data.get("info") or {}
        our = int(s["agent_index"])
        opp = 1 - our
        oa = opp_agent(data, opp)
        team = (info.get("TeamNames") or ["?", "?"])[opp]
        name = oa.get("Name") or oa.get("SubmissionFileName") or "?"
        print(f"{s['outcome']:4s} t={s['turn_count']:>2s} {team[:22]:22s} {str(name)[:55]}")

    print("\n=== μ IMPLICATION (21 public games) ===")
    w = sum(1 for s in rows if s["outcome"] == "win")
    print(f"W/L {w}/{len(rows)-w} = {100*w/len(rows):.1f}% episode WR")
    print("Loss reasons:", Counter(s["result_reason"] for s in rows if s["outcome"] == "loss"))


if __name__ == "__main__":
    main()
