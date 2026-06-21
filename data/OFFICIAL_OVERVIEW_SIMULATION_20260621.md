# Simulation Competition Overview

**Source:** https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/overview  
**Fetched:** 2026-06-21 via Claude in Chrome

---

## Evaluation: Skill Rating System

**Scoring System:** Gaussian N(μ, σ²) — μ = skill rating, σ² = uncertainty

- **Each submission plays episodes** against rotating pool of agents
- **Episode results update rating** via Bayesian update
- **Validation Episode:** New submission plays first episode to join pool
- **Pool selection:** Tries to match submissions with similar skill

## Timeline (Simulation)

| Date | Milestone |
|---|---|
| June 16, 2026 | **Start Date** |
| August 9, 2026 | Entry Deadline; Team Merger Deadline |
| August 16, 2026 | **Final Submission Deadline** |
| Aug 17 – Aug 31 | Final Evaluation (continued games until convergence) |

## Submission Mechanics

- **5 submissions per day** (no limit on number)
- **Select up to 2 Final Submissions** for final evaluation
- Format: `.tar.gz` with `main.py` at top level
- Command: `tar -czvf submission.tar.gz *`

## Prizes

**Simulation track:** No monetary prizes (knowledge/medals only)

## Key Constraints

- **No Ingress/Egress:** No external network access during episode evaluation
- **Simulator > Official TCG Rules:** See discussion 708586 for differences

## Reference Resources

- **TCG Rulebook:** https://www.pokemon.com/static-assets/content-assets/cms2/pdf/trading-card-game/rulebook/meg_rulebook_en.pdf
- **Simulator API:** https://matsuoinstitute.github.io/cabt/
- **Kaggle Environments:** https://github.com/Kaggle/kaggle-environments (v1.14.10+)

---

**Status:** Simulation track ongoing; Final Submission Deadline August 16, 2026
