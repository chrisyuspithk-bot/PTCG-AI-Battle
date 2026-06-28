# AGENTS — operating contract

> Auto repo state: see `REPO_STATE.md` (current snapshot) and `REPO_STATE_LOG.md` (daily history), regenerated each morning. Read REPO_STATE.md for where this repo stands right now.


The single operating contract for this repo (human or AI). Reset 2026-06-22 (Session 44). For the
*why* read `RULINGS.md`; for the *plan* read `ARCHITECTURE.md`; for *current state + next action*
read `STATE.md`. For the *forward plan* read `ROADMAP.md`. For *research + decisions* read
`report/RESEARCH_AND_DECISION_BRIEF.md`.

## Mindset (this governs everything — full version: `RULINGS.md` Part 0)
The errors that stalled 43 sessions were mindset errors, not bad luck. Hold these always:
1. **Measure; never assume** — verify load-bearing facts against the real engine/field/repeat reading.
2. **Simplicity wins; earn complexity** — every RL/MCTS/GA we built lost to plain rules/search.
3. **Pilot before deck; measure what we have before training something new.**
4. **The real field is the only judge** — never proxies, random, or mirror-only self-play.
5. **Ship nothing ungated**, and **finish/verify one thing before starting the next.**
6. **Ground decisions in math and the actual game** (imperfect-info POMDP on a TrueSkill ladder).

> If a plan violates one of these, stop and fix the plan — it outranks enthusiasm for any deck or model.

## Start every session by reading, in order
1. `STATE.md` — current state and the single next action.
2. **`eval/AGENT_CATALOG_FULL.md`** — what each of 21 ladder submissions actually was (brain × deck × training).
3. `report/RESEARCH_AND_DECISION_BRIEF.md` — measured evidence + decision framework.
4. `.cursor/SESSION.md` — ephemeral session focus (Cursor hook; continue prompt).
5. `RULINGS.md` — standing rulings (R1–**R12**). **Do not re-run ruled-out experiments.**
6. `ROADMAP.md` — now / next / not doing.
7. `ARCHITECTURE.md` — pillar design.
8. `TASKS.md` — build-order backlog; next unchecked item.

## The competition (verify specifics in `data/` source docs)
- **Simulation** (`pokemon-tcg-ai-battle`): submit `submission.tar.gz`; public **μ** is truth.
- **Strategy** (`pokemon-tcg-ai-battle-challenge-strategy`, ends 2026-09-14): stability + deck
  concept + sim performance + written report.
- **Imperfect-information** game; 10-min/player clock; μ updates on W/L/draw only (margin/speed do
  not count). Full facts: `RULINGS.md` Part 4 (cites `data/CABT_API.md`, `data/COMPETITION_SCORING.md`).

## Hard rules (the agent itself)
- **Never crash; always return a legal selection** from the simulator option mask — never infer
  legality from card text (Ruling R7). A single exception forfeits the game.
- **Keep ≥1 Basic on the bench** whenever legal (empty bench → `no_active` loss).
- Optimize **win probability + stability**, not blowout margin (Ruling R9).
- Keep RNG deterministic where we control it, so win-rate deltas are real.

## How we work (process)
- **Measure on the real field only** (Ruling R2): `eval/` harness vs `field/` decks + public
  agents. Never `pool_*` proxies or random/mirror self-play.
- **Nothing ML ships until it beats ladder evidence:** Dragapult bar **880.9 μ**; best home-grown Search **660.5 μ** on real-field harness filter + ≥2-reading ladder probe (R1, R3). **Local win-rate and weighted E[win] are not truth.**
- **Every reported win-rate carries metadata**: games, opponents, seeds, deck, brain (Ruling R8).
- **Don't break the spine.** `agent/` delivered SearchScorer **660.5 μ**; do not rename/refactor until smoke on Py≥3.11 (R7).
- **One source of truth per concern** (Ruling R10): decisions → `RULINGS.md`; state → `STATE.md`
  (+ `.cursor/SESSION.md` for ephemeral session); design → `ARCHITECTURE.md`. No new top-level
  handoff/instruction files.
- Improve one concrete behavior at a time, re-measure, keep only what improves the gate or fixes
  legality/stability.
- **Before train/upload:** name the catalog row in `eval/AGENT_CATALOG_FULL.md` you are extending or beating.
- **Weighted gates:** `field/weights.json` + `--weighted` — **filter only** until replay sample supports mixture (S49).
- **Rules before mixture (R11):** global deck rules → per-opponent levers → then field-mixture
  weighting for gates/training. See `TASKS.md` R1–R3.

## Before any Kaggle upload
- Read `data/SUBMISSION_PLAYBOOK.md`: **5 uploads/day**, **2 Final Submissions** (select manually).
- **Run the upload gate (required):**
  ```powershell
  python scripts/check_upload_eligible.py --manifest dist/candidates/<name>.manifest.json `
    --change "ONE LINE: concrete delta vs catalog row ref XXXXX" --local-gate <WR>
  ```
  Exit **1** → do not upload. Use `--suggest` for high-value next rows.
- **R12 — No duplicate brain×deck uploads.** Check `eval/AGENT_CATALOG_FULL.md`. If that row already
  has COMPLETE μ on ladder, **do not upload** unless you have a **material improvement** (new logic,
  deck, or levers) or it is **final lock-in** near deadline. Ports end at dry-run + local gate.
- Dry-run packaging first; never submit without explicit user confirmation **and** `check_upload_eligible` exit 0.

## Environment
- Engine + episode pull need **Python ≥3.11** and run on the user's machine (this sandbox is 3.10
  with no Kaggle egress). GPU work (if ever revived): the Python313 torch+cu128 interpreter.
- `pip install -r requirements.txt`. Kaggle creds under `.kaggle/` stay gitignored.
- End-of-session: prepend a dated block to `STATE.md` (state, files changed, measured result if any,
  blockers, the single exact next action). Update `.cursor/SESSION.md` when handing off in Cursor.
