"""Summarize Archaludon submission replay indices for cross-ref comparison."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS = [
    ("54083197", "R7 champion", "archaludon", 1196.1),
    ("54088877", "R8a+R8b probe", "archaludon_r8", 983.8),
    ("54089078", "R8+R9 probe", "archaludon_r9", 841.0),
]


def load_index(name: str) -> dict:
    return json.loads((ROOT / "report" / "submission_replays" / name / "index.json").read_text())


def summarize(ref: str, label: str, pkg: str, mu: float) -> dict:
    idx = load_index(pkg)
    eps = idx["episodes"]
    by_arch: dict[str, list[str]] = defaultdict(list)
    loss_reasons = Counter()
    win_turns, loss_turns = [], []

    for e in eps:
        arch = e.get("opponent_archetype") or "unknown"
        by_arch[arch].append(e["outcome"])
        if e["outcome"] == "loss":
            loss_reasons[e["result_reason"]] += 1
            loss_turns.append(e["turn_count"])
        else:
            win_turns.append(e["turn_count"])

    arch_rows = []
    for arch, outcomes in sorted(by_arch.items(), key=lambda x: -len(x[1])):
        w = sum(1 for o in outcomes if o == "win")
        n = len(outcomes)
        arch_rows.append((arch, w, n - w, 100 * w / n if n else 0, n))

    return {
        "ref": ref,
        "label": label,
        "mu": mu,
        "total": len(eps),
        "wins": idx["wins"],
        "losses": idx["losses"],
        "wr": idx.get("win_rate_pct", 0),
        "loss_reasons": dict(loss_reasons),
        "win_turns": win_turns,
        "loss_turns": loss_turns,
        "arch_rows": arch_rows,
    }


def main() -> None:
    summaries = [summarize(*r) for r in REFS]
    print("=" * 72)
    print("ARCHALUDON EPISODE SUMMARY (public ladder games)")
    print("=" * 72)
    for s in summaries:
        print(f"\n## {s['ref']} · {s['label']} · μ={s['mu']}")
        print(f"   {s['wins']}W / {s['losses']}L = {s['wr']:.1f}%  (n={s['total']})")
        print(f"   Loss reasons: {s['loss_reasons']}")
        wt, lt = s["win_turns"], s["loss_turns"]
        if wt:
            print(f"   Win turns:  avg={sum(wt)/len(wt):.1f}  med={sorted(wt)[len(wt)//2]}")
        if lt:
            print(f"   Loss turns: avg={sum(lt)/len(lt):.1f}  med={sorted(lt)[len(lt)//2]}")
        print("   By opponent archetype:")
        for arch, w, l, wr, n in s["arch_rows"]:
            print(f"     {arch:12} {w:2}W {l:2}L  {wr:5.1f}%  n={n}")

    print("\n" + "=" * 72)
    print("CROSS-REF: loss reason rates")
    print("=" * 72)
    for s in summaries:
        na = s["loss_reasons"].get("no_active", 0)
        pr = s["loss_reasons"].get("prize", 0)
        do = s["loss_reasons"].get("deck_out", 0)
        n = s["total"]
        print(
            f"  {s['ref']}: no_active {na}/{n} ({100*na/n:.1f}%)  "
            f"prize {pr}/{n} ({100*pr/n:.1f}%)  deck_out {do}/{n}"
        )


if __name__ == "__main__":
    main()
