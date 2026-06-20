# Kaggle Track B Checkpoint Sweep Cell

Preferred next Track B run. This calls `scripts/sweep_track_b_checkpoints.py`,
which trains in chunks, saves each PPO checkpoint, distills/gates each
checkpoint, re-distills the best finalists with more teacher episodes, and
packages only the best passing finalist.

Download when complete:

```text
/kaggle/working/track_b_sweep_outputs.zip
```

For the quick 30-40 minute run, leave `CHUNKS = 5`. For the stronger 50-60
minute run, set `CHUNKS = 7`.

```python
import os
import shutil
import subprocess
import sys
import time
import zipfile
import urllib.request
from pathlib import Path

# ---- knobs ----
CHUNKS = 5                    # Set to 7 for the ~55 minute run.
TIMESTEPS_PER_CHUNK = 100_000
N_ENVS = 4
GATE_GAMES = 40
FINALIST_GATE_GAMES = 80
DISTILL_EPISODES = 300
FINALIST_DISTILL_EPISODES = 800
FINALIST_DISTILL_EPOCHS = 50
SLUG = "rl_deck_sweep"
DECK = "report/rl_deck_campaign/best_deck.csv"
OPPONENTS = "benchmark"
HOLDOUT = "a2_kyogre"

REPO_URL = "https://github.com/TomBombadyl/kaggle_pokemon.git"
ZIP_URL = "https://github.com/TomBombadyl/kaggle_pokemon/archive/refs/heads/main.zip"
REPO = Path("/kaggle/working/kaggle_pokemon")
OUT = Path("/kaggle/working/out_sweep")
ARCHIVE = Path("/kaggle/working/track_b_sweep_outputs")

def run(cmd, *, cwd=None, check=True, capture=True):
    print("\n$", " ".join(map(str, cmd)), flush=True)
    if capture:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
        if p.stdout:
            print(p.stdout, flush=True)
        if p.stderr:
            print(p.stderr, file=sys.stderr, flush=True)
    else:
        p = subprocess.run(cmd, cwd=cwd, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))}")
    return p

started = time.time()

print("=== 1/5: repo ===", flush=True)
if not REPO.exists():
    probe = run(["git", "ls-remote", REPO_URL, "HEAD"], check=False)
    if probe.returncode != 0:
        raise SystemExit("GitHub unreachable. Turn Kaggle Internet On, restart session, rerun this cell.")
    clone = run(["git", "clone", "--depth", "1", REPO_URL, str(REPO)], check=False)
    if clone.returncode != 0:
        print("git clone failed; trying zip fallback", flush=True)
        zip_path = Path("/kaggle/working/kaggle_pokemon.zip")
        urllib.request.urlretrieve(ZIP_URL, zip_path)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall("/kaggle/working")
        next(Path("/kaggle/working").glob("kaggle_pokemon-*")).rename(REPO)

os.chdir(REPO)
run(["git", "log", "--oneline", "-1"], check=False)

print("=== 2/5: deps ===", flush=True)
run([sys.executable, "-m", "pip", "install", "-q", "gymnasium>=0.29", "stable-baselines3>=2.3", "sb3-contrib>=2.3"])

print("=== 3/5: cuda ===", flush=True)
import torch
print("torch", torch.__version__, flush=True)
print("cuda", torch.cuda.is_available(), flush=True)
print("device_count", torch.cuda.device_count(), flush=True)
print("gpu0", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu", flush=True)
if not torch.cuda.is_available():
    raise SystemExit("CUDA is false. Set Kaggle Accelerator=GPU, restart session, rerun this cell.")

print("=== 4/5: engine ===", flush=True)
run([sys.executable, "scripts/kaggle_setup.py"])

print("=== 5/5: checkpoint sweep ===", flush=True)
cmd = [
    sys.executable, "scripts/sweep_track_b_checkpoints.py",
    "--deck", DECK,
    "--slug", SLUG,
    "--chunks", str(CHUNKS),
    "--timesteps-per-chunk", str(TIMESTEPS_PER_CHUNK),
    "--n-envs", str(N_ENVS),
    "--opponents", OPPONENTS,
    "--holdout", HOLDOUT,
    "--gate-games", str(GATE_GAMES),
    "--finalist-gate-games", str(FINALIST_GATE_GAMES),
    "--distill-episodes", str(DISTILL_EPISODES),
    "--finalist-distill-episodes", str(FINALIST_DISTILL_EPISODES),
    "--finalist-distill-epochs", str(FINALIST_DISTILL_EPOCHS),
    "--out-dir", str(OUT),
    "--archive-base", str(ARCHIVE),
]
run(cmd, capture=False)

zip_file = ARCHIVE.with_suffix(".zip")
print("\nDONE", flush=True)
print("elapsed_minutes", round((time.time() - started) / 60, 1), flush=True)
print("download", zip_file, flush=True)
print("exists", zip_file.exists(), flush=True)
print("size", zip_file.stat().st_size if zip_file.exists() else None, flush=True)
```
