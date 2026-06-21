# Tomorrow 5-agent Simulation slate (2026-06-21)

Prepared 2026-06-20. No Kaggle submission was attempted. Today quota is already
5/5; run any upload commands only on 2026-06-21 after explicit user approval.

## Ground rules

- Public ladder mu is truth. Local gates are filters only.
- Protected Final remains `53869254` Search Lucario at 660.5 mu until a new upload
  beats it on public ladder.
- Do not upload a candidate just because it is novel.
- If a candidate completes near 600 then drops, stop that lane and preserve the
  remaining daily slots.
- Manually select the best two Final Submissions; do not rely on Kaggle recency.

## Ranked upload slate

> **2026-06-20 UPDATE — re-ranked.** A 30-game public gate for the imported
> `dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz` returned **55.3% suite mean
> (199/360, 0 draws/unfinished/crashes)** and **66.7% vs the 1084 baseline** — by far
> the strongest local candidate (every probe below is 5–15% on the same gate). It
> becomes **upload probe slot #1**. It still misses the 65% suite-mean bar (worst:
> Iono 30%, Crustle anti-wall 30%), so it is a probe, not a Final claim. The five
> entries below shift down one slot. Output:
> `report/public_gate/alakazam_best5_g30_20260620.txt`.

### 0. Ryotasueyoshi Alakazam best5 (imported public baseline) — NEW probe #1

- Deck/brain: bundled public rule-based Alakazam `main.py` + `deck.csv`.
- Package: `dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz`
- Submit command - DO NOT RUN WITHOUT USER OK:

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle -f dist/candidates/ryotasueyoshi_alakazam_best5.tar.gz -m "20260621 probe imported alakazam best5 (55.3% public gate)"
```

- Evidence: **5000-game gate 57.3% suite mean (2867/5002)**, clean (0 unfinished).
  Per-matchup at n=417 (supersedes the noisier 30g read).
- Known weaknesses (n=417): **Iono 29.7%** (only severe outlier),
  lucario-search-915 43.4%, crustle anti-wall 47.4%, vs-1084 **52.2%**.
- NOT upload-eligible by the standing bars (suite < 65%, vs-1084 < 55%, Iono < 45%);
  upload only as an explicit probe. An attempted Iono fix (deck-out-guard relaxation)
  regressed Iono 30%->22% and was discarded — Iono is a structural matchup problem.
- Type: Probe. Final candidate only if public mu beats 660.5 after ladder games.

### 1. Lucario v2 search probe / Final challenger

- Deck: `agent_decks/real_mega_lucario_ex.csv`
- Brain: `lucario_search` (`LucarioSearchScorer`)
- Package: `dist/candidates/track_a_lucario_search.tar.gz`
- Package command:

```bash
python scripts/package_submission.py --name track_a_lucario_search --scorer lucario_search --deck agent_decks/real_mega_lucario_ex.csv --gate --gate-games 12
```

- Submit command - DO NOT RUN WITHOUT USER OK:

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle -f dist/candidates/track_a_lucario_search.tar.gz -m "20260621 probe lucario_search v2 expanded leader-suite gate"
```

- Evidence:
  - Expanded leader-suite L1: 313/450 = 69.6%, gate passed.
  - Package L0 passed; package public gate @12 games/opponent: 11.1% suite mean.
- Known weaknesses:
  - Trevenant control 14/30 = 46.7%.
  - Trevenant Dunsparce 12/30 = 40.0%.
  - Generic public package gate is weak despite leader-suite pass.
- Upload priority: 1.
- Type: Probe first; Final candidate only if public mu beats 660.5 after ladder
  games.
- Stop/go:
  - Go to Final consideration only if mu exceeds `53869254` after >=40 minutes.
  - Stop Lucario variants if fast losses or Trevenant losses dominate replays.

### 2. Gen19 fast-basic + SearchScorer robust-deck probe

- Deck: `agent_decks/deck_rl/gen19_fast_basic.csv`
- Brain: `search` (`SearchScorer`)
- Package: `dist/candidates/track_a_gen19_fast_basic_search.tar.gz`
- Package command:

```bash
python scripts/package_submission.py --name track_a_gen19_fast_basic_search --scorer search --deck agent_decks/deck_rl/gen19_fast_basic.csv --gate --gate-games 12
```

- Submit command - DO NOT RUN WITHOUT USER OK:

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle -f dist/candidates/track_a_gen19_fast_basic_search.tar.gz -m "20260621 probe gen19 fast-basic robust deck search"
```

- Evidence:
  - Robust 79-opponent top-2 screen @12 games/opponent: robust 0.610, mean 0.728,
    CVaR 0.492, maximin 0.333; beat `top_mined_trevenant`.
  - Package L0 passed; package public gate @12 games/opponent: 8.3% suite mean.
- Known weaknesses:
  - Worst robust matchup: `a2_kyogre`.
  - Large disagreement between robust mined-gauntlet screen and package public gate.
- Upload priority: 2.
- Type: Probe. Final candidate only if public mu beats 660.5.
- Stop/go:
  - If mu falls below 600 after early ladder games, pause robust-deck Search
    uploads and inspect replays before spending another slot.

### 3. Top-mined Trevenant + SearchScorer leader-archetype probe

- Deck: `agent_decks/top_mined_trevenant.csv`
- Brain: `search` (`SearchScorer`)
- Package: `dist/candidates/track_a_trevenant_leader_search.tar.gz`
- Package command:

```bash
python scripts/package_submission.py --name track_a_trevenant_leader_search --scorer search --deck agent_decks/top_mined_trevenant.csv --gate --gate-games 12
```

- Submit command - DO NOT RUN WITHOUT USER OK:

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle -f dist/candidates/track_a_trevenant_leader_search.tar.gz -m "20260621 probe mined Trevenant leader deck search"
```

