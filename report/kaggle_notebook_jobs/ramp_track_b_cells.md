# Kaggle Track B Ramp Training Cells

Historical fallback only. Prefer `report/kaggle_notebook_jobs/sweep_track_b_cell.md`
for the next learned-policy run because it checkpoints, distills, gates, and
packages the best intermediate policy instead of packaging only the final PPO
state.

Use these instead of the 12M deep cell when Kaggle Draft Session keeps dying.

Important: for output survival, use **Save Version -> Run All** if you can. If
you run in Draft Session, download `/kaggle/working/track_b_ramp_outputs.zip`
as soon as the cell says `DONE`.

## 30 Minute Cell

Expected runtime from our observed speed: about 25-35 minutes.

```python
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
import urllib.request
from pathlib import Path

TIMESTEPS = 500_000
N_ENVS = 4
GATE_GAMES = 40
SLUG = "rl_deck_ramp"
DECK = "report/rl_deck_campaign/best_deck.csv"
OPPONENTS = "benchmark"
HOLDOUT = "a2_kyogre"

REPO_URL = "https://github.com/TomBombadyl/kaggle_pokemon.git"
ZIP_URL = "https://github.com/TomBombadyl/kaggle_pokemon/archive/refs/heads/main.zip"
REPO = Path("/kaggle/working/kaggle_pokemon")
OUT = Path("/kaggle/working/out_ramp")
ARCHIVE = Path("/kaggle/working/track_b_ramp_outputs")

def run(cmd, *, cwd=None, check=True):
    print("\n$", " ".join(map(str, cmd)), flush=True)
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout, flush=True)
    if p.stderr:
        print(p.stderr, file=sys.stderr, flush=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))}")
    return p

def run_live(cmd, *, cwd=None, check=True):
    print("\n$", " ".join(map(str, cmd)), flush=True)
    p = subprocess.Popen(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
    start = last = time.time()
    while True:
        line = p.stdout.readline()
        if line:
            print(line, end="", flush=True)
            last = time.time()
        elif p.poll() is not None:
            break
        elif time.time() - last > 60:
            print(f"[heartbeat] still running after {(time.time() - start) / 60:.1f} min", flush=True)
            last = time.time()
        else:
            time.sleep(1)
    rc = p.wait()
    if check and rc != 0:
        raise RuntimeError(f"command failed ({rc}): {' '.join(map(str, cmd))}")
    return rc

def collect():
    OUT.mkdir(exist_ok=True)
    patterns = [
        "agent/models/rl_policy.zip",
        f"agent/models/distilled_{SLUG}_v1.npz",
        "agent/models/distilled_v1.npz",
        f"dist/candidates/track_b_learned_{SLUG}.tar.gz",
        "report/rl_train/checkpoint.json",
        "report/track_b_runs/*.json",
        f"report/track_b_gates/*{SLUG}*gate.md",
        "report/rl_train/eval_*.json",
    ]
    saved = []
    for pattern in patterns:
        for src in glob.glob(pattern):
            dst = OUT / Path(src).name
            shutil.copy2(src, dst)
            saved.append(str(dst))
            print("saved", src, "->", dst, flush=True)
    zip_file = shutil.make_archive(str(ARCHIVE), "zip", str(OUT))
    print("download", zip_file, flush=True)
    return saved, zip_file

started = time.time()
print("=== 1/6: repo ===", flush=True)
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

print("=== 2/6: deps ===", flush=True)
run([sys.executable, "-m", "pip", "install", "-q", "gymnasium>=0.29", "stable-baselines3>=2.3", "sb3-contrib>=2.3"])

print("=== 3/6: cuda ===", flush=True)
import torch
print("torch", torch.__version__, flush=True)
print("cuda", torch.cuda.is_available(), flush=True)
print("device_count", torch.cuda.device_count(), flush=True)
print("gpu0", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu", flush=True)
if not torch.cuda.is_available():
    raise SystemExit("CUDA is false. Set Kaggle Accelerator=GPU, restart session, rerun this cell.")

print("=== 4/6: engine ===", flush=True)
run([sys.executable, "scripts/kaggle_setup.py"])

print("=== 5/6: train/distill/gate/package ===", flush=True)
cmd = [
    sys.executable, "scripts/train_track_b_deck.py",
    "--deck", DECK,
    "--slug", SLUG,
    "--timesteps", str(TIMESTEPS),
    "--n-envs", str(N_ENVS),
    "--opponents", OPPONENTS,
    "--holdout", HOLDOUT,
    "--gate-games", str(GATE_GAMES),
    "--package",
    "--promote",
    "--resume",
]
run_live(cmd)

print("=== 6/6: collect ===", flush=True)
saved, zip_file = collect()
print("DONE", flush=True)
print("elapsed_minutes", round((time.time() - started) / 60, 1), flush=True)
print("download", zip_file, flush=True)
print("\n".join(saved), flush=True)
```

