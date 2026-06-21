# DAILY RUNBOOK — Scheduled Autonomous Runs

**Purpose:** Stand-alone instructions for EVERY autonomous session. Follow this framework regardless of where the project stands.

**Effective:** 2026-06-21 onward  
**Owner:** Dylan (user)  
**Mode:** Autonomous overnight/scheduled runs with human handoff points

---

## 🎯 STARTUP (First 5 minutes of each run)

### 1. Verify Folder Access

```bash
# Confirm workspace folder is mounted
ls -la Z:\kaggle\pokemon/

# If error: Request folder access immediately. Cannot proceed without it.
```

---

### 2. Read Situation Reports

**IN ORDER (read these files sequentially):**

```
1. PROGRESS.md (top entry only)
   ↓ What did last run do? Where are we?
   
2. TASKS.md (full file)
   ↓ What's the task queue? What's checked vs unchecked?
   
3. README.md (if unclear on context)
   ↓ What is this project? What's the competition?
```

**Output: You now know EXACTLY what the last run did and what task is next.**

---

### 3. Check Critical Status

**Question 1: Have we submitted to Kaggle yet?**
- [ ] NO → Continue building/testing offline (Task workflow phase)
- [ ] YES → Jump to MONITORING phase (below)

**Question 2: Is there an active submission on the ladder?**
- [ ] NO → Proceed to next task in queue
- [ ] YES → Capture leaderboard snapshot (see MONITORING)

---

## 📊 EPISODE DATA MINING PHASE (Daily — Before any new work)

**CRITICAL: Mine yesterday's battles to inform today's decisions.**

This is the FIRST phase of every run — before monitoring, before tasks.

---

### Setup: Kaggle API Access

**Verify token exists:**
```bash
ls -la Z:\kaggle\pokemon/.kaggle/kaggle.json
# If missing: Cannot fetch episodes. Mark task [blocked].
```

**Verify Python environment:**
```bash
pip list | grep kaggle
# If missing: Run scripts/setup_env.sh first
```

---

### Phase 1: Fetch Yesterday's Episode Data

**Script: `scripts/fetch_daily_episodes.py`**

```python
#!/usr/bin/env python3
"""
Fetch and parse battle episodes from yesterday
Output: JSON files with battle logs, decks, results
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Setup
competition = "pokemon-tcg-ai-battle"
output_dir = Path("data/episodes/daily_fetches")
output_dir.mkdir(parents=True, exist_ok=True)

# Determine yesterday's date
yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
fetch_path = output_dir / f"episodes_{yesterday}.json"

# If already fetched today, skip
if fetch_path.exists():
    print(f"Episodes for {yesterday} already fetched at {fetch_path}")
    exit(0)

print(f"Fetching episodes from {yesterday}...")

# Download episode dataset via Kaggle API
# NOTE: Episodes are published as a Kaggle dataset
# https://www.kaggle.com/datasets/kaggle/pokemon-tcg-ai-battle-episodes-index

os.system(f"""
kaggle datasets download -d kaggle/pokemon-tcg-ai-battle-episodes-index \\
  -p {output_dir} --unzip
""")

print(f"Episodes saved to {fetch_path}")
print(f"Next: Run scripts/analyze_episodes.py")
```

**Run:**
```bash
cd Z:\kaggle\pokemon
python scripts/fetch_daily_episodes.py
```

**Output:** `data/episodes/daily_fetches/episodes_YYYY-MM-DD.json` (battle logs)

---

### Phase 2: Parse & Analyze Episodes

**Script: `scripts/analyze_daily_episodes.py`**

