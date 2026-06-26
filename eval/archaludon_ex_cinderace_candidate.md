# Archaludon ex / Cinderace — ported (R7 bench guard only)

**Status:** **Ladder probe submitted** ref **54083197** (2026-06-26) — await μ readings.  
**Delta vs public v5:** R7 empty-bench guard only (`agent/archaludon_bench_guard.py` — Duraludon → Relicanth priority). No prize-KO or deck tweaks.

---

## Source

Public Kaggle community share (2026-06-26, **v5**). Rule-based only — no ML.

| Field | Value |
|-------|-------|
| **Brain** | `agent/archaludon_agent.py` (community v5 + never-crash wrapper + bench guard) |
| **Deck** | `agent_decks/archaludon_ex_cinderace.csv` (public list, unchanged) |
| **Reference** | `notebooks/archaludon_ex_cinderace/archaludon_agent_public.py` |
| **Package** | `python scripts/package_archaludon.py` → `dist/candidates/archaludon_ex_cinderace_r7_bench.tar.gz` |

---

## Local gate (native full suite, n=30)

Full report: [`gate_archaludon.md`](gate_archaludon.md)

| Opponent | WR% | Record |
|----------|-----|--------|
| dragapult_ex_sample | 73.3 | W22/L8 |
| real_mega_abomasnow_ex | 66.7 | W20/L10 |
| real_iono | 43.3 | W13/L17 |
| real_dragapult_ex | 86.7 | W26/L4 |
| real_mega_lucario_ex | 93.3 | W28/L2 |

**Overall: 72.7%** [65.0, 79.2] (n=150) — filter only; ladder μ unknown.

Bench guard alone vs public v5 reference on same harness ≈ **74.0%** (within n=30 noise). Broader prize-KO scoring was tried and **regressed** — ruled out for now.

---

## Rebuild

```powershell
python scripts/bootstrap_archaludon.py   # after reference updates
python scripts/gate_archaludon.py --games 30 --suite full --report
python scripts/package_archaludon.py
python scripts/check_upload_eligible.py --manifest dist/candidates/archaludon_ex_cinderace_r7_bench.manifest.json `
  --change "Archaludon v5 + R7 bench guard" --local-gate 72.7
```

**Upload:** new brain×deck row (R12 OK). Gate vs **660.5 μ** Search bar before treating as home-grown progress.

---

## Future (optional)

- Deck list tweaks (trainer counts, Relicanth slot)
- Matchup levers if harness shows >5pp on one archetype
- Ladder probe when upload slot available
