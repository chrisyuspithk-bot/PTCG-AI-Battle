# Mega Lucario ex — SmartBench + Meta Tactics Report

Date: 2026-06-20  
Deck: `agent_decks/real_mega_lucario_ex.csv`  
Candidate tarball: `dist/candidates/track_c_lucario_rulecore_smartbench.tar.gz`  
Scorer: `LucarioScorer` + `bench_guard` + `smart_bench`

---

## Executive summary

We rebuilt the Lucario ladder agent around three fixes: **(1)** never skip the first
bench basic (empty-bench fast losses), **(2)** search/energy to find and feed Riolu
→ Mega Lucario ex early, and **(3)** competitive meta lines from official Mega
Lucario ex strategy (Solrock/Lunatone engine, Aura Jab accel, prize-aware
Brave/Hariyama/Solrock).

**Result:** mirror matchups improved materially (**43.3%** vs the official Lucario
sample at 30 games), but **overall L1 public gate remains ~10%** — strong Lucario
setup, weak cross-archetype play without sim search. **Do not replace Search Lucario
(668 μ, ref 53869254) on Finals** until a Search + Lucario hybrid beats it on L1
and L4 episode stats.

---

## Background: why we changed course

| Ref | Scorer | μ | Problem |
|-----|--------|---|---------|
| **53869254** | SearchScorer | **668** | Best proven Lucario; generic heuristic MAIN + search on setup/switch |
| **53886522** | LucarioScorer + SmartBench | **600** | Submitted to fix empty-bench losses; too few L4 episodes so far |
| **53885445** | LucarioMCTSScorer (RL iter-0) | **324** | Retired — Yuki_Kaneko replay: Makuhita active, Riolu in hand, **0 bench** → `no_active` |

μ alone hid the RL failure mode. Episode-level stats (win rate, avg turns,
`fast_loss_pct`, loss reason) are required before trusting any Lucario upload.

---

## Architecture (current SmartBench build)

```
Agent.act
  ├─ bench_critical? → LucarioScorer     (must bench first backup)
  ├─ setup bench     → smart 1–2 depth   (not fill-all-3)
  └─ else            → LucarioScorer     (MAIN, attack plan, trainers)
```

**Key modules**

| File | Role |
|------|------|
| `agent/lucario_policy.py` | Official sample attack plan + meta tactics (below) |
| `agent/bench_guard.py` | Route empty-bench / setup-bench to Lucario |
| `agent/smart_bench.py` | Min 1, max 2 voluntary bench basics |
| `agent/agent.py` | Never-crash wrapper; bench routing for all scorers |

---

## Meta tactics incorporated (sources)