```python
#!/usr/bin/env python3
"""
Parse yesterday's episodes and extract strategic insights
Output: Structured analysis + insights for decision-making
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

output_dir = Path("data/episodes/daily_fetches")
analysis_dir = Path("data/episodes/daily_analysis")
analysis_dir.mkdir(parents=True, exist_ok=True)

# Get yesterday's fetch file
yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
episodes_file = output_dir / f"episodes_{yesterday}.json"

if not episodes_file.exists():
    print(f"No episodes file found for {yesterday}. Run fetch_daily_episodes.py first.")
    exit(1)

print(f"Analyzing episodes from {yesterday}...")

# Load episodes
with open(episodes_file) as f:
    episodes = json.load(f)

# Parse battle data
battles = []
for episode in episodes:
    for battle in episode.get('battles', []):
        battles.append({
            'timestamp': episode.get('timestamp'),
            'player1_deck': battle.get('player1_deck_name'),
            'player2_deck': battle.get('player2_deck_name'),
            'winner': battle.get('winner'),  # 1 or 2
            'turns': battle.get('turns_taken'),
            'result': 'WIN' if battle['winner'] == 1 else 'LOSS'
        })

df = pd.DataFrame(battles)

# ========== ANALYSIS 1: Deck Frequency ==========
print("\n=== DECK META (yesterday) ===")
all_decks = pd.concat([df['player1_deck'], df['player2_deck']])
deck_freq = all_decks.value_counts()
print(deck_freq.head(10))

# Save to CSV
deck_freq.to_csv(analysis_dir / f"deck_frequency_{yesterday}.csv")

# ========== ANALYSIS 2: Win Rate by Deck ==========
print("\n=== WIN RATES BY DECK ===")
win_rates = {}
for deck in df['player1_deck'].unique():
    p1_battles = df[df['player1_deck'] == deck]
    if len(p1_battles) > 0:
        p1_wins = (p1_battles['winner'] == 1).sum()
        p1_wr = p1_wins / len(p1_battles)
        win_rates[deck] = {'wins': p1_wins, 'total': len(p1_battles), 'wr': p1_wr}

# Sort by frequency (at least 5 battles to count)
significant_decks = {d: wr for d, wr in win_rates.items() if wr['total'] >= 5}
sorted_decks = sorted(significant_decks.items(), key=lambda x: -x[1]['wr'])

for deck, stats in sorted_decks[:15]:
    print(f"  {deck}: {stats['wins']}/{stats['total']} ({stats['wr']*100:.1f}%)")

# Save win rates
with open(analysis_dir / f"win_rates_{yesterday}.json", 'w') as f:
    json.dump(significant_decks, f, indent=2)

# ========== ANALYSIS 3: Matchup Matrix ==========
print("\n=== TOP MATCHUPS (yesterday) ===")
matchups = {}
for _, row in df.iterrows():
    p1, p2 = row['player1_deck'], row['player2_deck']
    key = f"{p1} vs {p2}"
    
    if key not in matchups:
        matchups[key] = {'wins': 0, 'losses': 0}
    
    if row['winner'] == 1:
        matchups[key]['wins'] += 1
    else:
        matchups[key]['losses'] += 1

# Show top matchups
for matchup, results in sorted(matchups.items(), 
                               key=lambda x: x[1]['wins'] + x[1]['losses'], 
                               reverse=True)[:20]:
    total = results['wins'] + results['losses']
    wr = results['wins'] / total if total > 0 else 0
    print(f"  {matchup}: {results['wins']}-{results['losses']} ({wr*100:.0f}%)")

# ========== ANALYSIS 4: Speed Metrics ==========
print("\n=== GAME DURATION (turns) ===")
print(f"  Avg turns: {df['turns'].mean():.1f}")
print(f"  Median turns: {df['turns'].median():.0f}")
print(f"  Min: {df['turns'].min()}, Max: {df['turns'].max()}")

# ========== OUTPUT: Consolidated Report ==========
report = {
    'date': yesterday,
    'total_battles': len(df),
    'unique_decks': df['player1_deck'].nunique(),
    'top_decks': deck_freq.head(10).to_dict(),
    'win_rates': significant_decks,
    'avg_turns': float(df['turns'].mean()),
    'meta_summary': sorted_decks[:5]
}

with open(analysis_dir / f"daily_report_{yesterday}.json", 'w') as f:
    json.dump(report, f, indent=2)

print(f"\nAnalysis saved to {analysis_dir}/")
print(f"Next: Read daily_report_{yesterday}.json for insights")
```

**Run:**
```bash
python scripts/analyze_daily_episodes.py
```

**Outputs:**
- `data/episodes/daily_analysis/deck_frequency_YYYY-MM-DD.csv` — Deck meta %
- `data/episodes/daily_analysis/win_rates_YYYY-MM-DD.json` — Win % by deck
- `data/episodes/daily_analysis/daily_report_YYYY-MM-DD.json` — Consolidated summary

---

### Phase 3: Extract Insights → Inform Decisions

**Key questions answered by yesterday's data:**

1. **What decks are META?** (top 5 by frequency)
   - If Alakazam is <5% → Meta shifted; may need pivot
   - If Iono/Control > 30% → Our Alakazam faces hostile meta

