# PROGRESS → see STATE.md

The 157 KB append-only log from Sessions 1–43 was **reset on 2026-06-22 (Session 44)**. It is
preserved in full at branch `graveyard/pre-reset-20260622`:

```bash
git show graveyard/pre-reset-20260622:PROGRESS.md   # full historical run log
```

Going forward there is **one** handoff/state file — [`STATE.md`](STATE.md) — not two parallel logs
(Ruling R10). The consolidated record of what every past session tried and why it failed now lives
in [`RULINGS.md`](RULINGS.md).

**Where things went:**
- *What's true now + next action* → `STATE.md`
- *Ephemeral Cursor session* → `.cursor/SESSION.md`
- *What we tried + why* → `RULINGS.md`
- *What we're building* → `ARCHITECTURE.md` (§ Per-deck template phases 1–3)
- *Build backlog* → `TASKS.md` (R1–R3 pilot rules)

**Latest (2026-06-22, Session 44e):** Dragapult **850.5 μ** = **best so far** (ref 53950779) — **bar to
beat**, not the goal. Lucario v2 packaged; submit queued after daily quota. Next: phase-2 train/levers
to **exceed 850.5**.
