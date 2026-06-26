"""One-off: parse lucarioex_v5_field train.log into summary tables."""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "rl_mcts_field/lucarioex_v5_field/train.log"
METRICS = ROOT / "rl_mcts_field/lucarioex_v5_field/metrics.csv"
OUT = ROOT / "report/eval/lucarioex_v5_training_data.csv"

eval_re = re.compile(
    r"\[cycle (\d+)\] eval (\S+) \([^)]+\): ([\d.]+)% \(W(\d+)/L(\d+)/D(\d+)\)"
)
train_re = re.compile(
    r"\[cycle (\d+)\] loss=([\d.]+) field_wr=([\d.]+)% vs_champ=([\d.]+)% "
    r"promoted=(\d) champ_eval=([\d.]+)% best_field=([\d.]+)% samples=(\d+)"
)

log = LOG.read_text(encoding="utf-8", errors="replace")
evals: dict[int, dict[str, dict]] = defaultdict(dict)
trains: dict[int, dict] = {}

for line in log.splitlines():
    m = eval_re.search(line)
    if m:
        c, opp, wr, w, l, d = m.groups()
        evals[int(c)][opp] = {
            "wr": float(wr), "w": int(w), "l": int(l), "d": int(d),
        }
    m = train_re.search(line)
    if m:
        c = int(m.group(1))
        trains[c] = {
            "loss": float(m.group(2)),
            "field_wr": float(m.group(3)),
            "vs_champ": float(m.group(4)),
            "promoted": int(m.group(5)),
            "champ_eval": float(m.group(6)),
            "best_field": float(m.group(7)),
            "samples": int(m.group(8)),
        }

all_cycles = sorted(set(evals) | set(trains))
rows: list[dict] = []
for c in all_cycles:
    t = trains.get(c, {})
    for opp, ev in sorted(evals.get(c, {}).items()):
        rows.append({
            "cycle": c,
            "opponent": opp,
            "phase": "eval",
            "wins": ev["w"],
            "losses": ev["l"],
            "draws": ev["d"],
            "wr_pct": ev["wr"],
            "loss": "",
            "promoted": t.get("promoted", ""),
            "champ_eval_pct": t.get("champ_eval", ""),
            "field_gate_pct": t.get("field_wr", ""),
            "best_field_pct": t.get("best_field", ""),
            "train_loss": t.get("loss", ""),
            "samples": t.get("samples", ""),
        })
    if t:
        rows.append({
            "cycle": c,
            "opponent": "ALL",
            "phase": "train",
            "wins": "", "losses": "", "draws": "",
            "wr_pct": t.get("champ_eval", ""),
            "loss": t.get("loss", ""),
            "promoted": t.get("promoted", ""),
            "champ_eval_pct": t.get("champ_eval", ""),
            "field_gate_pct": t.get("field_wr", ""),
            "best_field_pct": t.get("best_field", ""),
            "train_loss": t.get("loss", ""),
            "samples": t.get("samples", ""),
        })

OUT.parent.mkdir(parents=True, exist_ok=True)
fields = list(rows[0].keys()) if rows else []
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

print(f"wrote {OUT} ({len(rows)} rows)")
print(f"cycles: {min(all_cycles)}-{max(all_cycles)} ({len(all_cycles)} cycles with data)")
print("\nTRAIN SUMMARY:")
print("cycle,champ_eval,field_gate,best_field,promoted,loss,samples")
for c in all_cycles:
    t = trains.get(c)
    if t:
        print(
            f"{c},{t['champ_eval']},{t['field_wr']},{t['best_field']},"
            f"{t['promoted']},{t['loss']},{t['samples']}"
        )

opps = sorted({o for c in evals for o in evals[c]})
print("\nMEAN EVAL BY OPPONENT:")
for opp in opps:
    vals = [evals[c][opp]["wr"] for c in evals if opp in evals[c]]
    print(
        f"{opp:32} n={len(vals):2} mean={sum(vals)/len(vals):5.1f}% "
        f"min={min(vals):4.1f}% max={max(vals):4.1f}%"
    )
