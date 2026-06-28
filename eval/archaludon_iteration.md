# Archaludon iteration — primary track (Session 52+)

**Champion (saved finalist baseline):** `archaludon_rules` × `archaludon_ex_cinderace.csv` · ref **54083197** · **1196.1 μ** (peak **1224.2**) · **R7 code only** on ladder.

**Iteration posture:** Record every probe in [`report/LADDER_BEST_SO_FAR.md`](../report/LADDER_BEST_SO_FAR.md). Small one-lever changes → local gate (filter) → ladder probe (truth). **Keep iterating** — a low-μ probe is data, not a permanent ban on that idea (refine, combine, or retry on R7 baseline). Replace leader only when probe beats **1196.1 μ** on ≥2 readings. R12 = do not re-upload an existing ref tarball; always ship a **new catalog row** for the next try.

---

## Probe record (Session 52–57, μ desc)

| Ref | Levers | Local n=30 | Ladder μ | Notes |
|-----|--------|----------:|---------:|-------|
| 54083197 | R7 bench guard | 72.7% | **1196.1** | **Leader** — 50 ep, 70.0% WR |
| 54088877 | R8a promote + R8b tempo | 75.3% | 983.8 | Best probe so far; no_active 17.9% on ladder |
| 54109878 | R7 + R8a only | 62.7% | 967.3 | Promote without R8b |
| 54109826 | R7 + R10 prize-attack | 62.0% | 854.0 | Attach-over-attack hypothesis |
| 54089078 | R8 + R9 TO_HAND | 68.0% | 841.0 | Safety net on R8 combo |
| 54138853 | R7 + R11 attach cap | 58.7% | 535.6 | Narrow cap vs global R10 |

**Pattern:** local gate ≠ ladder μ. Use probes to learn; next changes stay small and replay-backed.

**Registry:** [`report/LADDER_BEST_SO_FAR.md`](../report/LADDER_BEST_SO_FAR.md) · [`eval/ladder_log.csv`](ladder_log.csv)

**Offline DS:** `python scripts/analyze_archaludon_losses.py` — prize 10/10 behind race; close losses 82062971, 82073113, 82073596.

**Next levers to try (candidates, not closed):**
- **R12 dead-active tempo** (82062971) — local **70.7%** n=150; probe when uploaded
- Refined prize-race attach (R11 variant) — narrow trigger vs global cap
- R8 learnings: new rows for R8b-only / R8a-only variants

---

**All iteration → [`agent/archaludon_agent.py`](../agent/archaludon_agent.py)**

| Concern | Where in agent |
|---------|----------------|
| Setup / mulligan | `score_setup` |
| MAIN tempo | `score_play`, `score_evolve`, `score_attach`, … |
| Empty bench (this deck) | `_empty_bench_basic_score`, `_empty_bench_block_tempo` (R8b), `apply_overrides` |
| Active KO / promotion | `_mandatory_promote_score` (R8a) |
| Matchup levers | `apply_overrides`, `detect_matchup` |
| Safety net at submit | `archaludon_bench_guard.py` (packaged; do not iterate there first) |

Deck list only: `agent_decks/archaludon_ex_cinderace.csv`. Rebuild: `python scripts/package_archaludon.py`.

**Traces:** [`archaludon_no_active_trace.md`](archaludon_no_active_trace.md) · **A/B:** [`archaludon_bench_guard_ab.md`](archaludon_bench_guard_ab.md)

**R8 local gate (2026-06-26):** baseline **64.7%** → R8a promote **70.7%** → R8a+b tempo **75.3%** n=30 full ([`gate_archaludon.md`](gate_archaludon.md)). Ladder probe only after upload gate.

---

## Per-deck perspective (non-negotiable)

Each submission is **`brain × deck`**: a rule pilot written for **this** 60-card list. Dragapult rules, Lucario rules, and Archaludon rules are **not interchangeable**. Opponent decks also run different logic.