2. **What has BEST win rate?** (min 5 battles to count)
   - Compare to our DECK_RANKING benchmarks
   - If new deck outperforming Alakazam → Investigate why

3. **What beats our submission?** (matchup matrix)
   - If specific deck beats us consistently → Plan counter
   - If we have bad MU → Consider variant or pivot

4. **How fast is the meta?** (avg turns)
   - If meta avg turns = 4.5 → We need speed to compete
   - If = 8 → Control/grind deck might work

---

### Phase 4: Log Findings in PROGRESS.md

**Add this to your run's PROGRESS.md entry:**

```markdown
### EPISODE DATA (Yesterday's date)
- **Total battles analyzed:** [N]
- **Unique decks in meta:** [N]
- **Top 3 decks by frequency:** [Deck A (%), Deck B (%), Deck C (%)]
- **Best win rate:** [Deck X: Y% (N battles)]
- **Avg game length:** [X turns]
- **Key finding:** [One-sentence insight]
- **Action triggered:** [If any decision gate opened]
```

---

## 📊 MONITORING PHASE (If submission is active)

**Do this AFTER episode mining, BEFORE starting new work:**

### Pull Current Leaderboard State

**What to capture (paste into PROGRESS.md at end of run):**

```
SUBMISSION PERFORMANCE (timestamp: YYYY-MM-DD HH:MM UTC)
- Submission name: [name]
- μ (skill rating): [value]
- σ² (uncertainty): [value]
- Episodes completed: [count]
- Win/loss record (visible): [W-L]
- Rank on leaderboard: [position]
```

**Source:** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard

---

### Apply Decision Gates (Based on current μ)

#### Gate A: Has submission CRASHED? (μ < 400)
- **Action:** Stop new submissions. Analyze what went wrong.
- **Next:** Debug submission; don't iterate.

#### Gate B: Is submission STABLE? (μ unchanged >8h)
- **YES** → Convergence achieved; safe to iterate
- **NO** → Let it run longer; skip new submissions today

#### Gate C: How many SUBMISSION SLOTS remain today?
- **0 slots left (5/5 used)** → Cannot submit; focus on analysis/code
- **1-4 slots left** → Can make strategic submission if gated decision says yes
- **5 slots available** → Full discretion; choose submission strategy

**Source:** `OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md` (5/day limit)

---

## ✅ TASK WORKFLOW (Sequential Backlog Model)

### Find First Unchecked Task

```
Open TASKS.md
Find first [ ] (unchecked) task
Read its full description
```

### Execute Task

**Do REAL work:**
- Write code (scripts, agents, utilities)
- Run experiments (local validation, gate testing)
- Analyze data (replays, win-rate breakdowns, metrics)
- Draft reports (strategy docs, analysis, findings)
- DO NOT: Just write notes or theories—execute and validate

### Mark Complete + Move Forward

```
[ ] Task 1 — Description
[x] Task 2 — Description (DONE)
[ ] Task 3 — Description (NEXT)
```

**Keep going through tasks in order until run budget is nearly exhausted.**

---

## 🚫 TASK BLOCKERS

