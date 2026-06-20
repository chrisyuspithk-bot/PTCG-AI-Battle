# Repo cleanup & continuous improvement plan

Date: 2026-06-20  
Status: **active roadmap** after Lucario bench fix + smart-bench submit.

---

## What we learned (condense into rules)

| Learning | Rule going forward |
|----------|-------------------|
| Empty bench → active KO → fast μ loss | **Mandatory:** ≥1 backup basic; cap voluntary bench at **2** (`agent/smart_bench.py`, `agent/bench_guard.py`) |
| Early RL/MCTS checkpoint ≠ ladder strength | **No RL submit** until L1 public gate + replay spot-check pass |
| Official deck-specific policy beats generic RL on Lucario | Use **`LucarioScorer`** (sample policy port) for Lucario deck; keep **`RuleCoreScorer`** for other decks |
| Wrong card IDs in `deck_tech` silently broke setup priority | **Verify IDs** against official sample / `EN_Card_Data.csv` before any deck tech change |
| Ladder μ ≠ local random WR | Log **turn count + loss reason** from replays; never optimize on local WR alone |
| 5 uploads/day, 2 Final Submissions | Manual Final selection before deadline (`data/SUBMISSION_PLAYBOOK.md`) |
| Simulator legal mask is truth | Train/eval only on `select.option`; don't infer legality from card text |
| GPU Track B needs Python 3.13 + cu128 | **Not** miniconda CPU torch (`data/PROJECT_PRIORITIES.md`) |
| Kaggle replay JSON + local recorder | Debug policy failures in minutes, not after ladder μ drift |

---

## Phase 0 — Immediate (this week)

### Done
- [x] `agent/lucario_policy.py` — official sample + smart bench
- [x] `agent/smart_bench.py`, `agent/bench_guard.py` — universal guard in `Agent.act`
- [x] Fix `LUCARIO_TECH` card IDs (676=Solrock, 677=Riolu, 678=Mega Lucario ex)
- [x] Package + submit `track_c_lucario_rulecore_smartbench`
- [x] Smoke 17/17

### Next 48h
1. **Pull ladder μ** for new Lucario submit; compare vs Search 668 / broken RL 355.
2. **Add `scripts/record_local_battle.py`** — JSON replay recorder (kiyotah pattern) for regression tests.
3. **Golden replay tests** — 3 fixtures: empty-bench prevented, smart setup bench (1–2), attack blocked with no backup.
4. **Re-download Lucario notebook** `model_best.pth` after iter≥2; gate before any Track D re-submit.

---

## Phase 1 — Repo hygiene (1–2 sessions)

### A. Source tree (single truth)

```
agent/           # competition agents only (what gets packaged)
  lucario_policy.py   # deck-specific brains
  rule_core.py        # generic brain + Lucario delegate
  smart_bench.py      # shared bench policy
scripts/         # gates, package, train, mine
data/            # protocols, playbooks, card CSV
report/          # generated artifacts (gitignore heavy blobs)
dist/candidates/ # packaged tarballs only (not full submission_build/)
notebooks/       # Kaggle GPU jobs
agent_decks/     # deck CSVs by archetype
```

**Actions:**
- [ ] Add/update root `.gitignore`: `dist/submission_build/`, `**/__pycache__/`, `*.pth`, large `report/az/`, duplicate `dist/submission_build/**`
- [ ] **Stop tracking** `dist/submission_build/` tree (already duplicated tar content)
- [ ] Move one-off handoffs (`RUN_36_HANDOFF.md`, etc.) → `report/handoffs/` or delete after PROGRESS absorb
- [ ] Deduplicate `.cursor/CHANGELOG.agent.md` path variants (Windows duplicate entries)

### B. Documentation map (read order)

| Order | File | Purpose |
|-------|------|---------|
| 1 | `PROGRESS.md` | Latest handoff |
| 2 | `TASKS.md` | Next unchecked task |
| 3 | `data/PROJECT_PRIORITIES.md` | Two-track priorities |
| 4 | `data/SUBMISSION_PLAYBOOK.md` | Upload limits |
| 5 | `data/KAGGLE_SIMULATION_CLI.md` | Episodes/replays |
| 6 | `data/EVAL_PROTOCOL.md` | L0–L4 gates |
| 7 | `data/COMPETITION_SCORING.md` | μ semantics |