## 55 Minute Cell

Run this after the 30 minute cell if the same Kaggle session is still alive. It
will resume from `rl_policy.zip`. If the session restarted, it still runs fresh.

```python
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
import urllib.request
from pathlib import Path

TIMESTEPS = 1_000_000
N_ENVS = 4
GATE_GAMES = 40
SLUG = "rl_deck_ramp"
DECK = "report/rl_deck_campaign/best_deck.csv"
OPPONENTS = "benchmark"
HOLDOUT = "a2_kyogre"

REPO_URL = "https://github.com/TomBombadyl/kaggle_pokemon.git"
ZIP_URL = "https://github.com/TomBombadyl/kaggle_pokemon/archive/refs/heads/main.zip"
REPO = Path("/kaggle/working/kaggle_pokemon")
OUT = Path("/kaggle/working/out_ramp")
ARCHIVE = Path("/kaggle/working/track_b_ramp_outputs")

def run(cmd, *, cwd=None, check=True):
    print("\n$", " ".join(map(str, cmd)), flush=True)
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout, flush=True)
    if p.stderr:
        print(p.stderr, file=sys.stderr, flush=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))}")
    return p

def run_live(cmd, *, cwd=None, check=True):
    print("\n$", " ".join(map(str, cmd)), flush=True)
    p = subprocess.Popen(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
    start = last = time.time()
    while True:
        line = p.stdout.readline()
        if line:
            print(line, end="", flush=True)
            last = time.time()
        elif p.poll() is not None:
            break
        elif time.time() - last > 60:
            print(f"[heartbeat] still running after {(time.time() - start) / 60:.1f} min", flush=True)
            last = time.time()
        else:
            time.sleep(1)
    rc = p.wait()
    if check and rc != 0:
        raise RuntimeError(f"command failed ({rc}): {' '.join(map(str, cmd))}")
    return rc

def collect():
    OUT.mkdir(exist_ok=True)
    patterns = [
        "agent/models/rl_policy.zip",
        f"agent/models/distilled_{SLUG}_v1.npz",
        "agent/models/distilled_v1.npz",
        f"dist/candidates/track_b_learned_{SLUG}.tar.gz",
        "report/rl_train/checkpoint.json",
        "report/track_b_runs/*.json",
        f"report/track_b_gates/*{SLUG}*gate.md",
        "report/rl_train/eval_*.json",
    ]
    saved = []
    for pattern in patterns:
        for src in glob.glob(pattern):
            dst = OUT / Path(src).name
            shutil.copy2(src, dst)
            saved.append(str(dst))
            print("saved", src, "->", dst, flush=True)
    zip_file = shutil.make_archive(str(ARCHIVE), "zip", str(OUT))
    print("download", zip_file, flush=True)
    return saved, zip_file

started = time.time()
print("=== 1/6: repo ===", flush=True)
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

print("=== 2/6: deps ===", flush=True)
run([sys.executable, "-m", "pip", "install", "-q", "gymnasium>=0.29", "stable-baselines3>=2.3", "sb3-contrib>=2.3"])

print("=== 3/6: cuda ===", flush=True)
import torch
print("torch", torch.__version__, flush=True)
print("cuda", torch.cuda.is_available(), flush=True)
print("device_count", torch.cuda.device_count(), flush=True)
print("gpu0", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu", flush=True)
if not torch.cuda.is_available():
    raise SystemExit("CUDA is false. Set Kaggle Accelerator=GPU, restart session, rerun this cell.")

print("=== 4/6: engine ===", flush=True)
run([sys.executable, "scripts/kaggle_setup.py"])

print("=== 5/6: train/distill/gate/package ===", flush=True)
cmd = [
    sys.executable, "scripts/train_track_b_deck.py",
    "--deck", DECK,
    "--slug", SLUG,
    "--timesteps", str(TIMESTEPS),
    "--n-envs", str(N_ENVS),
    "--opponents", OPPONENTS,
    "--holdout", HOLDOUT,
    "--gate-games", str(GATE_GAMES),
    "--package",
    "--promote",
    "--resume",
]
run_live(cmd)

print("=== 6/6: collect ===", flush=True)
saved, zip_file = collect()
print("DONE", flush=True)
print("elapsed_minutes", round((time.time() - started) / 60, 1), flush=True)
print("download", zip_file, flush=True)
print("\n".join(saved), flush=True)
```
