# OFFICIAL GROUNDING RULE — Daily Task Foundation

**Established:** 2026-06-21  
**Purpose:** Every daily task, decision, and strategy must be grounded in official competition documents and community discussions.  
**Enforcement:** All work referencing rules, mechanics, timelines, or data must cite local official docs.

---

## 📋 Core Principle

**Every claim about competition mechanics, rules, deadlines, or data MUST be grounded in an official document.**

No assumptions. No inference. No "I think the rules say..."—**reference the actual doc.**

---

## 📚 Available Official Documents (Local)

### Rules & Mechanics (Frozen, Authoritative)
✅ `data/OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md`  
✅ `data/OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md`  
✅ `data/OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md` — **CRITICAL**  
✅ `data/OFFICIAL_WELCOME_DISCUSSION_708584_20260621.md`

### Timelines & Evaluation (Frozen)
✅ `data/OFFICIAL_OVERVIEW_SIMULATION_20260621.md`

### Data Schemas (Frozen)
✅ `data/OFFICIAL_DATA_RESOURCES_20260621.md`

### Reference Index
✅ `data/KAGGLE_OFFICIAL_REFERENCES_20260621.md` — Master URL index  
✅ `data/OFFICIAL_KAGGLE_REFERENCES_MANIFEST_20260621.md` — File manifest

---

## 🔴 What Still Requires Direct Access

These pages use JavaScript rendering or dynamic content—fetch fresh from Kaggle when needed:

- **Code Notebooks** (both competitions) — Must visit Kaggle directly to see latest notebooks
- **Discussion Threads** (main boards) — Continuously updated; check Kaggle for latest posts
- **Writeups** (Strategy) — User submissions; check Kaggle for new writeups
- **Leaderboard/Episodes** — Real-time data; not captured locally

**For these:** Link directly to Kaggle URL + note the fetch date in your work.

---

## 🎯 How to Apply This Rule

### Example 1: Deck Submission Question
❌ **Wrong:** "I think we can submit 5 decks to the Strategy competition"  
✅ **Right:** "Per `OFFICIAL_COMPETITION_RULES_STRATEGY_20260621.md`, Strategy is a hackathon with 1 submission only."

### Example 2: Simulator Behavior Question
❌ **Wrong:** "Official Pokémon TCG rules say simultaneous KO prize-taking is simultaneous"  
✅ **Right:** "Per `OFFICIAL_SIMULATOR_QUIRKS_DISCUSSION_20260621.md`, simulator behavior differs: next player takes first (sequential). Simulator behavior is official for this competition."

### Example 3: Timeline Reference
❌ **Wrong:** "The deadline is sometime in August"  
✅ **Right:** "Per `OFFICIAL_OVERVIEW_SIMULATION_20260621.md`, Final Submission Deadline is August 16, 2026."

### Example 4: Unknown Question
❌ **Wrong:** *Guess at the answer*  
✅ **Right:** "This isn't covered in our local official docs. Need to fetch fresh from Kaggle [URL]."

---

## 📥 Citation Format

When referencing official docs in daily work:

```
Per OFFICIAL_[DOCUMENT_TYPE]_[DATE].md:
[Quote or paraphrase with specific section]

Example:
Per OFFICIAL_COMPETITION_RULES_SIMULATION_20260621.md (Evaluation section):
"Each Submission has an estimated Skill Rating modeled by Gaussian N(μ, σ²)"
```

---

## 🔄 When to Re-fetch

**Fetch fresh from Kaggle if:**
- Rule changes are announced (check announcements)
- New discussions are posted (weekly check recommended)
- Discussion threads have new clarifications
- Strategy writeups are published (track for patterns)
- Bug fixes are released (simulator updates)

**Do NOT re-fetch:**
- Competition rules (frozen after competition starts)
- Baseline timelines (fixed by contract)
- Data schemas (fixed by competition design)

---

## 📊 Document Status Dashboard

| Document | Last Fetch | Authority | Update Freq |
|---|---|---|---|
| Simulation Rules | 2026-06-21 | Official | Never (frozen) |
| Strategy Rules | 2026-06-21 | Official | Never (frozen) |
| Simulator Quirks | 2026-06-21 | Official Host | As-needed (check weekly) |
| Overview | 2026-06-21 | Official | Never (frozen) |
| Data Resources | 2026-06-21 | Official | Never (frozen) |
| Discussions | 2026-06-21 | Community | Evolving (check weekly) |
| Code/Writeups | Not fetched | Community | Dynamic (check weekly) |

---

## 🚨 Violation Examples

These would break the grounding rule:

1. Deciding on strategy without checking RULES first
2. Claiming a rule exists that isn't in official docs
3. Making a decision based on "what we did before" without verifying it's still allowed
4. Ignoring simulator behavior differences vs official TCG
5. Submitting without confirming deadline in OFFICIAL_OVERVIEW
6. Building around a mechanic without checking OFFICIAL_SIMULATOR_QUIRKS

---

## ✅ Daily Checklist

Before proposing any strategy or decision:

- [ ] **Rules:** Check `OFFICIAL_COMPETITION_RULES_*.md`
- [ ] **Simulator:** Check `OFFICIAL_SIMULATOR_QUIRKS_*.md` (if about game mechanics)
- [ ] **Timeline:** Check `OFFICIAL_OVERVIEW_*.md` (if about deadlines)
- [ ] **Data:** Check `OFFICIAL_DATA_RESOURCES_*.md` (if about card/deck info)
- [ ] **Cite:** Reference the document in your writeup
- [ ] **Unknown?** Note it & queue a Kaggle fetch

---

## 🎓 Benefits of This Rule

1. **No miscommunication** — Everyone references the same source of truth
2. **No wasted effort** — Stops assumptions that turn out wrong mid-project
3. **Compliance ready** — Every decision is defensible with official grounding
4. **Fast decisions** — Docs are local; no need to hunt Kaggle when deciding
5. **Audit trail** — Future work can see exactly which rule each decision followed

---

**Enforcement starts:** 2026-06-21  
**Owner:** Dylan (user)  
**Last reviewed:** 2026-06-21
