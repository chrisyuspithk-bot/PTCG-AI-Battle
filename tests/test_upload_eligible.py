"""Tests for scripts/check_upload_eligible.py (R12 upload gate)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_upload_eligible.py"
ALAKAZAM_MANIFEST = ROOT / "dist" / "candidates" / "ryotasueyoshi_alakazam_best5.manifest.json"


def _run(*args: str) -> int:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).returncode


def test_blocks_alakazam_port_without_material_change():
    if not ALAKAZAM_MANIFEST.exists():
        return  # package not built in CI
    assert _run("--manifest", str(ALAKAZAM_MANIFEST), "--change", "port verify") == 1
    assert _run("--manifest", str(ALAKAZAM_MANIFEST)) == 1


def test_allows_lucario_scorer_with_hypothesis():
    code = _run(
        "--brain",
        "LucarioScorer",
        "--deck",
        "agent_decks/real_mega_lucario_ex.csv",
        "--change",
        "LucarioScorer full gate: smart bench + matchup levers vs Search baseline",
        "--local-gate",
        "55.0",
    )
    assert code == 0


def test_missing_manifest_friendly_exit():
    code = subprocess.run(
        [sys.executable, str(SCRIPT), "--manifest", "dist/candidates/foo.manifest.json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert code.returncode == 1
    assert "Manifest not found" in code.stderr
    assert "LucarioScorer" in code.stderr


def test_blocks_weak_local_gate():
    code = _run(
        "--brain",
        "LucarioScorer",
        "--deck",
        "agent_decks/real_mega_lucario_ex.csv",
        "--change",
        "LucarioScorer: bench fix vs Dragapult native",
        "--local-gate",
        "39.3",
    )
    assert code == 1


def test_suggest_exits_zero():
    assert _run("--suggest") == 0