**Actions:**
- [ ] Merge overlapping content in `report/competition_improvement_plan_*.md` into this plan; archive stubs
- [ ] One `notebooks/README.md` index linking Lucario / Track B / Alakazam kernels

### C. Agent packaging matrix

| Scorer | Deck | When to use | Gate |
|--------|------|-------------|------|
| `rulecore` | Lucario | **Default Lucario ladder** (official + smart bench) | L1 public + replay |
| `search` | Kyogre / meta | Proven 626–679 μ | L2 pool |
| `learned` | per-deck npz | Only after Track B L2 pass | SPRT 210/240 |
| `lucario_mcts` | Lucario + `.pth` | After notebook promotions + bench replay OK | L1 + local JSON |
| `heuristic` | any | Smoke / fallback only | smoke only |

**Actions:**
- [ ] Add `--scorer lucario` alias → `LucarioScorer` directly in `package_submission.py`
- [ ] `scripts/promote_candidate.py` — registry row + gate log + tarball path

---

## Phase 2 — Training loops (continuous)

### Track A — Policy quality (Lucario + meta)

```
record_local_battle → tag failures → fix scorer → golden JSON → gate → package → submit (user OK)
```

- BC from public replays: `mine_episode_replays.py` → `collect_traces.py` (extend for JSON source)
- Lucario notebook: finish 40 iters; promote only when gate beats `LucarioScorer` baseline

### Track B — Per-deck Learned RL

- One `train_track_b_deck.py` run per deck with **Python 3.13 GPU**
- Artifacts: `agent/models/distilled_<deck>_v1.npz`
- **Never share** one distill npz across decks (Alakazam E1 lesson)

### Track C — Deck RL (GA)

- Checkpoint: `report/rl_deck_campaign/best_deck.csv` (fitness 0.864)
- gen19 lanes passed L1; queue L2 + package when Alakazam/Kyogre brains ready

---

## Phase 3 — Measurement discipline

### Every reported win-rate must include:
- Game count, opponent definition, seed policy, deck paths, scorer name

### Gate pyramid (from `EVAL_PROTOCOL.md`)
- **L0** smoke 17/17
- **L1** public sample field (12×12 minimum)
- **L2** benchmark pool SPRT
- **L3** ladder μ after COMPLETE + 40 min
- **L4** replay mining on worst episodes

### Submission log (maintain in `report/submission_log.csv`)

| ref | date | scorer | deck | μ @24h | notes |
|-----|------|--------|------|--------|-------|
| 53869254 | 2026-06-20 | search | lucario | 668 | best Lucario rules |
| 53885445 | 2026-06-20 | lucario_mcts | lucario | 355 | early RL — retired |
| TBD | 2026-06-20 | rulecore smartbench | lucario | pending | official sample + bench fix |

---

## Phase 4 — Alakazam & portfolio

1. **Phase A:** `rulecore` + `pool_alakazam_dudunsparce.csv` — submit only if L1 ≥ Lucario Search behavior
2. **Phase B:** 1M GPU Learned — submit only if beats Phase A on L2
3. **Portfolio (2 Finals):** Kyogre Search ~626 + best Lucario; manually pin on Kaggle

See `report/alakazam_submission_plan.md` for error log E1–E8.

---

## Phase 5 — Automation (optional, high ROI)

- [ ] `scripts/record_local_battle.py` + viewer note in `KAGGLE_SIMULATION_CLI.md`
- [ ] Nightly: smoke + one L1 gate on protected tarball; write `report/nightly_checkpoint.json`
- [ ] Pre-submit hook: smoke + L1 + user confirm flag

---

## Definition of done (repo “clean”)

- [ ] No duplicate submission_build trees in git status
- [ ] Every active scorer documented in packaging matrix
- [ ] Lucario ladder agent = official sample + smart bench (submitted)
- [ ] Local JSON replay path documented and scripted
- [ ] TASKS.md reflects single next action per track
- [ ] PROGRESS.md updated after each run

---

## Single next actions (by track)

| Track | Next action |
|-------|-------------|
| **Lucario ladder** | Watch μ for `track_c_lucario_rulecore_smartbench`; replay worst episodes |
| **Lucario RL** | Notebook iter≥2 → import → JSON replay → compare vs RuleCore before re-submit |
| **Alakazam** | Finish GPU 1M or package Phase A RuleCore |
| **Deck RL** | L2 package gen19 fast-basic with passed Learned npz |
| **Repo** | Implement `record_local_battle.py` + gitignore cleanup |
