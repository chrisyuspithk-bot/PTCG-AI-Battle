# Evaluation & testing protocol

Professional workflow for this repo. **Local gates filter; Kaggle ladder validates.**

**Primary submission track: Track B (LearnedScorer)** — train + distill per deck; use both Final Submission slots for Learned agents once local gates pass.

Related: [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md) (upload rules), [`META_NOTES.md`](META_NOTES.md) (field meta).

---

## 1. Three optimization loops (do not mix them)

| Loop | What moves | Training | Submission brain | Deck at submit |
|------|------------|----------|------------------|----------------|
| **A — Rules + search** | Heuristic logic; optional `search_*` on promotion/switch | None (hand-tuned) | `SearchScorer` or default `HeuristicScorer` | Any legal deck |
| **B — Policy RL** | MaskablePPO on **fixed player deck** vs league opponents | `rl/train_rl.py` → distill → `distilled_v1.npz` | `LearnedScorer` | **Same deck (or close archetype) used in training** |
| **C — Deck RL / GA** | 60-card list vs benchmark suite | `rl/train_deck_campaign.py` | Pair with A or B brain | **Output deck** (`report/rl_deck_campaign/best_deck.csv`) |

**Your insight is correct:** a distilled policy is **not deck-agnostic**. It learns on `CabtEnv` with one player deck (`agent/deck.csv` by default) and meta opponents from the league/benchmark. Submitting LearnedScorer on Alakazam or Dragapult without **retraining + re-distilling on that deck** is a valid ladder probe but not a fair test of the policy.

---

## 2. Benchmark suite (opponents for deck RL & local fitness)

**Canonical list:** [`agent_decks/benchmark/suite.json`](../agent_decks/benchmark/suite.json)

| Tag | Decks | Purpose |
|-----|-------|---------|
| **meta** | 6× `pool_*.csv` | Championship-field proxies (Dragapult, Crustle, Bellibolt, Alakazam, Greninja, Mega Greninja) |
| **high_performer** | Kyogre, big basic, Starmie | Local winners |
| **baseline** | `agent/deck.csv` | Pilot sanity |

**Maintain:** add real Worlds lists to `agent_decks/benchmark/worlds_*.csv` + `suite.json` when sourced. Validate with `scripts/validate_deck.py`.

**Used by:**
- `rl/benchmark.py` — weighted win rate for deck fitness
- `rl/train_deck_campaign.py` — GA generations
- `scripts/arena.py` `pool_decks()` — 6 meta decks for Track A/B gates (subset of suite)

---

## 3. Test pyramid (run in order)

### L0 — Legality (every change)

```bash
python scripts/smoke_test.py                    # 17/17 agent contract
python scripts/smoke_replay.py                  # 3/3 bench-guard golden fixtures
python scripts/validate_deck.py                 # all agent_decks/*.csv
```

### L1 — Local pool (fast smoke, N=8–12 games/opponent)

| Goal | Command |
|------|---------|
| Heuristic on deck | `python scripts/arena.py --help` / gate helpers |
| Search vs pool | `python scripts/gate_track_a.py --games 12 --deck <path>` |
| Learned vs pool | `python scripts/gate_track_b.py --games 12 --deck <path> --model agent/models/distilled_<slug>_v1.npz` |
| **Track B full pipeline** | `python scripts/train_track_b_deck.py --deck <path> --timesteps 100000 --gate-games 40 --package` |
| Deck spread (Learned) | Only after per-deck train+distill; see `scripts/train_track_b_deck.py` |
| Deck fitness (weighted) | `python rl/benchmark.py` |

Record: wins/total, game count, deck path, scorer name.

### L2 — SPRT gate (promote to packaging, N=40)

```bash
python scripts/gate_track_b.py --games 40 --deck agent_decks/a2_kyogre_33_energy.csv --model agent/models/distilled_kyogre-33-energy_v1.npz
```

Or one command:

```bash
python scripts/train_track_b_deck.py --deck agent_decks/a2_kyogre_33_energy.csv --slug kyogre --timesteps 100000 --gate-games 40 --package --promote
```

Pass criteria: SPRT `accept_b` or win-rate ≥ Search baseline (see gate scripts).

### L3 — Package dry-run

```bash
python scripts/package_submission.py --name <candidate> --scorer heuristic|search|learned --deck <path>
python scripts/verify_archive.py dist/candidates/<candidate>.tar.gz --games 50
```

### L4 — Episode analysis (why W/L; complements μ)

After a submission reaches COMPLETE and plays ladder games:

```bash
python scripts/analyze_submission.py --ref <submission_ref>
```

Reads `report/replays/*.json` and updates [`report/submission_log.csv`](../report/submission_log.csv) with:
- **win_rate** (W / decided episodes)
- **avg_turns** / **median_turns**
- **fast_loss_pct** (losses ending before turn 15)
- **top_loss_reason** (`prize`, `deck_out`, `no_active`, `card_effect`)

**Pass criteria:** `avg_turns > 15`, `fast_loss_pct < 20%`, top loss reason ≠ `no_active`.

Local debugging before submit:

```bash
python scripts/record_local_battle.py --agent-a lucario --agent-b search --games 20
```

### L5 — Kaggle ladder (truth; max 5/day, 2 Finals)

See [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md). **Manually select 2 Final Submissions** before deadline.

```bash
python scripts/track_ladder.py
python scripts/track_ladder.py --fetch-logs
```

