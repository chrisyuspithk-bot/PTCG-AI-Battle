# Submission registry — rebuild & resubmit

**Before any upload:** `python scripts/check_upload_eligible.py` must exit **0** (R12).

**Limits:** 5 uploads/day; **2 Final Submissions** (manual). See [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md).

**Quick rebuild (ladder track only):**
```powershell
cd Z:\kaggle\pokemon
python scripts/package_dragapult.py
```
Lucario archive tarballs: `python scripts/repackage_champions.py --include-lucario`

---

## Ladder ship track (880.9 μ)

| Field | Value |
|-------|-------|
| **Ref** | 53989933 |
| **μ** | **880.9** |
| **Brain** | Official Crispin + `dragapult_bench_guard.py` (R7) |
| **Deck** | `agent_decks/dragapult_ex_sample.csv` |
| **Rebuild** | `python scripts/package_dragapult.py` |

---

## Home-grown benchmark (660.5 μ — improve, don't ignore)

| Field | Value |
|-------|-------|
| **Ref** | 53869254 |
| **Brain** | SearchScorer |
| **Deck** | `agent_decks/real_mega_lucario_ex.csv` |
| **Rebuild** | `python scripts/package_submission.py --name lucario_ex_search --scorer search --deck agent_decks/real_mega_lucario_ex.csv` |

---

## External benchmark (659.0 μ — ported S50)

| Field | Value |
|-------|-------|
| **Ref** | 53913404 |
| **μ** | **659.0** (ladder ref 53913404 — **do not re-upload**, R12) |
| **Brain** | `agent/alakazam_agent.py` (ryotasueyoshi best5 + never-crash wrapper) |
| **Deck** | `agent_decks/ryotasueyoshi_alakazam_best5.csv` |
| **Rebuild** | `python scripts/package_alakazam.py` |
| **Local gate** | 62.0% full suite @ n=30 (`eval/alakazam_best5_baseline_session49.md`) |
| **Bootstrap** | `python scripts/bootstrap_alakazam_best5.py` (from notebook) |

---

## Ruled out for μ chase

| Ref | μ | Why |
|-----|--:|-----|
| 53995982 | 580.6 | Field MCTS v5 < model4 651.3 < Search 660.5 |
| Track B learned | ≤585 | Retired |
| 53946148 | 185.4 | Snorlax-opponent MCTS |

Full table: [`eval/AGENT_CATALOG_FULL.md`](../eval/AGENT_CATALOG_FULL.md)

---

## Post-upload

```powershell
python scripts/track_ladder.py
```
Append `eval/ladder_log.csv` + update catalog if new brain×deck row.

---

## Related

- [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md) — limits & checklist
- [`KAGGLE_SIMULATION_CLI.md`](KAGGLE_SIMULATION_CLI.md) — CLI workflow
- [`eval/ladder_log.csv`](../eval/ladder_log.csv) — μ history
