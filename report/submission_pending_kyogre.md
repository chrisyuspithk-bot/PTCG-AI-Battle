# Pending upload — Track B Kyogre (LearnedScorer)

**Status:** Package ready; Kaggle API rejected submit **2026-06-19** (5/5 daily slots used).

## Artifact

- `dist/candidates/track_b_learned_kyogre.tar.gz` (5.4 MiB)
- Local gate: Learned **206/240** vs pool @40g, SPRT pass
- Model: `agent/models/distilled_kyogre_v1.npz`

## Submit (first slot tomorrow or when quota resets)

```bash
kaggle competitions submit -c pokemon-tcg-ai-battle \
  -f dist/candidates/track_b_learned_kyogre.tar.gz \
  -m "Track B Kyogre LearnedScorer per-deck 100k train (user approved)"
```

Then:

```bash
python scripts/track_ladder.py
python scripts/track_ladder.py --fetch-logs
```

## Kaggle UI

1. After COMPLETE (~40 min), note **publicScore** (μ).
2. **My Submissions → Select as Final Submission** for this ref (Final 1 target).
3. Consider replacing weaker Final (e.g. TA2 Abomasnow 486 μ) with this Learned Kyogre.

## Today’s submissions (quota full)

| ref | file | μ |
|-----|------|---|
| 53854707 | a2_kyogre heuristic | **633.0** |
| 53856711 | track_a_probe_1 Search | 580.8 |
| 53856584 | track_b alakazam (old distill) | 490.4 |
| 53856590 | track_b dragapult (old distill) | 468.9 |
| 53856676 | track_a_probe_2 Search | 486.4 |
