# STATE — current state & the single next action

> **Mindset:** `RULINGS.md` Part 0 · **Plan:** `ROADMAP.md` · **Upload gate:** `scripts/check_upload_eligible.py --suggest`

---

## As of 2026-06-26 (Session 51 — Starmie upload)

### Submitted

| Field | Value |
|-------|-------|
| **Ref** | **54083513** (PENDING) |
| **Package** | `starmie_froslass_ashleysandlin.tar.gz` |
| **Brain × deck** | `starmie_rules` × `starmie_froslass_ashleysandlin.csv` |
| **Local gate** | Mirror **56.7%** n=30; full suite **9.3%** (filter only) |
| **R12** | New catalog row — exit 0 |

**Next:** `python scripts/track_ladder.py` after COMPLETE; ≥2 μ readings ≥40 min apart.

---

## As of 2026-06-26 (Session 51 — execute batch)

### Delivered this run

| Item | Result |
|------|--------|
| **Starmie / Froslass field opponent** | `agent/starmie_agent.py`, deck, `PrizeTracker`, `scripts/gate_starmie.py`; mirror **56.7%** n=30 (`eval/gate_starmie_session51.md`) |
| **SearchScorer stability fix** | Refresh `Battle.battle_ptr` each search (was crashing full-suite gate); re-gate **26.7%** n=30 (`eval/gate_search.md`) |
| **PrizeTracker → SearchScorer** | Deck-search contexts penalize inferred prized cards |
| **Archaludon ladder** | Ref **54083197** **COMPLETE** μ=**600.0** (first reading — wait ≥40 min for 2nd) |
| **verify_official_opponents** | 12 decks OK including `starmie_froslass_ashleysandlin` |

### THE SINGLE NEXT ACTION

**Track Starmie ref 54083513** + **Archaludon ref 54083197** (2nd reading **731.3 μ**) — `python scripts/track_ladder.py` after ≥40 min.

---

## As of 2026-06-26 (Session 51 — Archaludon ladder probe)

### Ladder probe submitted

| Field | Value |
|-------|-------|
| **Ref** | **54083197** |
| **Package** | `archaludon_ex_cinderace_r7_bench.tar.gz` |
| **Brain × deck** | `archaludon_rules` × `archaludon_ex_cinderace.csv` |
| **Delta** | Community v5 + R7 empty-bench guard only |
| **Local gate** | **72.7%** full suite n=30 (`eval/gate_archaludon.md`) |
| **Status** | **COMPLETE** μ=**600.0** (2026-06-26 16:19 UTC) — await 2nd reading |

**Next:** `python scripts/track_ladder.py` ≥40 min after first COMPLETE before treating 600 as stable.

---

## As of 2026-06-26 (Session 51 — Alakazam iteration)

### Measured

| Item | Result |
|------|--------|
| Alakazam bench guard A/B @ n=50 | Guard **regresses** (53.6% vs 56.8%) → **default OFF** |
| Dragapult levers on Alakazam | **58.7%** @ n=30 → **reverted** (hurt Lucario/Iono) |
| Latest gate (notebook deck, n=30) | **54.0%** (variance; S50 **62.0%** still reference) |
| Dragapult stack | Unchanged — full guard + Crispin rules; **880.9 μ** hold |

Full write-up: `eval/alakazam_iteration_session51.md`

### THE SINGLE NEXT ACTION

**Replay analysis** — Alakazam losses vs `dragapult_ex_sample` (stable ~33–37% weakness). No Kaggle upload until **two** n=30 gates ≥62% or paired n=50 beat baseline.

---

### Ladder truth

| Rank | Brain × deck | μ | Ref |
|-----:|--------------|----:|-----|
| 1 | dragapult_crispin + R7 × `dragapult_ex_sample` | **880.9** | 53989933 |
| 2 | SearchScorer × `real_mega_lucario_ex` | **660.5** | 53869254 |
| 3 | imported Alakazam best5 | **659.0** | 53913404 |
| 4 | basic MCTS model4 × Lucario | **651.3** | 53946742 |

**Bar:** **880.9 μ**. **R12:** no duplicate uploads — iterate or don't upload.

### Session 50 delivered

| Item | Status |
|------|--------|
| B1 Alakazam port | `agent/alakazam_agent.py`, package, gate **62.0%** @ n=30 |
| R12 + `check_upload_eligible.py` | Blocks ports, weak local gates (<55%), duplicates |
| Native Alakazam opponents | `top_mined_alakazam` + `ryotasueyoshi_alakazam_best5` in official registry |
| LucarioScorer gate @ n=30 | **39.3%** — **do not upload** (`eval/lucario_scorer_baseline_session50.md`) |
| Duplicate Alakazam upload | Wasted slot — lesson in R12 |

### Session 50 measurements (native field full suite n=30)

| Brain | Deck | Overall WR | Report |
|-------|------|------------|--------|
| SearchScorer | `real_mega_lucario_ex` | **27.3%** | `eval/gate_search.md` |
| LucarioScorer | same | **39.3%** | `eval/lucario_scorer_baseline_session50.md` |
| Alakazam best5 | notebook deck | **62.0%** | `eval/alakazam_best5_baseline_session49.md` |

Note: ladder **660.5 μ** used different gate opponents than today's native full suite — local % is filter only.

### THE SINGLE NEXT ACTION

**Iterate SearchScorer toward 660.5+ μ** (home-grown bar) — one targeted fix, local gate, then `check_upload_eligible`:

```powershell
python scripts/gate_search.py --games 30 --suite full --report
# after a concrete fix:
python scripts/check_upload_eligible.py --brain SearchScorer `
  --deck agent_decks/real_mega_lucario_ex.csv `
  --change "SearchScorer: <delta>" --local-gate <WR>
```

**Parallel offline:** Alakazam levers (beat **62%** local before upload vs **659 μ**).

**Do not upload:** LucarioScorer @ 39.3%, Alakazam re-port, Dragapult without material change.

---

## Recent sessions

| Session | Result |
|---------|--------|
| **50** | B1 port; R12; upload gate; LucarioScorer 39.3%; duplicate upload lesson |
| **49** | Agent catalog; pilot×deck 10% collapse; epistemic reset |
