#!/usr/bin/env python3
"""Rebuild field/weights.json archetype shares from latest meta JSON."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_GLOB = "report/meta/deck_by_mu_band_*.json"
OUT = ROOT / "field" / "weights.json"


def main() -> int:
    meta_files = sorted(ROOT.glob("report/meta/deck_by_mu_band_*.json"), reverse=True)
    if not meta_files:
        print("No meta JSON found; keeping hand-tuned weights.json")
        return 1

    meta = json.loads(meta_files[0].read_text(encoding="utf-8"))
    band_stats = meta.get("manifest_band_stats") or {}
    total_eps = sum(int(v.get("episodes", 0)) for v in band_stats.values())

    arch = Counter()
    for band_data in (meta.get("deck_by_band") or {}).values():
        for name, apps in (band_data.get("arch_appearances") or {}).items():
            if name != "unknown":
                arch[name] += int(apps)

    arch_total = sum(arch.values()) or 1
    # Map replay archetype names to lever/registry archetype keys.
    name_map = {
        "lucario": "lucario_mirror",
        "dragapult": "dragapult_psychic",
        "alakazam": "alakazam_psychic",
        "bellibolt": "iono_lightning",
        "kyogre": "kyogre_water",
        "trevenant": "trevenant_control",
    }
    weights: dict[str, float] = {}
    for name, count in arch.items():
        key = name_map.get(name, name)
        weights[key] = round(count / arch_total, 3)

    # Normalize lucario dominance if replay sample thin.
    if "lucario_mirror" not in weights:
        weights["lucario_mirror"] = 0.45

    doc = json.loads(OUT.read_text(encoding="utf-8"))
    doc["opponent_archetype_weights"] = weights
    doc["source"] = str(meta_files[0].relative_to(ROOT))
    if total_eps:
        doc["mu_band_volume"] = {
            k: round(int(v.get("episodes", 0)) / total_eps, 4)
            for k, v in band_stats.items()
            if int(v.get("episodes", 0)) > 0
        }
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
