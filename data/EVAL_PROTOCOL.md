# Evaluation & testing protocol

Professional workflow for this repo. **Local gates filter; Kaggle ladder validates.**

**Proven home-grown floor:** SearchScorer × real Mega Lucario ex **660.5 μ** (ref 53869254).  
**Ladder bar:** Dragapult v3 **880.9 μ**. Any upload must cite **new** catalog row + hypothesis (R1, R3, **R12**).  
**Catalog:** [`eval/AGENT_CATALOG_FULL.md`](../eval/AGENT_CATALOG_FULL.md)

Related: [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md), [`RULINGS.md`](../RULINGS.md) R1–R12,
[`META_NOTES.md`](META_NOTES.md).

---

## 1. Optimization loops (current vs retired)

| Loop | What moves | Training | Submission brain | Status |
|------|------------|----------|------------------|--------|
| **A — Rules + search** | Heuristic logic; `search_*` on key contexts | None | `SearchScorer` / `HeuristicScorer` | **KEEP — floor** |
| **D — Lucario field RL+MCTS** | Transformer + MCTS | `train_lucario_field_mcts.py` | `lucario_mcts` | **RETIRED** — v5 **580.6 μ** < Search **660.5 μ** |
| **Per-deck rule pilot** | Official sample logic + safety wrapper | None | e.g. `dragapult` custom agent module | **Active probes** |
| **B — Policy RL (PPO+distill)** | MaskablePPO per deck | `rl/train_rl.py` (graveyard) | `LearnedScorer` | **RETIRED** — best 585 μ |
| **C — Deck GA** | 60-card list | `rl/train_deck_campaign.py` (graveyard) | pair with A/B | **RETIRED** |

**Invariant:** gate on **real mined decks + public agents** (`agent_decks/{real_*,top_mined_*}`,
`data/kaggle_ref/opponents/`). Never `pool_*` proxies or mirror-only training (Ruling R2).

---

## 2. Real-field opponent set

**Canonical lists (today):** `agent_decks/real_*.csv`, `agent_decks/top_mined_*.csv` (10 decks used
by `train_lucario_field_mcts.py`).

**Public agents:** `python scripts/extract_public_agents.py` → `data/kaggle_ref/opponents/`.

**Future:** migrate to `field/decks/` + `field/registry.json` when `eval/harness.py` lands (TASKS F2).

**Retired as gate opponents:** `agent_decks/pool_*.csv`, random, mirror-only self-play.

---

## 3. Test pyramid (run in order)

### L0 — Legality (every change)

```bash
python scripts/smoke_test.py              # agent contract
python scripts/smoke_replay.py            # bench-guard golden fixtures
python scripts/smoke_cg_engine.py         # cg.dll battle_start (MCTS / field train)
python scripts/validate_deck.py           # deck CSV legality
```

### L1 — Real-field gate (N≈30/opp, Wilson CI)

```bash
python scripts/gate_search.py --games 30 --suite full --report   # SearchScorer (660.5 μ bar)
python scripts/gate_lucario_rules.py --games 30 --suite full --report  # LucarioScorer
python scripts/gate_dragapult.py --games 30    # Dragapult ex probe
python scripts/gate_vs_public.py --agent dist/candidates/<name>.tar.gz --games 30  # packaged vs public agents
```

Record: wins/total/draws, opponents, seeds, deck, brain name.

### L2 — SPRT vs champion

Compare candidate vs SearchScorer floor on the same opponent set and game count. Promote only if
Wilson lower bound beats champion or SPRT accepts.

### L3 — Package dry-run

```bash
# Rules/search
python scripts/package_submission.py --name <candidate> --scorer search --deck <path>

# Lucario field RL+MCTS (after train completes)
python scripts/package_submission.py \
  --name track_d_lucarioex_field_v1 \
  --scorer lucario_mcts \
  --deck agent_decks/real_mega_lucario_ex.csv \
  --model rl_mcts_field/lucarioex_v1/model_best.pth \
  --meta rl_mcts_field/lucarioex_v1/run_meta.json

python scripts/verify_archive.py dist/candidates/<name>.tar.gz --games 50
```

### L4 — Episode analysis (post-ladder)

```bash
python scripts/analyze_submission.py --ref <submission_ref>
python scripts/track_ladder.py --fetch-logs
```

**Pass criteria:** `avg_turns > 15`, `fast_loss_pct < 20%`, top loss reason ≠ `no_active`.

### L5 — Kaggle ladder (truth)

See [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md). **≥2 μ readings ≥40 min apart** (Ruling R1).
Max **5 uploads/day**; **2 Final Submissions** selected manually.

**Mandatory before upload (R12):**

```bash
python scripts/check_upload_eligible.py --manifest dist/candidates/<name>.manifest.json \
  --change "ONE LINE: what changed vs last ladder row" --local-gate <WR>
# or: python scripts/check_upload_eligible.py --suggest
```

Exit **1** = do not upload. Ports end at L3 dry-run; ladder truth already exists for that row.

---

## 9. Upload iteration loop (how to improve, not replay)

