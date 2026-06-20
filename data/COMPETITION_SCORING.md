# Simulation ladder scoring — how agents get μ

**Competition:** `pokemon-tcg-ai-battle` (Simulation). Strategy track is separate.

Ground truth for rank is **public μ** on the leaderboard after enough ladder episodes.
Local win-rate gates **filter only**. See also [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md),
[`PROJECT_PRIORITIES.md`](PROJECT_PRIORITIES.md), [`SIMULATOR_RESOURCE_NOTES.md`](SIMULATOR_RESOURCE_NOTES.md).

Source: Kaggle competition **Evaluation** page (fetched via `kaggle competitions pages pokemon-tcg-ai-battle --content`).

---

## What you see after upload

| Phase | What happens | μ meaning |
|-------|----------------|-----------|
| **Upload** | Package validated | — |
| **Validation episode** | Agent plays **a copy of itself** | Pass → proceed; fail → **ERROR** (download logs) |
| **COMPLETE (~instant)** | Enters ladder pool | **μ ≈ 600** starting rating (not field performance) |
| **~40+ min** | Matchmaking vs similar-μ agents | μ moves with **W/L/draw** |
| **Ongoing** | All uploads keep playing; newer agents get **more episodes** | μ drifts as σ (uncertainty) shrinks |
| **Deadline + ~2 weeks** | Final evaluation window | Leaderboard locks |

**Do not treat μ=600 on COMPLETE as failure** — it is the initialized skill estimate after validation.

---

## Official rating model (Kaggle)

Each submission has skill modeled as a **Gaussian** **N(μ, σ²)**:

- **μ** — estimated skill (leaderboard number, e.g. 633.0)
- **σ** — uncertainty (decreases as more episodes complete)

After each **episode** (one game vs one opponent submission):

| Result | μ update |
|--------|----------|
| **Win** | Your μ **increases**; opponent μ **decreases** |
| **Loss** | Your μ **decreases**; opponent μ **increases** |
| **Draw** | Both μ values move **toward their mean** |

Update **magnitude** depends on:

- How surprising the result was vs pre-game μ (upset vs expected)
- Each side’s current **σ** (early agents move more per game)

### Official: margin and speed do NOT change μ per episode

> *“The score by which your agent wins or loses an Episode does not affect the skill rating updates.”*

So **turn count, prize margin, and “how badly” you lost** are **not** direct inputs to the μ formula.

---

## Why tempo still matters (operational)

Even though **one episode’s μ delta is W/L/draw only**, agents that **collapse quickly** still end up with **bad μ** because:

1. **A fast loss is still a loss** — each `deck_out`, `no_active`, or prize blowout costs μ the same as a slow loss *for that episode*.
2. **Weak agents lose more episodes** — if you die in 8 turns vs 40, you may play **more games per hour** and rack up **more losses** before σ stabilizes.
3. **New agents get heavy episode volume** — early bugs (empty bench, illegal stalls) show up fast in μ.
4. **Matchmaking is μ-based** — sustained losses drag μ down; you face a different opponent mix, not a separate “speed penalty.”

**Project policy:** still optimize for **bench depth**, **avoid deck-out / no_active**, and **close winning games cleanly** — not because Kaggle adds a turn bonus, but because those failures are **losses** and happen **often** on weak agents.

Log from replays/logs: `turns`, `result reason`, `prize` differential — see [`KAGGLE_SIMULATION_CLI.md`](KAGGLE_SIMULATION_CLI.md).

---

## Leaderboard rules that affect strategy

| Rule | Implication |
|------|-------------|
| **5 uploads / team / day** | Probes OK; don’t waste slots on ungated agents |
| **2 Final Submissions** | **Manually select** best two μ agents before deadline |
| **Latest-2 tracking (observed)** | Auto-select may ignore your best μ if it isn’t recent |
| **Best μ shown on leaderboard** | All submissions keep playing; track each on Submissions tab |
| **Similar-μ matchmaking** | Beating strong agents moves μ more when σ is low |
| **No private LB** | Public μ is the only rank signal |

Protected baselines (our field): Kyogre heuristic **633**, TA1 Search **626** (2026-06-20).

---

## Agent design priorities (scoring-aware)

### 1. Never crash; always legal options

Validation fails → **ERROR**, no ladder. Runtime errors in episodes → losses + log review.

Use simulator **legal mask only** — see [`SIMULATOR_RESOURCE_NOTES.md`](SIMULATOR_RESOURCE_NOTES.md).

### 2. Bench ≥1 Basic whenever possible

Empty bench → active KO → **`no_active` loss** → μ drop. Implemented in:

- `agent/agent.py` (HeuristicScorer)
- `agent/rule_core.py` (RuleCoreScorer)
- `agent/evalfn.py` (search leaves + RL shaping)

### 3. Gate before upload

| Level | Games | Purpose |
|-------|-------|---------|
| L0 | smoke 17/17 | Contract |
| L1 | 12 × pool | Fast filter |
| L2 | 40 × pool | Package threshold |
| Public | 30–100 × suite | Best predictor of ladder (see `report/competition_insights.md`) |

Local pool WR **does not** predict μ; public-agent gate is closer.

### 4. Two training tracks (do not mix)

| Track | Brain | Deck |
|-------|-------|------|
| Lucario RL+MCTS | `model_best.pth` | `real_mega_lucario_ex.csv` |
| Track B Learned | `distilled_<slug>_v1.npz` | **Same deck as training** |

---

## Training implications

| Loop | Scoring-aware note |
|------|-------------------|
| **Track A (Search/RuleCore)** | Primary path to 600+ μ; opponent-archetype guards matter |
| **Track B (Learned)** | Per-deck train+distill; old Alakazam distill ≈490 μ |
| **Lucario RL** | vs-random training ≠ ladder; need iters + public gate |
| **Deck RL** | Deck fitness ≠ μ; pair with strong brain |

**RL reward:** terminal ±1 win/loss in `rl/cabt_env.py`; shaping via `board_value()` (prize, bench, turn pressure). Shaping does **not** need to mimic Kaggle μ — it should reduce **loss modes** that hurt episode WR.

---

## Measurement checklist (every submit)

1. Submission ref + description
2. μ at COMPLETE vs μ after **40+ min**
3. `kaggle competitions episodes <ref> -v` — episode count, opponents
4. Worst episodes → `replay` + `logs` — turn count, loss reason
5. Record in `report/ladder_history.csv`

---

## Related docs

- [`KAGGLE_SIMULATION_CLI.md`](KAGGLE_SIMULATION_CLI.md) — episodes, replays, logs, scouting
- [`SUBMISSION_PLAYBOOK.md`](SUBMISSION_PLAYBOOK.md) — daily limit, Final Submissions, disabled tooltip
- [`PROJECT_PRIORITIES.md`](PROJECT_PRIORITIES.md) — always-on checklist
- [`SIMULATOR_RESOURCE_NOTES.md`](SIMULATOR_RESOURCE_NOTES.md) — simulator ≠ official TCG; episode datasets