**Therefore:**
- Learn only from **our seat** in ladder replays — when `yourIndex == our_agent_index`.
- Do **not** bucket improvement work by generic “opponent archetype” alone; fix **Archaludon pilot + this list**.
- Kaggle `agent_logs` are timing-only — **deck logs** come from replay step extraction.

**Deck log pipeline:**

```powershell
python scripts/analyze_submission.py --ref 54083197
python scripts/extract_deck_perspective_logs.py --ref 54083197 --deck archaludon `
  --deck-csv agent_decks/archaludon_ex_cinderace.csv --brain archaludon_rules
```

| Output | Purpose |
|--------|---------|
| `report/deck_logs/archaludon/{episode_id}.json` | Our turns only: bench/hand/prize, select context, action |
| `report/deck_logs/archaludon/losses.json` | Losses with last 3 decision snapshots |
| `report/deck_logs/archaludon/index.json` | W/L from **this deck’s** POV |

Code to change: **`agent/archaludon_agent.py`** only (+ deck CSV if list changes). `archaludon_bench_guard.py` is packaged fallback.

---

## Ladder truth (n=50 public, champion ref 54083197)

| Metric | Value |
|--------|------:|
| Win rate | **70.0%** (35W / 15L) |
| Loss reasons | prize **10** · **no_active 4** · deck_out 1 |

Cross-ref (56 ep R8 probe): no_active **17.9%**. Field meta: `report/strategy_analysis_20260627.md`.

---

## Refinement backlog (Archaludon rules + this list only)

### P0 — Forfeit stability (R7b fix — Session 52)

**Root cause (deck logs):** v5 scored SETUP_BENCH `-10000` (“never bench”); MAIN still picked Ultra Ball (300) over Duraludon/Relicanth when bench empty; guard only matches engine **Basic** IDs (169, 57 — Cinderace 666 is not Basic).

**Changes:** setup bench priorities; 50k MAIN play when bench empty; block Ultra Ball when bench empty; extended guard for SETUP_BENCH/TO_BENCH/TO_FIELD.

**Local gate:** **67.3%** n=150 (was 72.7% — acceptable tradeoff for bench safety; ladder is truth).

| Episode | Reason | Signal |
|---------|--------|--------|
| 82055480 | no_active @ t=3 | bench=0 all game |
| 82068759 | no_active @ t=15 | promote path |

**Before upload:** A/B confirm 0 `no_active` @ n≥50; ladder probe as new row (`archaludon_r7b`).

### P1 — Prize losses (our pilot decisions)

**Measured (Session 56, n=10 champion):** all 10 ended **behind in prize race**; deck-log traces show **attach/setup (type 7) over attack (type 13)** when both legal on MAIN. Close losses: 82062971 (2 vs 1), 82073113, 82073596. **R10 probe 54109826** tests `score_attack()` — wait for ladder μ before further changes.

```powershell
python scripts/analyze_archaludon_losses.py
```

### P2 — Local harness (same deck, native opponents)

| Opponent pilot | WR% n=30 |
|----------------|----------:|
| real_iono | **40.0%** |
| dragapult_ex_sample | 66.7% |

Use harness only as A/B filter for **this** brain×deck.

### Ruled out on this list

- Prize-KO overlay (regressed)
- **R9 `_to_hand_pick_floor`** (54089078: 68% local, 841 μ — regressed vs R8)
- ML / MCTS / SearchScorer on Archaludon list
- Copying Dragapult/Lucario levers without Archaludon-specific replay proof

---

## Iteration loop

```powershell
# one change in archaludon_agent.py or archaludon_bench_guard.py
python scripts/gate_archaludon.py --games 30 --suite full --report
python scripts/package_archaludon.py
python scripts/check_upload_eligible.py --manifest dist/candidates/archaludon.manifest.json `
  --change "Archaludon: <delta vs 54083197>" --local-gate <WR>
```

Upload only with material delta (R12). **Saved champion:** ref **54083197** @ **1196.1 μ** — beat on ladder before Sep Final lock-in.
