# Simulation submission playbook

Competition: `pokemon-tcg-ai-battle` (Simulation ladder).  
**Official rules source:** Kaggle Competition Rules §2.2, §3.18(c), §3.10 (user pasted 2026-06-19).

Strategy track (`pokemon-tcg-ai-battle-challenge-strategy`) is separate.

---

## The two limits (official language)

From **§2.2 SUBMISSION LIMITS**:

| Rule | Official text | Plain English |
|------|---------------|---------------|
| **Daily uploads** | “You may submit a maximum of **five (5) Submissions per day**.” | You can **upload 5 new agents per day**. Hard cap. |
| **Final Submissions** | “You may select up to **two (2) Final Submissions for judging**.” | Only **2** of all your uploads are your **Final Submissions** — the ones used for **final leaderboard placement**. |

From **§3.18(c) — “Final Submission”**:

> The Submission **selected by the user**, or **automatically selected by Kaggle** in the event not selected by the user, that is/are used for **final placement on the competition leaderboard**.

So:

- **All 5 daily uploads can COMPLETE**, play ladder games, and show a **public μ** during the competition.
- **Only 2** are your **Final Submissions** at any time (for official final standing).
- Kaggle UI **“Disabled due to the competition's active submission limit”** = this upload is **not** one of your two Final Submissions. It is **not** a timeout, ERROR, or “you uploaded too many today.”

**You were right that 5 can all go live.** What’s limited to 2 is which ones count as **Final Submissions for judging**, not how many can run on the ladder.

---

## How Final Submissions get chosen

1. **You select them** on the Kaggle submissions page (check/pin your two picks), **or**
2. **Kaggle auto-selects** if you don’t — observed behavior: **two most recent** COMPLETE uploads become the active Final pair; older ones show “disabled.”

**Action item:** Before deadline, **manually select** your best two (e.g. Kyogre 633.0 + TA1 625.7) so Kaggle doesn’t auto-pick your last two uploads if those aren’t your best.

---

## Sliding window (observed when not manually selected)

Upload order (2026-06-19, 5/5 daily quota used):

```
#1 Kyogre heuristic     μ 633.0  →  not a Final (disabled after #3)
#2 Alakazam Learned     μ 490.4  →  not a Final
#3 Dragapult Learned    μ 468.9  →  not a Final
#4 TA2 Search Abomasnow μ 580.2  →  Final slot (2nd most recent)
#5 TA1 Search Kyogre+2e μ 625.7  →  Final slot (most recent)
```

Auto-selected Finals: **#5 + #4**. Best μ overall (**#1 Kyogre 633.0**) was disabled because it wasn’t manually selected and wasn’t in the auto top-2 recency window.

---

## Other official notes (§3.10, §2.2)

- **Scoring:** Submissions scored on episode performance; performances aggregated for leaderboard position. **No Private Leaderboard** in Simulation competitions.
- **Team size:** max 5 members.
- **Team merge:** combined submission count must stay ≤ (submissions/day × days competition has run).

---

## μ during the competition

- **~600.0 right after COMPLETE** = validation self-play baseline, **not failure** (§3.10 + our probes).
- **~40+ min later** = ladder matchmaking updates μ from W/L vs field.
- μ can drift as more games finish (e.g. 672.7 → 633.0 on Kyogre).
- Local random-gate win % does **not** predict ladder rank.

---

## Pre-submit checklist

1. Dry-run: `python scripts/package_submission.py --name … --scorer … --deck …`
2. Smoke: `python scripts/smoke_test.py` (17/17)
3. User explicit OK for Kaggle upload
4. **Uploads left today?** Max **5/day** (§2.2a)
5. **Final slots:** Will this be one of your **2 Final Submissions**? If probing, OK — but **select best two manually** before deadline
6. After upload: `python scripts/track_ladder.py` then `--fetch-logs`
7. Log ref + μ in `report/submission_candidates_2026-06-19.md` and `report/ladder_history.csv`

---

## Deadline strategy

- Pick **2 Final Submissions** explicitly on Kaggle — don’t rely on auto-select if your best μ isn’t your most recent upload.
- Use daily upload quota for **probes**; re-upload or **select** winners before **Final Submission Deadline**.
- Keep at least one daily slot near deadline for a lock-in re-upload if needed.

---

## What “disabled” is NOT

- Not a **timeout** (10 min/player is per-game; submission ERROR is different)
- Not a **validation failure** (those show ERROR)
- Not “5/day exceeded” (that blocks new uploads entirely)

---

## Commands

```bash
python scripts/track_ladder.py
python scripts/track_ladder.py --fetch-logs

kaggle competitions submit -c pokemon-tcg-ai-battle \
  -f dist/candidates/<archive>.tar.gz \
  -m "description"
```

See also: `data/META_NOTES.md`, `data/CABT_API.md`, `data/EVAL_PROTOCOL.md`, `report/finals_strategy.md`.