Grounded in [Pokemon.com Mega Lucario ex deck strategy](https://www.pokemon.com/us/strategy/pokemon-tcg-deck-list-and-strategy-building-a-mega-lucario-ex-deck) and League Battle Deck guidance.

### Early game — engine + line

- **Solrock + Lunatone** — prioritize completing the pair on bench/setup; Lunatone
  ability boosted when Solrock is in play and discard is thin (fuel for Aura Jab).
- **Search trainers** — Dusk Ball / Poké Pad when no Riolu line; Fighting Gong /
  Premium Power Pro when line needs energy; Lillie early when engine missing.
- **Riolu line** — bench Riolu first backup; attach to 2 energy; evolve to Mega
  Lucario ex before over-committing to wall lines.

### Mid game — prize trade (competitive pattern)

- **Solrock Cosmic Beam (70)** — prefer vs low-HP, single-prize targets.
- **Aura Jab (982)** — 130 damage + discard-to-bench accel; favored when discard
  has Fighting energy and bench needs power (Hariyama second attacker).
- **Mega Brave (983)** — 270 damage; plan only on **2+ prize** KOs; skip Brave on
  1-prize targets above 130 HP.
- **Hariyama** — evolve Makuhita when gust target exists (Heave-Ho); 210 damage
  line for ex prizes; energy from Jab accel.
- **Premium Power Pro** — high priority on planned KO / Brave turns (stacks in sim).
- **Gravity Mountain** — play when opponent has Stage 2 in play (−30 HP in sim).
- **Mega Brave cooldown** — retreat + Switch scored up when Brave unavailable but
  another Brave turn is planned later.

### Deliberately not done

- **Blanket END-over-ATTACK** when bench empty and no PLAY — rejected; END does not
  fix empty bench and stalls tempo. Guard only forces **PLAY when legal**.

---

## Measurement results

### L0 (legal + bench golden tests)

```bash
python scripts/smoke_test.py      # 17/17
python scripts/smoke_replay.py    # 12/12
```

### L1 public gate (`gate_vs_public.py`)

Candidate: `track_c_lucario_rulecore_smartbench.tar.gz`

| Games/opponent | Suite mean | vs Lucario sample | Notes |
|----------------|------------|-------------------|-------|
| 12 | 9.7–11.1% | 25–42% | High variance |
| **30** | **10.0%** (36/360) | **43.3%** (13/30) | Mirror gain holds |

**30-game per-matchup snapshot**

| WR | Opponent |
|----|----------|
| **43.3%** | `a-sample-rule-based-agent-mega-lucario-ex-deck` |
| 23.3% | Dragapult ex sample |
| 13.3% | Abomasnow sample, Dragapult tempo |
| 6.7% | Lucario **search** baseline, Alakazam |
| 0–3.3% | Iono, Crustle bot, anti-wall, 1084 baseline, public-scores-915 |

### Local self-play (sanity only, not ladder truth)

| Matchup | n | Win rate | Avg turns |
|---------|---|----------|-----------|
| Lucario vs heuristic | 24 | 54–62% | ~13 |

### L4 (Kaggle episodes — prior refs)

| Ref | win_rate | avg_turns | fast_loss_pct |
|-----|----------|-----------|---------------|
| 53869254 (Search) | 48.5% (33 ep) | 13.4 | 58.8% |
| 53886522 (SmartBench) | 50% (2 ep) | 10.5 | 100% |

Re-run after next upload: `python scripts/analyze_submission.py --ref <ref>`

---

## Why mirror is ~43% but overall is ~10%

**Mirror (~43%):** SmartBench + meta tactics fix Lucario-specific openings and
prize sequencing against a similar deck — find Riolu, feed energy, Solrock/Lunatone,
Jab → Hariyama/Brave lines.

**Overall (~10%):** Public field agents win on **lookahead and cross-deck
decisions** — promotion, switch, gust timing, tempo vs spread/walls. Our **668 μ**
agent uses **`SearchScorer`** (sim search on setup/switch) with a **generic heuristic
MAIN**. SmartBench uses **`LucarioScorer` only** — better MAIN for Lucario, no
search layer. We improved half the stack; the other half carried ladder rating.

**One sentence:** setup and mirror play got better; whole-game skill vs diverse
opponents did not, because search-backed promotion/switch is still missing.

---

## Recommended combined stack (next build)

Target: **`LucarioSearchScorer`** — merge 668 μ search with SmartBench Lucario MAIN.

```
Agent.act          → bench_guard (unchanged)
Card contexts      → cg search_* (200 ms budget) — setup, switch, to active
MAIN               → LucarioScorer — meta, Jab/Brave, Gong, PPP, evolve
```

**Ship gate:** L1 @ 30 games vs public field; must beat Search Lucario local benchmark
(~29% note on 53869254) before replacing Finals slot.

**Portfolio (unchanged):**

- **Final 1:** 53869254 (Search Lucario, 668 μ) until hybrid proves better.
- **Experimental upload:** SmartBench or hybrid only with user OK; 5 uploads/day.
- **Lucario RL:** blocked until notebook iter ≥ 4; see `report/handoffs/lucario_rl_reimport_status.md`.

---

## Commands reference

```bash
# Package + L0/L1 gate (12 games default)
python scripts/package_submission.py \
  --name track_c_lucario_rulecore_smartbench \
  --scorer lucario \
  --deck agent_decks/real_mega_lucario_ex.csv \
  --gate

# Stable L1 (30 games per opponent)
python scripts/gate_vs_public.py \
  --agent dist/candidates/track_c_lucario_rulecore_smartbench.tar.gz \
  --games 30

# Local replay + stats
python scripts/record_local_battle.py \
  --agent-a lucario --agent-b search \
  --deck-a agent_decks/real_mega_lucario_ex.csv \
  --games 24 --seed 42

# Post-upload episode analysis
python scripts/analyze_submission.py --ref <submission_ref>
```

---

## Files changed (this Lucario pass)

- `agent/lucario_policy.py` — search/energy trainers, meta attack plan, Jab/Brave IDs
- `agent/bench_guard.py`, `agent/smart_bench.py`, `agent/agent.py`
- `scripts/smoke_replay.py` — 12 golden tests
- `report/submission_log.csv`, `report/FINALS_PIN.md`
- `data/KAGGLE_SIMULATION_CLI.md` §8–9, `data/EVAL_PROTOCOL.md`

---

## Exact next action

Implement **`LucarioSearchScorer`** (Search fallback = LucarioScorer on Lucario
deck), package `track_a_lucario_ex_search_v2`, run **L1 @ 30 games**, compare to
53869254 baseline; pin Finals only if L1 and L4 improve.