- Evidence:
  - Robust 79-opponent top-2 screen @12 games/opponent: robust 0.574, mean 0.694,
    CVaR 0.453, maximin 0.250.
  - Package L0 passed; package public gate @12 games/opponent: 15.3% suite mean.
- Known weaknesses:
  - Worst robust matchup: `a2_kyogre`.
  - SearchScorer is not Trevenant-specific control logic; this is deck transfer,
    not a full leader-brain clone.
- Upload priority: 3.
- Type: Probe.
- Stop/go:
  - Continue only if mu holds above the protected baseline band or replays show
    long-game control wins; otherwise prioritize Trevenant-specific RuleCore work.

### 4. Gen19 fast-basic + Track B learned policy

- Deck: `agent_decks/deck_rl/gen19_fast_basic.csv`
- Brain: `learned`
- Model: `agent/models/distilled_gen19-fast-basic_v1.npz`
- Package: `dist/candidates/track_b_learned_gen19_fast_basic.tar.gz`
- Package command:

```bash
python scripts/gate_track_b.py --games 40 --deck agent_decks/deck_rl/gen19_fast_basic.csv --model agent/models/distilled_gen19-fast-basic_v1.npz --name track_b_learned_gen19_fast_basic
```

- Submit command - DO NOT RUN WITHOUT USER OK:

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle -f dist/candidates/track_b_learned_gen19_fast_basic.tar.gz -m "20260621 probe Track B learned gen19 fast-basic"
```

- Evidence:
  - L2 Track B gate @40 games/opponent: Learned 203/240.
  - Same-deck Search baseline: 206/240.
  - SPRT: accept_b; package dry-run OK.
- Known weaknesses:
  - Learned did not beat Search on the same deck at L2.
  - Treat as a learned-policy probe, not the preferred gen19 brain.
- Upload priority: 4.
- Type: Probe only.
- Stop/go:
  - Upload only if there is a spare slot after Search probes, or if the user wants
    explicit Track B ladder data. If it underperforms Search, keep RL offline.

### 5. Kyogre Search backup / conservative comparison

- Deck: `agent_decks/a2_kyogre_33_energy.csv`
- Brain: `search` (`SearchScorer`)
- Package: `dist/candidates/track_a_kyogre_search_backup.tar.gz`
- Package command:

```bash
python scripts/package_submission.py --name track_a_kyogre_search_backup --scorer search --deck agent_decks/a2_kyogre_33_energy.csv --gate --gate-games 12
```

- Submit command - DO NOT RUN WITHOUT USER OK:

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle -f dist/candidates/track_a_kyogre_search_backup.tar.gz -m "20260621 backup Kyogre search comparison"
```

- Evidence:
  - Package L0 passed; package public gate @12 games/opponent: 13.2% suite mean.
  - Kyogre family has prior ladder baseline value, but this exact archive has no
    fresh public mu proof.
- Known weaknesses:
  - Not a new ceiling hypothesis.
  - Public package gate remains weak.
- Upload priority: 5.
- Type: Backup/probe only unless public mu beats 660.5.
- Stop/go:
  - Use only if earlier probes fail quickly or if a conservative comparison slot
    is useful for calibrating tomorrow's field.

## Rejected reserve

`track_d_lucario_rl_mcts_iter5` was imported and packaged, but should not be in
tomorrow's upload slate.

- Deck: `agent_decks/real_mega_lucario_ex.csv`
- Brain: `lucario_mcts`
- Package: `dist/candidates/track_d_lucario_rl_mcts_iter5.tar.gz`
- Import/package command:

```bash
python scripts/import_lucario_rl_outputs.py --source report/kaggle_notebook_jobs/lucario/kaggle_download_iter45_20260620 --name track_d_lucario_rl_mcts_iter5 --gate-games 12
```

- Evidence:
  - Dry-run import OK.
  - Public gate @12 games/opponent: 8/144 = 5.6%.
  - Six matchups were 0/12.
- Decision: do not upload until the imported RL policy beats Search Lucario or
  LucarioSearchScorer in L1/L2 gates.

## Final-submission guidance

Keep `53869254` selected as a protected Final until beaten. If tomorrow produces
two agents above 660.5 mu, select:

1. The highest-mu new agent after replay/log review.
2. The second-highest-mu new agent only if its losses are not dominated by crash,
   no-active, or deck-out failures; otherwise keep `53869254`.

If no new upload beats 660.5, keep `53869254` as Final and do not pin novelty
probes.

## Required post-upload commands

After each approved upload:

```bash
kaggle competitions submissions pokemon-tcg-ai-battle -v
kaggle competitions episodes <ref> -v
python scripts/track_ladder.py --fetch-logs
python scripts/analyze_submission.py --ref <ref>
```

Record ref, COMPLETE mu, 40+ minute mu, episode count, loss reasons, and Final
selection decision in `PROGRESS.md`, `.cursor/SESSION.md`, and
`report/ladder_history.csv`.