---

## 4. Recommended matrix: brain × deck

Test **one dimension at a time** locally; combine only after single-axis gates pass.

### Track A (Search) — deck varies, brain fixed

1. `scripts/deck_search.py` or `scripts/prepare_track_a_probes.py` — energy/base grid vs pool
2. Gate best deck @ 40 games
3. Package `--scorer search`
4. Ladder probe (1 slot)

**Today’s result:** Search + Kyogre+2e (625→546 μ) ≈ Heuristic Kyogre (633); Search + Abomasnow weaker.

### Track B (Learned) — **primary submission path; retrain per archetype**

```bash
python scripts/train_track_b_deck.py \
  --deck agent_decks/a2_kyogre_33_energy.csv \
  --slug kyogre \
  --timesteps 100000 \
  --gate-games 40 \
  --package \
  --promote
```

Steps inside the orchestrator:
1. `rl/train_rl.py --deck <path> --opponents benchmark` (10 diverse opponents)
2. `scripts/distill_policy.py` with matching deck/opponents
3. `scripts/gate_track_b.py --deck <path> --model distilled_<slug>_v1.npz`
4. Package `track_b_learned_<slug>.tar.gz` with `--model` (embeds npz in tarball)

Do **not** reuse one `distilled_v1.npz` across archetypes without retraining.

**Today’s result:** Single distill (trained on default deck) on Alakazam/Dragapult → 490 / 469 μ vs Heuristic Kyogre 633.

### Track C (Deck RL) — deck varies, scorer fixed during fitness

```bash
# Overnight: alternate policy PPO + deck GA
python rl/train_deck_campaign.py --phase full --cycles 2 --resume

# Output
report/rl_deck_campaign/best_deck.csv
```

Evaluate exported deck with **the same scorer** used in fitness (`--scorer` in benchmark). Then:

- **Heuristic/Search:** package immediately after L2 gate
- **Learned:** run Track B pipeline **on the new deck** before submitting LearnedScorer

---

## 5. Policy RL training requirements

| Requirement | Why | Where |
|-------------|-----|-------|
| **Fixed player deck** per run | Policy input is board+options for that list’s lines | `CabtEnv(deck_path=...)` |
| **Diverse opponents** | Avoid overfitting to one matchup | `rl/env_factory.py` — benchmark suite (default) or pool |
| **Distill to numpy** | Kaggle has no torch | `scripts/distill_policy.py --deck` must match train |
| **Latency < 50 ms** | 10 min/game clock | `report/distill_gate.md` |

`rl/train_rl.py` now trains vs **benchmark suite** by default (same opponents as deck RL campaign).

---

## 6. Daily / weekly cadence

### Daily (when uploading)

| Slot | Suggested use |
|------|----------------|
| 1–3 | Probes (new deck archetype or brain A/B) |
| 4–5 | **Lock in** — re-upload best μ; **select 2 Finals** on Kaggle UI |

Always: `track_ladder.py` + `--fetch-logs` after COMPLETE.

### Weekly (offline)

| Day | Task |
|-----|------|
| Mon | Refresh benchmark suite; validate new Worlds proxies |
| Tue | Track A deck_search @ 40g on best base |
| Wed | Track B policy retrain on **one** new archetype + distill |
| Thu | Deck campaign cycle (`train_deck_campaign.py`) |
| Fri | Compare `report/ladder_history.csv`; update `submission_candidates_*.md` |

---

## 7. Artifacts map

| Artifact | Path |
|----------|------|
| Heuristic package | `dist/candidates/a2_kyogre.tar.gz` etc. |
| Search package | `dist/candidates/track_a_probe_*.tar.gz` |
| Learned package | `dist/candidates/track_b_learned_<slug>.tar.gz` |
| Policy checkpoint | `agent/models/rl_policy.zip` |
| Distilled weights | `agent/models/distilled_v1.npz` |
| Deck campaign best | `report/rl_deck_campaign/best_deck.csv` |
| Ladder history | `report/ladder_history.csv` |
| Agent logs | `report/agent_logs/` |

---

## 8. Decision log (2026-06-19 ladder)

| Submit | Brain | Deck | μ | Note |
|--------|-------|------|---|------|
| Kyogre heuristic | Heuristic | Kyogre | **633** | Best overall; not Final unless selected |
| TA1 | Search | Kyogre+2e | 546 | Final slot |
| TA2 | Search | Abomasnow+4e | 499 | Final slot |
| Alakazam | Learned (wrong deck train) | Alakazam | 490 | Probe only |
| Dragapult | Learned (wrong deck train) | Dragapult | 469 | Probe only |

**Takeaway:** Search ≈ heuristic on Kyogre line; Learned needs **per-deck retrain**; pick Finals manually.

---

## 9. Quick command reference

```bash
# Track A
python scripts/gate_track_a.py --games 40 --deck agent_decks/a2_kyogre_33_energy.csv
python scripts/package_submission.py --name track_a_search --scorer search --deck <deck>

# Track B (after retrain on target deck)
python rl/train_rl.py --timesteps 50000 --resume
python scripts/distill_policy.py --episodes 100
python scripts/gate_track_b.py --games 40
python scripts/package_submission.py --name track_b_learned_kyogre --scorer learned --deck <same deck>

# Deck RL
python rl/train_deck_campaign.py --phase full --cycles 2 --resume

# Ladder
python scripts/track_ladder.py --fetch-logs
```
