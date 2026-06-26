# Kaggle Simulation competitions — CLI workflow

Reference for **The Pokémon Company - PTCG AI Battle Challenge Simulation**
(`pokemon-tcg-ai-battle`). Strategy track is separate (`pokemon-tcg-ai-battle-challenge-strategy`).

Related: [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md), [`COMPETITION_SCORING.md`](COMPETITION_SCORING.md),
[`fetch_agent_logs.py`](../scripts/fetch_agent_logs.py), [`track_ladder.py`](../scripts/track_ladder.py).

---

## 1. Find and inspect

```bash
kaggle competitions list -s simulation
kaggle competitions pages pokemon-tcg-ai-battle
kaggle competitions pages pokemon-tcg-ai-battle --content
kaggle competitions topics list pokemon-tcg-ai-battle -s top --page-size 10
kaggle competitions topics show pokemon-tcg-ai-battle <topic_id>
```

---

## 2. Join and download

Accept rules on the Kaggle website first.

```bash
kaggle competitions list --group entered
kaggle competitions download pokemon-tcg-ai-battle -p data/kaggle_ref/simulation
```

Local engine copy: `python scripts/fetch_sim_engine.py` → `data/sim/sample_submission/cg/`.

---

## 3. Submit an agent

**Before submit (R12):** `python scripts/check_upload_eligible.py --suggest` then gate + manifest check.

Packaging:

```bash
# Dragapult (880.9 μ ship track)
python scripts/package_dragapult.py

# Alakazam best5 (659 μ — upload only with material improvement)
python scripts/package_alakazam.py

# Search / heuristic / lucario_mcts
python scripts/package_submission.py --name <candidate> --scorer search|heuristic|lucario_mcts --deck <path> [--model <path>]
```

Submit (user OK only; 5/day):

```powershell
kaggle competitions submit pokemon-tcg-ai-battle `
  -f dist/candidates/dragapult_ex_sample.tar.gz `
  -m "catalog row + one-line delta"
```

**Limits:** 5 uploads/team/day; **2 Final Submissions** for judging (select manually on Kaggle).

---

## 4. Monitor submissions

```bash
kaggle competitions submissions pokemon-tcg-ai-battle
kaggle competitions submissions pokemon-tcg-ai-battle -v
python scripts/track_ladder.py
```

Note the submission **ref** (ID) for episodes/logs.

---

## 5. Episodes, replays, agent logs

```bash
# List episodes for a submission ref
kaggle competitions episodes <submission_ref>
kaggle competitions episodes <submission_ref> -v

# Episode replay JSON
kaggle competitions replay <episode_id>
kaggle competitions replay <episode_id> -p report/replays

# Agent debug logs (agent_index is 0-based)
kaggle competitions logs <episode_id> 0
kaggle competitions logs <episode_id> 1 -p report/agent_logs
```

Local wrapper (READ ONLY): `python scripts/fetch_agent_logs.py --ref <submission_ref>`.

---

## 6. Leaderboard scouting

```bash
kaggle competitions leaderboard pokemon-tcg-ai-battle -s
kaggle competitions team-submissions <team_id>
kaggle competitions episodes <best_submission_ref>
```

Use replays/logs on top teams to study tempo, bench usage, and prize sequencing.

---

## 7. Typical iteration loop (2026-06 — native field harness)

1. **Local gate (filter only):** native opponents via `eval/harness.py` — not ladder truth
   ```powershell
   python scripts/gate_alakazam.py --games 30 --suite full --report
   python scripts/gate_search.py --games 30 --suite full --report
   python scripts/gate_dragapult.py --games 30 --suite full --report
   python scripts/gate_lucario_rules.py --games 30 --suite full --report
   ```
2. **Upload eligibility (R12):** `python scripts/check_upload_eligible.py --brain … --deck … --change "…" --local-gate <WR>`
3. **Package dry-run:** `package_dragapult.py` / `package_alakazam.py` / `package_submission.py`
4. **Submit** (user OK): `kaggle competitions submit …`
5. Wait **≥40 min**; require **≥2 μ readings** before pivoting (R1)
6. **Episode analysis:** `python scripts/analyze_submission.py --ref <ref>`
7. Log ref + μ in `eval/ladder_log.csv`; decode row in `eval/AGENT_CATALOG_FULL.md`

**Packaged agent vs public opponents (different gate):**
```powershell
python scripts/gate_vs_public.py --agent dist/candidates/<name>.tar.gz --games 30
```

**Do not re-upload** a brain×deck already COMPLETE on ladder except final lock-in near deadline (R12).

---

## 8. Local debugging (harness)

Use harness gates + smoke tests offline (no Kaggle egress required for gates):

```powershell
python -m pytest tests/test_harness_smoke.py -q
python scripts/gate_alakazam.py --games 10 --suite core
```

For head-to-head packaged agents vs `data/kaggle_ref/opponents/`, use `gate_vs_public.py` (requires `--agent`).

---

## 9. Episode analysis (per submission ref)

μ alone hides *how* an agent wins or loses. Pull episode stats after COMPLETE:

```bash
python scripts/analyze_submission.py --ref 53886522
python scripts/analyze_submission.py --ref 53869254 --agent-index 0
```

Pipeline:
1. `fetch_agent_logs.py --ref <ref>` (episode list)
2. Downloads replay JSON → `report/replays/<episode_id>.json`
3. Writes `report/submission_stats/{ref}_stats.csv`
4. Updates `report/submission_log.csv` with win_rate, avg_turns, fast_loss_pct, top_loss_reason

**Pass criteria (L4):** `avg_turns > 15`, `fast_loss_pct < 20%`, top loss reason ≠ `no_active`.

See [`EVAL_PROTOCOL.md`](EVAL_PROTOCOL.md) and [`COMPETITION_SCORING.md`](COMPETITION_SCORING.md).

---

## 10. Project-specific commands

| Task | Command |
|------|---------|
| Upload gate (R12) | `python scripts/check_upload_eligible.py --suggest` |
| Alakazam gate (659 μ bar) | `python scripts/gate_alakazam.py --games 30 --suite full --report` |
| SearchScorer gate | `python scripts/gate_search.py --games 30 --suite full --report` |
| Dragapult gate / package | `python scripts/gate_dragapult.py --games 30` · `python scripts/package_dragapult.py` |
| LucarioScorer gate | `python scripts/gate_lucario_rules.py --games 30 --suite full --report` |
| Packaged vs public agents | `python scripts/gate_vs_public.py --agent dist/candidates/<name>.tar.gz --games 30` |
| Ladder sync | `python scripts/track_ladder.py` · `--fetch-logs` |
| Episode stats | `python scripts/analyze_submission.py --ref <ref>` |
| Meta by μ band | `python scripts/analyze_meta_by_mu_band.py --download-per-band 50` |
