#!/usr/bin/env python3
"""Rebuild and dry-run submission tarballs (no Kaggle upload).

Default: Dragapult v3 only (ladder track). Lucario packages are archive/probes —
not co-champions. Use --include-lucario when you explicitly need those tarballs.

Usage:
    python scripts/repackage_champions.py
    python scripts/repackage_champions.py --include-lucario
    python scripts/repackage_champions.py --include-lucario --skip-lucario-r2
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "dist" / "candidates"
MANIFEST_OUT = CAND / "champions_manifest.json"

LUCARIO_V5_MODEL = ROOT / "rl_mcts_field" / "lucarioex_v5_field" / "model_best.pth"
LUCARIO_V5_META = ROOT / "rl_mcts_field" / "lucarioex_v5_field" / "run_meta.json"
LUCARIO_DECK = ROOT / "agent_decks" / "real_mega_lucario_ex.csv"


def _run(cmd: list[str], label: str) -> None:
    print(f"\n=== {label} ===")
    print(" ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        raise SystemExit(f"{label} failed (exit {proc.returncode})")


def _size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024) if path.exists() else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--include-lucario", action="store_true",
                    help="Also package Lucario v5 MCTS (+ optional R2 levers)")
    ap.add_argument("--skip-lucario-r2", action="store_true",
                    help="With --include-lucario: skip R2 levers package")
    args = ap.parse_args()

    CAND.mkdir(parents=True, exist_ok=True)

    # 1. Dragapult v3 (standalone packager — matches ref 53989933 on ladder)
    _run([sys.executable, "scripts/package_dragapult.py"], "Dragapult v3")

    entries: list[dict] = []

    drag_tar = CAND / "dragapult_ex_sample.tar.gz"
    drag_manifest = CAND / "dragapult_ex_sample.manifest.json"
    entries.append({
        "id": "dragapult_v3",
        "role": "ladder_champion",
        "tarball": str(drag_tar.relative_to(ROOT)),
        "size_mb": round(_size_mb(drag_tar), 2),
        "rebuild": "python scripts/package_dragapult.py",
        "kaggle_submit": (
            "kaggle competitions submit pokemon-tcg-ai-battle "
            "-f dist/candidates/dragapult_ex_sample.tar.gz "
            '-m "dragapult v3: Crispin rules + bench guard R7"'
        ),
        "ladder_ref": "53989933",
        "ladder_mu": 880.8,
        "deck": "agent_decks/dragapult_ex_sample.csv",
        "brain": "agent/dragapult_agent.py + dragapult_bench_guard.py",
        "manifest": str(drag_manifest.relative_to(ROOT)) if drag_manifest.exists() else None,
    })

    if not args.include_lucario:
        out = {
            "built_at": datetime.now(timezone.utc).isoformat(),
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "pin_policy": (
                "Ladder track: Dragapult only until another brain×deck beats 880.8 μ "
                "(2+ readings). Lucario: use --include-lucario for archive builds."
            ),
            "champions": entries,
        }
        MANIFEST_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nWrote {MANIFEST_OUT.relative_to(ROOT)}")
        print("Dragapult dry-run OK. No Kaggle upload attempted.")
        return 0

    if not LUCARIO_V5_MODEL.exists():
        print(f"\nWARNING: {LUCARIO_V5_MODEL} missing — Lucario packages skipped")
    else:
        # 2. Lucario v5 MCTS (matches ref 53995982 on ladder)
        _run([
            sys.executable, "scripts/package_submission.py",
            "--name", "lucarioex_v5_field_mcts",
            "--scorer", "lucario_mcts",
            "--model", str(LUCARIO_V5_MODEL.relative_to(ROOT)),
            "--meta", str(LUCARIO_V5_META.relative_to(ROOT)),
            "--deck", str(LUCARIO_DECK.relative_to(ROOT)),
        ], "Lucario v5 MCTS")

        luc_v5_tar = CAND / "lucarioex_v5_field_mcts.tar.gz"
        entries.append({
            "id": "lucario_v5_mcts",
            "role": "strategy_hub_probe",
            "tarball": str(luc_v5_tar.relative_to(ROOT)),
            "size_mb": round(_size_mb(luc_v5_tar), 2),
            "rebuild": (
                "python scripts/package_submission.py --name lucarioex_v5_field_mcts "
                "--scorer lucario_mcts "
                "--model rl_mcts_field/lucarioex_v5_field/model_best.pth "
                "--meta rl_mcts_field/lucarioex_v5_field/run_meta.json "
                "--deck agent_decks/real_mega_lucario_ex.csv"
            ),
            "kaggle_submit": (
                "kaggle competitions submit pokemon-tcg-ai-battle "
                "-f dist/candidates/lucarioex_v5_field_mcts.tar.gz "
                '-m "lucarioex v5 field MCTS final (25 cycles)"'
            ),
            "ladder_ref": "53995982",
            "ladder_mu": 580.6,
            "deck": "agent_decks/real_mega_lucario_ex.csv",
            "brain": "lucario_mcts + model_best.pth",
            "note": "Pre-R2 levers in weights; rules path preferred for future builds",
        })

        if not args.skip_lucario_r2:
            # 3. Lucario v5 + current matchup_levers (dragapult R2 boss_orders=900)
            _run([
                sys.executable, "scripts/package_submission.py",
                "--name", "lucarioex_v5_r2_levers_20260626",
                "--scorer", "lucario_mcts",
                "--model", str(LUCARIO_V5_MODEL.relative_to(ROOT)),
                "--meta", str(LUCARIO_V5_META.relative_to(ROOT)),
                "--deck", str(LUCARIO_DECK.relative_to(ROOT)),
            ], "Lucario v5 + R2 levers (current matchup_levers.py)")

            r2_tar = CAND / "lucarioex_v5_r2_levers_20260626.tar.gz"
            entries.append({
                "id": "lucario_v5_r2_levers",
                "role": "optional_probe",
                "tarball": str(r2_tar.relative_to(ROOT)),
                "size_mb": round(_size_mb(r2_tar), 2),
                "rebuild": (
                    "python scripts/package_submission.py "
                    "--name lucarioex_v5_r2_levers_20260626 "
                    "--scorer lucario_mcts "
                    "--model rl_mcts_field/lucarioex_v5_field/model_best.pth "
                    "--meta rl_mcts_field/lucarioex_v5_field/run_meta.json "
                    "--deck agent_decks/real_mega_lucario_ex.csv"
                ),
                "kaggle_submit": (
                    "kaggle competitions submit pokemon-tcg-ai-battle "
                    "-f dist/candidates/lucarioex_v5_r2_levers_20260626.tar.gz "
                    '-m "lucario v5 MCTS + dragapult R2 levers (boss_orders=900)"'
                ),
                "ladder_ref": None,
                "ladder_mu": None,
                "local_gate": "+13.3pp vs 3-opp suite (Session 44j); not on ladder yet",
                "note": "Packages agent/matchup_levers.py at build time",
            })

    out = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "pin_policy": (
            "No rush to pin Finals during development. All uploads can COMPLETE and "
            "earn μ; only 2 count for final placement — select manually before deadline "
            "(data/SUBMISSION_PLAYBOOK.md)."
        ),
        "champions": entries,
    }
    MANIFEST_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {MANIFEST_OUT.relative_to(ROOT)}")
    print("All packages dry-run OK. No Kaggle upload attempted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