Every upload must answer **four questions** in writing (`--change` + Kaggle `-m`):

| # | Question | Where to look |
|---|----------|---------------|
| 1 | **Which catalog row am I beating?** | `eval/AGENT_CATALOG_FULL.md` — ref + μ |
| 2 | **What exactly changed?** | brain logic / deck list / levers / scorer — one primary delta |
| 3 | **Why should μ improve?** | matchup evidence from local gate or replay, not vibes |
| 4 | **What is the stop rule?** | R1: 2 readings; pivot if μ flat or down |

### Work order (never skip)

```
IDEA → one concrete change → L0 smoke → L1 gate n≥30 (record R8 metadata)
     → compare WR to prior row for same deck
     → L3 package dry-run → check_upload_eligible.py (exit 0)
     → user OK → L5 ladder → track_ladder.py → update catalog
```

### When **not** to upload

| Situation | End state |
|-----------|-----------|
| Porting external notebook → `agent/` | Dry-run + local gate. Ladder row already exists. |
| Repackaging same hashes | `check_upload_eligible.py` blocks policy-equivalent manifests. |
| Local gate flat or down vs prior | Fix or abandon; do not burn a slot. |
| “Verify packaging” | **Never** — that is L3 dry-run only. |

### High-value next rows (2026-06-26)

Run `python scripts/check_upload_eligible.py --suggest` for the live list. Today:

1. **LucarioScorer × Lucario deck** — never properly laddered (535.6 @ 2 games); beat Search **660.5** is the bar.
2. **SearchScorer iteration** on Lucario — one fix at a time; local WR must move before upload.
3. **Alakazam levers** — only after local gate beats **62%** port baseline; targets **659+ μ** as new row.

### Final lock-in exception (R12)

Near **Sep 2026** deadline only: re-ship best-known tarball with `--final-lock-in` to pin **2 Finals**.
Not for development probes.

---

## 4. Lucario field RL+MCTS workflow (Loop D)

```powershell
python scripts/bootstrap_lucario_mcts_runtime.py   # after official sample changes
python scripts/smoke_cg_engine.py
python scripts/train_lucario_field_mcts.py --device cpu --cycles 5
# outputs: rl_mcts_field/lucarioex_v1/{model_best.pth, metrics.csv, run_meta.json}
```

**Training rules:**
- Opponents = real field decks only (see `run_meta.json` `opponents` list).
- Opponent deck passed into `search_begin` (not Snorlax stub).
- Draw terminal label = 0.0 in training.
- Inference: `LucarioScorer` fallback if model missing; `LUC_SUBMIT_SEARCH_COUNT` modest (default 12).

**Ship criteria:** L0–L2 on real field, then L5 with stable μ **> 850.5** (current best so far).
SearchScorer 668 remains the rules-only Lucario floor; **850.5 is the team bar** until beaten.

---

## 5. Per-deck rule pilot workflow

Example: Dragapult ex (`agent/dragapult_agent.py`, `agent_decks/dragapult_ex_sample.csv`).

```bash
python scripts/gate_dragapult.py --games 30
python scripts/package_dragapult.py   # if packaging script present
```

Improve via matchup levers on visible board (Boss timing, bench depth) — one change at a time, re-gate.

---

## 6. Artifacts map (live)

| Artifact | Path |
|----------|------|
| Search/heuristic package | `dist/candidates/*.tar.gz` |
| Lucario MCTS weights | `rl_mcts_field/lucarioex_v1/model_best.pth` (gitignored) |
| Train metrics | `rl_mcts_field/lucarioex_v1/metrics.csv` |
| Ladder history | `report/ladder_history.csv`, `report/submission_log.csv` |
| Future unified log | `eval/ladder_log.csv` (scaffold) |
| Replays / logs | `report/replays/`, `report/agent_logs/` |

**Graveyard:** Track B/C artifacts under `graveyard/pre-reset-20260622` — do not resurrect without
addressing RULINGS 2C.

---

## 7. Quick command reference

```bash
# Spine gate (packaged tarball vs public agents)
python scripts/gate_vs_public.py --agent dist/candidates/<name>.tar.gz --games 30

# SearchScorer (home-grown bar)
python scripts/gate_search.py --games 30 --suite full --report

# Lucario field train (CPU default)
python scripts/train_lucario_field_mcts.py --device cpu --cycles 5

# Package Lucario MCTS
python scripts/package_submission.py --name track_d_lucarioex_field_v1 \
  --scorer lucario_mcts --deck agent_decks/real_mega_lucario_ex.csv \
  --model rl_mcts_field/lucarioex_v1/model_best.pth \
  --meta rl_mcts_field/lucarioex_v1/run_meta.json

# Ladder
python scripts/track_ladder.py --fetch-logs
```

---

## 8. Historical decision log (pre-reset)

See `RULINGS.md` Part 1 for the full μ scoreboard. Key takeaway: Learned/MCTS/GA paths never beat
hand-tuned rules/search on the ladder; the rebuild gates all new ML against that evidence.
