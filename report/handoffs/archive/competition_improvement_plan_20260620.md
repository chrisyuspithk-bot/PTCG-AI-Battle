# Competition Improvement Plan - 2026-06-20

## Sources Checked

- Kaggle REST API, read-only:
  - `competitions/submissions/list/pokemon-tcg-ai-battle`
  - `competitions/list?search=pokemon-tcg-ai-battle`
- Local ladder history: `report/ladder_history.csv`
- Local reports:
  - `report/ladder_analysis_20260619.md`
  - `report/rl_deck_candidate_readiness_20260619.md`
  - `data/EVAL_PROTOCOL.md`
  - `data/SUBMISSION_PLAYBOOK.md`
  - `data/META_NOTES.md`
- Local gate artifacts:
  - `report/track_b_gates/track_b_learned_rl_deck_kaggle_20260619_gate.md`
  - `report/track_b_gates/track_b_learned_rl_deck_ramp_1m_20260620_gate.md`

Full public leaderboard rows were not available through the tested API/web routes.
The API did confirm our current competition metadata: Simulation competition ID
`116727`, `teamCount=2090`, `userRank=1219`, `maxDailySubmissions=5`, deadline
`2026-08-16T23:59:00Z`.

## Current Live Position

Fresh Kaggle API submission list as of 2026-06-20T02:29Z:

| Ref | Archive | Status | Score | Note |
|---:|---|---|---:|---|
| 53854707 | `a2_kyogre.tar.gz` | complete | 633.0 | Best submitted score; heuristic Kyogre |
| 53856711 | `track_a_probe_1.tar.gz` | complete | 626.0 | SearchScorer Kyogre+2e; stable second |
| 53856676 | `track_a_probe_2.tar.gz` | complete | 548.6 | SearchScorer Abomasnow+4e declined from prior sync |
| 53856584 | `track_b_learned_alakazam.tar.gz` | complete | 490.4 | Old buggy LearnedScorer probe |
| 53856590 | `track_b_learned_dragapult.tar.gz` | complete | 468.9 | Old buggy LearnedScorer probe |
| 53854588 | `a2_kyogre.tar.gz` | error | - | First package had `__file__` validation failure |

Current best local-not-yet-submitted package:

| Archive | Gate | Decision |
|---|---:|---|
| `track_b_learned_rl_deck_kaggle_20260619.tar.gz` | 210/240 = 87.5% | Best learned candidate; submit only with explicit user approval |
| `track_b_learned_rl_deck_ramp_1m_20260620.tar.gz` | 193/240 = 80.4% | Valid but weaker; keep for audit |

## What The Leaders Imply

We do not have full leaderboard rows, but our `userRank=1219` out of `2090`
teams and best score `633.0` make the gap clear: the top field is far above our
current ladder proof. The strongest local notes already observed that the field
top was around the 1300 range. A small heuristic tweak will not close that.

The main strategic lesson from our own ladder history is stronger:

1. Deck quality matters more than fancy policy code.
2. Local random win rate is only a filter; live ladder is truth.
3. Learned policies must be trained and distilled on the exact submitted deck.
4. More PPO steps are not automatically better; final-only packaging threw away
   stronger intermediate policies.

## Diagnosis

### 1. Final-only PPO packaging is wrong

The 1M ramp run had its best raw eval near 400k-500k:

- 400k: train 90%, holdout Kyogre 90%
- 440k: train 90%, holdout 85%
- 500k: train 90%, holdout 85%
- final 1M: train 80%, holdout 75%

We packaged only the final PPO policy, then distilled only that snapshot. That is
why 1M produced a lower gate than 100k.

Fix: checkpoint sweep. Distill and gate multiple saved checkpoints, then package
the best gate winner.

### 2. Distillation sample is too small

`scripts/distill_policy.py` defaults to `100` teacher episodes. The 100k report
had about 1592 teacher decisions; this is small for a stochastic, multi-context
card-game policy. With a weak distillation sample, a good teacher can become a
mediocre `.npz` submission model.

Fix: for serious candidates, distill with 300-1000 teacher episodes and compare
gate scores. Keep latency checks, but model size is tiny, so this should remain
fast at inference.

### 3. Benchmark pool is useful but not live-meta enough

`agent_decks/benchmark/suite.json` includes meta proxies and local high
performers. It does not yet include confirmed leader/live decks from logs or
fresh episodes. This makes training optimize the proxy pool, not necessarily the
leaderboard field.

Fix: mine public agent logs and official/episode datasets for archetypes beating
Kyogre; add them to `agent_decks/benchmark/suite.json` with weights.

### 4. Current active/final selection risk

Kaggle auto-select behavior can leave the best score disabled if the newest two
are not the best. Our best score is still Kyogre `633.0`; TA1 is `626.0`.

Fix: manually pin/select the best two final submissions in the Kaggle UI before
deadline. Do not rely on recency.

## Priority Plan

### P0 - Protect current best

- Keep `a2_kyogre.tar.gz` and `track_a_probe_1.tar.gz` as the current best live
  pair unless a new upload beats them.
- Manually select/pin Kyogre `633.0` and TA1 `626.0` as finals when appropriate.
- Do not submit the 1M ramp package; it is valid but weaker.

### P1 - Submit the fixed learned candidate as a ladder probe

Candidate:

`dist/candidates/track_b_learned_rl_deck_kaggle_20260619.tar.gz`

Reason:

- Gate `210/240 = 87.5%`, better than the 1M ramp `193/240`.
- It is the best learned candidate after reward fixes.
- It has no live ladder proof yet.

This should be treated as a probe, not a final replacement until its score moves
after ladder games.

### P2 - Build checkpoint-sweep training

Run shape:

1. Train fixed deck in 100k or 200k chunks.
2. After each chunk, copy `agent/models/rl_policy.zip` to a named checkpoint.
3. Distill each checkpoint using `--distill-episodes 300` initially.
4. Gate each distilled checkpoint with `--gate-games 40`.
5. Package only the best gate score.

Target checkpoints for the next Kaggle run:

- 100k
- 200k
- 300k
- 400k
- 500k
- 750k
- 1M

Based on the ramp curve, expect 400k-500k to beat final 1M.

### P3 - Increase distillation quality

For any checkpoint that gates well:

- rerun distill at 500 episodes
- optionally 1000 episodes if runtime is acceptable
- re-gate at 80 games if close to best

Only promote if gate beats `210/240`.

### P4 - Improve policy architecture only after data loop is fixed

Current `LearnedScorer` is a tiny one-hidden-layer option scorer over
hand-engineered features. It is fast but loses context. Before changing
architecture, fix checkpoint selection and distillation. If still stuck:

- Add context-specific heads or feature flags for select context.
- Train pairwise/ranking loss by option group instead of scalar imitation only.
- Add heuristic residual: score = learned + calibrated heuristic prior, so the
  model cannot forget obvious KOs/attachments.

### P5 - Live-meta benchmark update

- Fetch public logs for all current complete submissions when CLI/API support is
  available.
- Identify common loss causes and opponent archetypes.
- Add those decks to `agent_decks/benchmark/suite.json`.
- Retrain Track B on the updated benchmark and hold out Kyogre plus one live
  leader archetype.

## Next Concrete Work Item

Create a Kaggle checkpoint-sweep cell:

- 500k total by default, 100k chunks.
- Distill/gate every chunk.
- Keep `best_gate.json`.
- Collect all gate reports and the best package into one zip.

This directly fixes the failure mode from the 1M ramp run.