**If a task is BLOCKED (can't complete due to external dependency):**

```
[blocked] Task X — Reason (e.g., "Awaiting user confirmation on Path A vs B")
```

**Then skip to NEXT UNBLOCKED TASK and continue.**

**Examples of valid blockers:**
- "Awaiting Kaggle API token configuration"
- "Awaiting user decision on Alakazam vs alternative deck"
- "Awaiting leaderboard convergence (μ not stable)"

**Examples of INVALID blockers (don't use these):**
- "Don't feel like doing it"
- "Seems hard"
- "Need to think about it"

---

## 🔍 DECISION FRAMEWORK (When uncertain, apply this)

### Hierarchy of Data Sources (apply in this order)

**Priority 1: Yesterday's Episode Data** (real ladder, real decks, real meta)
- Freshest, most representative
- Use to: Identify meta shift, validate our benchmarks, find new strategies
- Example: "Iono jumped to 40% of meta" → Our Alakazam gets harder

**Priority 2: Our PROGRESS.md Performance History** (our submissions, our ladder scores)
- Contextual, known environment
- Use to: Compare current μ to historical, spot trends
- Example: "Alakazam was 620 three days ago, now 640" → Convergence + improving

**Priority 3: Benchmarks (DECK_RANKING, STRATEGY_DECISION)** (curated, validated)
- Historical best-known data
- Use to: Validate new findings against known good values
- Example: "New deck gates 18%, old Trevenant gates 15%" → Marginal improvement

**Priority 4: Official Docs** (rules, mechanics, constraints)
- Immutable, foundational
- Use to: Ensure compliance, check limits
- Example: "Can we submit 10?" → No, 5/day limit (OFFICIAL_COMPETITION_RULES)

---

### Decision: Which Agent to Submit Next?

**Gate 1: What does YESTERDAY'S DATA say?**
```
Read: data/episodes/daily_analysis/daily_report_YYYY-MM-DD.json

Questions:
- Is our current submission's archetype in top 5 meta?  YES → confidence, hold / NO → meta shifted, consider pivot
- Is there a NEW deck in top 5 that outperforms our benchmark? YES → investigate, maybe test / NO → stay course
- Do we see consistent counters to our submission type? YES → plan variant / NO → proceed
```

**Gate 2: What does OUR LADDER say?**
```
Current μ vs forecast:
- μ > forecast + 30 → EXCEEDING: Hold submissions, let it run longer
- μ in forecast range → ON TRACK: Can iterate cautiously (test variant or archetype)
- μ < forecast - 30 → UNDERPERFORMING: Analyze why; prepare backup deck
```

**Gate 3: What's the TASK QUEUE say?**
```
Check TASKS.md:
- Do we have explicit "submit [deck]" task? → Execute it
- Do we have "analyze [data]" task? → Do episode mining, use findings to inform next task
- Uncertain? → Episode data informed next best guess? Default: Episode mining + analysis task
```

**EXAMPLE DECISION TREE:**

```
START: "What should we submit next?"
  ↓
Gate 1: Check daily_report_YESTERDAY.json
  ├─ New archetype in top 5? (e.g., "Lucario Control" jumped to 3rd)
  │   └─ YES → "Test Lucario variant" (different archetype = diversify risk)
  │   └─ NO → Continue
  ├─ Consistent counter to OUR type?
  │   └─ YES → "Build Alakazam v2 (counter-tech)" or "Test Trevenant (different archetype)"
  │   └─ NO → Continue
  ↓
Gate 2: Check current leaderboard μ for our submission
  ├─ μ > 640? → "Let it run; don't submit yet"
  ├─ μ 620–640? → "Safe to test archetype variant"
  ├─ μ < 600? → "Analyze failure; prepare Trevenant backup"
  ↓
Gate 3: Check TASKS.md
  ├─ Explicit task says "submit X"? → Do that
  ├─ Explicit task says "analyze Y"? → Do episode mining → use findings
  ├─ No explicit guidance? → Use Gate 1+2 result
  ↓
DECISION MADE: Submit [Deck] for Slot 2
```

---

### Is this decision TECHNICAL (code/experiment)?
→ **Ground in official docs + yesterday's episode data + our PROGRESS.md**
- Example: "Which deck to submit?" → 
  1. Check yesterday's episode data (meta? counters?)
  2. Check DECK_RANKING_20260621.md (benchmarks)
  3. Check our leaderboard (current μ says safe to iterate?)
  4. DECIDE based on data

### Is this decision STRATEGIC (which task next)?
→ **Follow TASKS.md order; skip only if blocked**
→ **But use episode data to INFORM task selection when flexible**
- Example: "Which analysis task next?" → If episodes show new archetype, prioritize that analysis

### Is this decision about TIMING (when to submit)?
→ **Apply monitoring gates (MONITORING PHASE) + episode data**
- Example: "Should we submit now?" → Episode data shows meta stable? Our μ converged? Gates pass → YES

### Is this decision about SUBMISSION CONTENT?
→ **Must cite official rules + performance benchmarks + yesterday's meta**
- Example: "Can we submit 5 agents?" → Check OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md (yes, 5/day)
- Example: "Which 5 agents?" → Check yesterday's episodes + our DECK_RANKING + PROGRESS.md performance

---

## 📝 LOGGING & DOCUMENTATION

### During the run:
- Keep notes in a scratch file (e.g., `SESSION.md` in `.cursor/` folder)
- Log decisions, findings, metrics as you go
- Don't wait until the end to remember what you did

### At END OF RUN (MANDATORY):

Append to top of `PROGRESS.md`:

```markdown
### YYYY-MM-DD (Session # — Brief description)
- **Worked on:** [Task 1, Task 2, Task 3 — what you actually did]
- **Completed:** [x] Task N, [x] Task N+1
- **Results:** 
  - [If submission: Current μ, σ², episodes]
  - [If code: Link to file, brief description]
  - [If analysis: Key finding in 1-2 sentences]
- **Blockers:** [List any tasks marked [blocked] with reasons]
- **NEXT (single exact action):** [One clear, specific next step for next run]
```

**Requirements:**
- Honest status (don't exaggerate what you completed)
- Specific metrics (not "it works"; say "μ=636.8, σ²=15.3")
- Clear next action (not "keep working"; say "Check Alakazam convergence +12h, then trigger replay analysis")

---

## 🎬 END-OF-RUN HANDOFF (ALWAYS DO THIS)

**Before session ends, ALWAYS:**

1. **Update PROGRESS.md** (dated entry at top)
2. **Update TASKS.md** (check marks reflect reality)
3. **Save all new files** to `Z:\kaggle\pokemon/`
4. **Verify files committed** (if git: `git status`)
5. **Leave SESSION.md** (optional scratch notes for continuity)

**NEVER end a run without logging progress.**

---

## 🤖 RL TRAINING WORKFLOW (Informed by Episode Data)

**When task is "Train RL agent on [archetype]" — use episode data to seed training.**

### Step 1: Identify Training Target (from episode data)

**Read yesterday's report:**
```bash
cat data/episodes/daily_analysis/daily_report_YYYY-MM-DD.json
```

**Identify opportunity:**
- Is a new archetype rising in meta? → Train policy on that deck type
- Is a specific matchup weak? → Train policy against that counter
- Is a proven deck underperforming in our hands? → Train RL variant of that deck

**Example:**
```json
"top_decks": [
  ["Alakazam", 0.62],
  ["Iono Control", 0.58],    ← Rising (was 4th yesterday)
  ["Trevenant", 0.51],
  ["Kyogre", 0.47]
]

Decision: "Iono Control rising — train RL policy for Control archetype"
```

---

### Step 2: Extract Winning Decks (for seed data)

**From episode matchup matrix, identify best-performing decks:**

```python
# File: scripts/extract_seed_decks.py
"""
Extract winning deck lists from yesterday's episodes
to seed RL training (copy winning structure)
"""

import json
from pathlib import Path

analysis_dir = Path("data/episodes/daily_analysis")
yesterday = "YYYY-MM-DD"  # Update to actual date

# Read win rates
with open(analysis_dir / f"win_rates_{yesterday}.json") as f:
    win_rates = json.load(f)

# Find top performers (>55% win rate, min 5 battles)
seeds = {}
for deck, stats in win_rates.items():
    if stats['wr'] > 0.55 and stats['total'] >= 5:
        seeds[deck] = {
            'winrate': stats['wr'],
            'battles': stats['total'],
            'deck_list': None  # Populate from episode logs if available
        }

# Save seed decks for RL training
with open("report/deck_rl/episode_seed_decks.json", 'w') as f:
    json.dump(seeds, f, indent=2)

print(f"Extracted {len(seeds)} seed decks for RL training")
```

**Run:**
```bash
python scripts/extract_seed_decks.py
```

---

### Step 3: RL Training Config (Based on Episode Insights)

**Create training config file:**

```yaml
# File: rl/training_config_YYYY-MM-DD.yaml

target_deck_type: "Iono Control"  # From episode data
training_episodes: 1000
batch_size: 32

reward_shaping:
  # Based on episode data: Control decks average 7.2 turns to win
  # Reward for: long games, stall, disruption
  turn_reward: +1 per turn (incentivize grinds)
  disruption_reward: +5 for Iono plays
  wall_setup_reward: +3 for active setup
  
seed_deck: "episode_seed_decks.json"  # Yesterday's best performers

validation:
  # Gate against meta from episodes
  min_winrate_vs_alakazam: 0.35
  min_winrate_vs_kyogre: 0.40
  min_winrate_vs_meta: 0.50 (vs top 5 decks)
```

---

### Step 4: Run RL Training

```bash
cd Z:\kaggle\pokemon

# Train with config informed by episode data
python rl/train_deck_campaign.py \
  --config rl/training_config_YYYY-MM-DD.yaml \
  --epochs 10 \
  --seed 42 \
  --output report/deck_rl/rl_variant_YYYY-MM-DD.tar.gz
```

---

### Step 5: Validate Against Episode Meta

**After RL training, test learned policy:**

```python
# File: scripts/validate_rl_vs_episode_meta.py
"""
Validate trained RL agent against yesterday's meta decks
"""

import json
from pathlib import Path

# Load episode data (meta decks)
analysis_dir = Path("data/episodes/daily_analysis")
with open(analysis_dir / "daily_report_YYYY-MM-DD.json") as f:
    meta_report = json.load(f)

# Load trained RL agent
rl_agent = load_agent("report/deck_rl/rl_variant_YYYY-MM-DD.tar.gz")

# Simulate against top meta decks
results = {}
for deck, stats in meta_report['meta_summary'][:5]:  # Top 5
    win_rate = simulate(rl_agent, deck, episodes=50)
    results[deck] = win_rate
    print(f"  vs {deck}: {win_rate*100:.1f}%")

# Decision gate
avg_meta_wr = sum(results.values()) / len(results)
if avg_meta_wr > 0.50:
    print("✅ RL agent competitive vs meta. Ready for submission.")
else:
    print("❌ RL agent weak vs meta. Needs more training or different approach.")
```

---

### Step 6: Log RL Training Result

**Add to PROGRESS.md:**

```markdown
### RL Training (Episode-Informed)
- **Seed deck type:** [Type from episode data]
- **Trained on:** [N episodes]
- **Val gate vs top 5 meta:** [X%] (target: >50%)
- **Decision:** [Ready for Slot 2? Or needs more work?]
```

---

## 📊 MONITORING PHASE (If submission is active)

**First run only (or if missing):**

```bash
cd Z:\kaggle\pokemon
bash scripts/setup_env.sh
```

This:
- Installs pip packages from requirements.txt (with --break-system-packages)
- Copies/verifies Kaggle token at `Z:\kaggle\pokemon/.kaggle/kaggle.json`
- Downloads competition data (if missing)

**Verify token exists:**
```bash
ls -la Z:\kaggle\pokemon/.kaggle/kaggle.json
# If missing: Kaggle operations (submit, pull replays) will be BLOCKED
```

---

## 📚 OFFICIAL DOCS (Ground All Decisions)

**Keep these available as reference:**

| Topic | Document | Use for |
|---|---|---|
| **Rules** | `OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md` | Submission limits, scoring, eligibility |
| **Rules (Strategy)** | `OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md` | Strategy competition format (1 submission only!) |
| **Simulator** | `OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md` | Behavior differences from official TCG |
| **Timeline** | `OFFICIAL_OVERVIEW_SIMULATION_20260621.md` | Deadlines (Aug 16 for Simulation, Sep 13 for Strategy) |
| **Data** | `OFFICIAL_DATA_RESOURCES_20260621.md` | Card schemas, metadata |
| **Deck benchmarks** | `report/DECK_RANKING_20260621.md` | Which decks are strongest (Alakazam 57.3%, Trevenant 15.3%, etc.) |
| **Strategy** | `report/STRATEGY_DECISION_20260621.md` | Why we chose Alakazam; known weaknesses |
| **Grounding rule** | `OFFICIAL_GROUNDING_RULE_20260621.md` | How to cite official docs in work |

**When uncertain about competition mechanics → Check these docs FIRST. Don't guess.**

---

## 🎯 COMMON WORKFLOWS (Copy-paste as needed)

### Workflow A: Monitoring Active Submission

```
1. Pull leaderboard (https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard)
2. Find your submission; note μ, σ², episodes
3. Compare to previous run's metrics
4. Apply decision gates (convergence? crashed? safe to iterate?)
5. Log in PROGRESS.md
```

### Workflow B: Pulling Replay Data

```bash
# Verify token exists
ls -la Z:\kaggle\pokemon/.kaggle/kaggle.json

# Run replay-fetch script (when ready)
cd Z:\kaggle\pokemon
python scripts/fetch_alakazam_replays.py  # (or relevant submission)
```

See `MASTER_INSTRUCTIONS_POST_SUBMISSION_20260621.md` (Phase 2) for full replay analysis setup.

### Workflow C: Building & Testing New Deck

```
1. Create deck file (CSV format, 60 cards)
2. Validate legality: python scripts/validate_deck.py --deck deck.csv
3. Build submission bundle: tar -czvf submission.tar.gz [files]
4. DRY RUN: Test locally with simulator
5. If passes: Log in PROGRESS.md as ready for submission
6. Wait for human approval before upload to Kaggle
```

### Workflow D: Submitting to Kaggle

```
ONLY if:
- [ ] Task explicitly says "submit"
- [ ] Submission has been validated (dry-run passed)
- [ ] μ decision gates allow it (not crashed, convergence OK)
- [ ] Haven't used all 5 daily slots yet

Then:
1. Run: python scripts/upload_to_kaggle.py --submission submission.tar.gz
2. Log submission ID in PROGRESS.md
3. Start monitoring (Workflow A)
```

---

## 🚨 GUARDRAILS (Non-negotiable)

1. **DO NOT submit without explicit task approval** — Only submit if current task says "submit"
2. **DO validate before submitting** — Deck legality, tar structure, API format
3. **DO ground decisions in official docs** — Don't assume; check the rules
4. **DO log your work** — Every run ends with PROGRESS.md entry
5. **DO respect submission quotas** — 5/day (Simulation), 1 total (Strategy)

---

## 📅 TYPICAL RUN TIMELINE

### +0 min: Startup
- Verify folder access
- Read PROGRESS.md, TASKS.md
- Check monitoring gates

### +0–15 min: EPISODE DATA MINING (CRITICAL — DO FIRST)
- Run `scripts/fetch_daily_episodes.py` (yesterday's data)
- Run `scripts/analyze_daily_episodes.py` (parse meta)
- Read `data/episodes/daily_analysis/daily_report_YYYY-MM-DD.json`
- Log findings in PROGRESS.md (meta composition, win rates, key insights)
- Use findings to INFORM next task selection

### +15–45 min: Task Execution (Informed by Episode Data)
- Find first [ ] task in TASKS.md
- Use episode insights to guide implementation (e.g., "train RL on rising archetype")
- Real work (code, experiment, analysis)
- Mark complete in TASKS.md

### +45–75 min: Execute 2nd Task (If time permits)
- Continue task workflow
- Repeat until blocked or time-limited

### +75–90 min: Validation & Logging
- Update PROGRESS.md with:
  - Episode data findings (meta, win rates, insights)
  - Tasks completed (with results)
  - Current leaderboard status (if submission active)
  - Decisions made (informed by which data sources?)

### +90 min: Handoff
- PROGRESS.md updated with:
  - Summary of episode data analyzed
  - Summary of tasks completed
  - Next action (e.g., "Wait for Alakazam convergence +12h, then run replay analysis")
- TASKS.md reflects completed work
- All files saved to Z:\kaggle\pokemon/

---

## ✅ PRE-RUN CHECKLIST

**Before each scheduled run starts, verify:**

- [ ] Folder accessible: `Z:\kaggle\pokemon/`
- [ ] Python env has dependencies: `pip list | grep kaggle`
- [ ] Kaggle token exists: `ls -la .kaggle/kaggle.json`
- [ ] PROGRESS.md readable (last entry < 24h old)
- [ ] TASKS.md has clear next task
- [ ] No critical blockers from previous run

**If ANY of these fail, fix before proceeding.**

---

## 📞 ESCALATION (When to stop and wait for human)

**Stop and escalate if:**

- Leaderboard submission CRASHED (μ dropped >100 points suddenly)
- Cannot authenticate to Kaggle API (token missing/invalid)
- Task requires user decision (e.g., "Path A vs Path B")
- Folder access lost mid-run
- Ambiguity about which task is actually "next"

**In escalation:**
1. Log issue in PROGRESS.md (mark task [blocked])
2. Leave clear summary of what went wrong
3. Await human instruction before resuming

---

## 🎓 PHILOSOPHY

**This is a sequential backlog system:**
- PROGRESS.md = history of what happened
- TASKS.md = queue of what's next
- Each run handles 1–3 tasks, logs findings, passes to next run
- Decisions are grounded in official docs + empirical data
- No guessing; no assumptions; cite sources

**Success = clear handoff between runs, verified progress, auditable decisions.**

---

**Runbook created:** 2026-06-21  
**Effective date:** 2026-06-21 onward  
**Owner:** Dylan (user)  
**Mode:** Autonomous daily runs with human escalation points

---

## 🚀 FIRST THING NEXT RUN

1. Read this file (you're here!)
2. Read PROGRESS.md top entry
3. Read TASKS.md
4. Find first [ ] task
5. Execute it
6. Repeat until budget exhausted
7. Log PROGRESS.md entry
8. Handoff

**Go!**
