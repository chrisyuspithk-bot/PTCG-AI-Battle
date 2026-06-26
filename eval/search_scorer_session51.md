# SearchScorer — battle_ptr fix + prize tracker gate

**Date:** 2026-06-26 Session 51 execute batch

## Bug fixed

`SearchScorer._ensure_engine()` cached `Battle.battle_ptr` across harness games. After `battle_finish()` / next `battle_start()`, search used a stale pointer → native engine **ACCESS_VIOLATION** on multi-opponent gates.

**Fix:** `agent/search_policy.py` — refresh `battle_ptr` on every search call.

## PrizeTracker wiring

`SearchScorer` + `LucarioSearchScorer` update `PrizeTracker` each turn; prized cards penalized on deck-search contexts (`CTX_TO_HAND`, etc.).

## Gate (full suite, n=30)

| Overall | **26.7%** [20.2, 34.3] |
|---------|--------------------------|

Comparable to pre-fix **27.3%** — prize inference did not move the local bar; stability fix unblocks iteration.

**Do not upload** — far below **660.5 μ** SearchScorer ladder row.
