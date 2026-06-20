## Imported Claude Cowork project instructions

# Project Rules

This folder is the single source of truth for the Kaggle competition project:
`Z:\kaggle\pokemon`.

## Competition
- **Simulation (ladder / agents):** [pokemon-tcg-ai-battle](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle) — submit tarballs; μ is truth.
- **Strategy (report):** [pokemon-tcg-ai-battle-challenge-strategy](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy) — deadline September 14, 2026.

## Read before RL, gates, or Simulation upload
1. [`data/PROJECT_PRIORITIES.md`](data/PROJECT_PRIORITIES.md) — dual tracks, GPU path, tempo/bench policy.
2. [`data/SIMULATOR_RESOURCE_NOTES.md`](data/SIMULATOR_RESOURCE_NOTES.md) — **simulator behavior is ground truth** (not official TCG rules).
3. [`data/COMPETITION_SCORING.md`](data/COMPETITION_SCORING.md) — **how μ works** (Gaussian rating, validation @600, W/L updates; avoid loss modes).
4. [`data/KAGGLE_SIMULATION_CLI.md`](data/KAGGLE_SIMULATION_CLI.md) — episodes, replays, logs, scouting.
5. [`data/SUBMISSION_PLAYBOOK.md`](data/SUBMISSION_PLAYBOOK.md) — 5 uploads/day; 2 Final Submissions.

## Environment
- Re-run environment setup at the start of a run when possible: `scripts/setup_env.sh`.
- On Linux, use `pip install --break-system-packages` through the setup script.
- On Windows, if pip rejects `--break-system-packages`, run `python -m pip install -r requirements.txt` and log the setup-script incompatibility.
- **Windows GPU RL:** use `C:\Users\tobin\AppData\Local\Programs\Python\Python313\python.exe` (torch+cu128, RTX 4070 Ti SUPER). **Do not** use miniconda3 default python for Track B — it installs `torch+cpu` only.
- Kaggle credentials are expected under `.kaggle/` and must stay gitignored.
- Work with Kaggle Grand Champion expectations: verify assumptions, measure changes, and keep the agent legal and deterministic.
- Start each run by reading `PROGRESS.md` and `TASKS.md`. The top `PROGRESS.md` entry is the latest handoff; the first unchecked task in `TASKS.md` is the next task.
- Read `README.md` when project context is needed.
- Work tasks in order. Complete real work in this folder, mark completed tasks `[x]`, and continue to the next task when time allows.
- If a task is blocked, mark it `[blocked]` with a one-line reason, log it in `PROGRESS.md`, and move to the next task that can be done offline.
- Before ending a run, prepend a dated `PROGRESS.md` entry with tasks worked, files changed, current best win-rate if measured, blockers, and the single exact next action.

## Environment
- Re-run environment setup at the start of a run when possible: `scripts/setup_env.sh`.
- On Linux, use `pip install --break-system-packages` through the setup script.
- On Windows, if pip rejects `--break-system-packages`, run `python -m pip install -r requirements.txt` and log the setup-script incompatibility.
- Kaggle credentials are expected under `.kaggle/` and must stay gitignored.
- If Kaggle access is unavailable, continue with offline work: code, harnesses, card analysis, report drafting, and local self-play.

## Verification
- Ground competition-specific facts in official competition docs, official cabt docs, or downloaded competition artifacts. Label assumptions clearly in `PROGRESS.md`.
- Do not submit to Kaggle or perform external irreversible actions unless an explicit task calls for it. For first submission work, dry-run packaging first and leave actual submission for user confirmation.
- **Testing workflow:** read [`data/EVAL_PROTOCOL.md`](data/EVAL_PROTOCOL.md) — three loops (Search / Policy RL / Deck RL), test pyramid L0–L4, brain×deck matrix.
- **Before every Simulation upload:** read [`data/SUBMISSION_PLAYBOOK.md`](data/SUBMISSION_PLAYBOOK.md). **5/day uploads**; **2 Final Submissions** for judging (§2.2 — select manually); “disabled” ≠ timeout.
- Keep RNG deterministic where the code controls randomness so win-rate comparisons are fair.
- Use local self-play as a sanity filter, not final ladder truth. Record game counts and matchup definitions with every reported win-rate.

## Agent Priorities
- The agent must never crash and must always return legal selections from the **simulator option mask** — never infer legality from card text alone (see `SIMULATOR_RESOURCE_NOTES.md`).
- **Always keep ≥1 Pokémon on bench** when legal (setup + MAIN); empty bench → fast ladder losses.
- Optimize for **episode wins** and **avoid loss modes** (deck-out, no_active, empty bench) — Kaggle updates μ on W/L/draw per episode, not turn margin (see `COMPETITION_SCORING.md`).
- Prefer simple strategies that the rule-based pilot can execute reliably.
- Improve one concrete behavior at a time, re-measure, and keep only changes that improve the current benchmark or clearly fix legality/stability.

## Operating Contract
