"""Distill torch RL/BC policy to numpy submission format."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent.features import FEATURE_VERSION, OPTION_DIM, STATE_DIM, option_features, state_features  # noqa: E402
from agent.learned_policy import LearnedScorer  # noqa: E402

TORCH_MODEL = ROOT / "agent" / "models" / "rl_policy.pt"
BC_MODEL = ROOT / "agent" / "models" / "bc_v1.npz"
OUT_MODEL = ROOT / "agent" / "models" / "distilled_v1.npz"
REPORT = ROOT / "report" / "distill_gate.md"

IN_DIM = STATE_DIM + OPTION_DIM
HIDDEN = 64


def _rl_checkpoint_stem(path: Path) -> str | None:
    """Return SB3 load stem if rl_policy.zip or .pt exists."""
    if path.exists() or path.with_suffix(".zip").exists():
        return str(path.with_suffix(""))
    alt = path.parent / f"{path.stem}.zip"
    if alt.exists():
        return str(alt.with_suffix(""))
    return None


def _base_env(env):
    while hasattr(env, "env"):
        env = env.env
    return env


def _make_teacher_env(deck_path: Path | None = None, opponents: str = "benchmark"):
    from rl.env_factory import make_masked_cabt_env, resolve_deck_path

    deck = resolve_deck_path(deck_path)
    return make_masked_cabt_env(deck, opponents=opponents, seed=0)


def _load_teacher(path: Path, deck_path: Path | None = None, opponents: str = "benchmark"):
    try:
        from sb3_contrib import MaskablePPO
    except ImportError:
        return None, None
    if not path.exists() and path.with_suffix(".zip").exists():
        path = path.with_suffix(".zip")
    stem = _rl_checkpoint_stem(path)
    if stem is None:
        return None, None
    env = _make_teacher_env(deck_path, opponents)
    try:
        model = MaskablePPO.load(stem, env=env)
        return model, env
    except Exception:
        return None, env


def collect_teacher_labels(model, env, episodes: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """Roll out teacher; return list of (option_inputs, teacher_probs) per decision."""
    import torch

    base = _base_env(env)
    groups: list[tuple[np.ndarray, np.ndarray]] = []
    device = model.policy.device

    for ep in range(episodes):
        obs, info = env.reset(seed=ep)
        terminated = truncated = False
        while not (terminated or truncated):
            raw = base._obs
            if raw is None:
                break
            sel = raw.get("select")
            mask = info.get("action_mask")
            if sel is not None and mask is not None and base._select_player() == 0:
                opts = sel.get("option") or []
                n = len(opts)
                if n > 0:
                    obs_t = torch.as_tensor(obs, device=device).float().unsqueeze(0)
                    mask_t = torch.as_tensor(mask, device=device).bool().unsqueeze(0)
                    with torch.no_grad():
                        dist = model.policy.get_distribution(obs_t, action_masks=mask_t)
                        probs = dist.distribution.probs.squeeze(0).cpu().numpy()
                    probs = probs[:n]
                    probs = probs / max(probs.sum(), 1e-8)
                    state = state_features(raw)
                    xs = np.stack(
                        [np.concatenate([state, option_features(raw, opts[i])]) for i in range(n)],
                    ).astype(np.float32)
                    groups.append((xs, probs.astype(np.float32)))

            action, _ = model.predict(obs, action_masks=mask, deterministic=True)
            obs, _reward, terminated, truncated, info = env.step(int(action))

    return groups


def _init_student_from_npz(model, path: Path) -> bool:
    import torch

    data = np.load(path)
    if data["w1"].shape[0] != IN_DIM:
        return False
    device = next(model.parameters()).device
    model[0].weight.data = torch.tensor(data["w1"].T, dtype=torch.float32, device=device)
    model[0].bias.data = torch.tensor(data["b1"], dtype=torch.float32, device=device)
    w2 = np.asarray(data["w2"], dtype=np.float32).reshape(-1, 1)
    b2 = np.asarray(data["b2"], dtype=np.float32).reshape(-1)
    model[2].weight.data = torch.tensor(w2.T, dtype=torch.float32, device=device)
    model[2].bias.data = torch.tensor(b2, dtype=torch.float32, device=device)
    return True


def train_student(
    groups: list[tuple[np.ndarray, np.ndarray]],
    init: Path | None,
    epochs: int,
) -> dict:
    import torch
    import torch.nn as nn

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = nn.Sequential(
        nn.Linear(IN_DIM, HIDDEN),
        nn.Tanh(),
        nn.Linear(HIDDEN, 1),
    ).to(device)
    if init is not None and init.exists():
        _init_student_from_npz(model, init)

    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    for _ in range(epochs):
        for xs, teacher_probs in groups:
            xt = torch.tensor(xs, device=device)
            target = torch.tensor(teacher_probs, device=device)
            target = target / target.sum().clamp(min=1e-8)
            scores = model(xt).squeeze(-1)
            log_probs = torch.log_softmax(scores, dim=0)
            loss = -(target * log_probs).sum()
            opt.zero_grad()
            loss.backward()
            opt.step()

    w1 = model[0].weight.detach().cpu().numpy().T.astype(np.float32)
    b1 = model[0].bias.detach().cpu().numpy().astype(np.float32)
    w2 = model[2].weight.detach().cpu().numpy().T.astype(np.float32)
    b2 = model[2].bias.detach().cpu().numpy().astype(np.float32)
    return {"w1": w1, "b1": b1, "w2": w2.squeeze(), "b2": b2}


def distill_from_maskable_ppo(
    src: Path,
    init: Path | None,
    episodes: int,
    epochs: int,
    deck_path: Path | None = None,
    opponents: str = "benchmark",
) -> tuple[dict | None, int]:
    """Teacher rollout + student train. Returns (weights, n_decisions)."""
    model, env = _load_teacher(src, deck_path, opponents)
    if model is None or env is None:
        return None, 0
    try:
        groups = collect_teacher_labels(model, env, episodes)
        if not groups:
            return None, 0
        weights = train_student(groups, init, epochs)
        return weights, len(groups)
    finally:
        env.close()


def latency_check(scorer: LearnedScorer, n: int = 200) -> float:
    obs = {
        "logs": [],
        "current": {"turn": 5, "yourIndex": 0, "players": [{}, {}]},
        "select": {
            "type": 0, "context": 0, "minCount": 1, "maxCount": 1,
            "option": [{"type": 14}, {"type": 7, "index": 0}, {"type": 13, "attackId": 1}],
        },
    }
    start = time.perf_counter()
    for _ in range(n):
        scorer.choose(obs, obs["select"], obs["current"], obs["select"]["option"])
    return (time.perf_counter() - start) / n * 1000.0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default=str(TORCH_MODEL))
    parser.add_argument("--fallback", default=str(BC_MODEL))
    parser.add_argument("--out", default=str(OUT_MODEL))
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--deck", default=str(ROOT / "agent" / "deck.csv"), help="Must match RL training deck")
    parser.add_argument("--opponents", choices=("benchmark", "pool"), default="benchmark")
    parser.add_argument("--package-dry-run", action="store_true")
    args = parser.parse_args(argv)

    deck_path = Path(args.deck)
    if not deck_path.is_absolute():
        deck_path = ROOT / deck_path

    init_path = Path(args.fallback) if Path(args.fallback).exists() else None
    weights, n_decisions = distill_from_maskable_ppo(
        Path(args.src), init_path, args.episodes, args.epochs, deck_path, args.opponents,
    )
    source = "torch_distill"
    if weights is None and Path(args.fallback).exists():
        data = np.load(args.fallback)
        weights = {k: data[k] for k in ("w1", "b1", "w2", "b2")}
        source = "bc_fallback"
        n_decisions = 0

    if weights is None:
        print("no torch or BC weights found")
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        feature_version=FEATURE_VERSION,
        state_dim=STATE_DIM,
        option_dim=OPTION_DIM,
        **weights,
    )

    scorer = LearnedScorer(model_path=out)
    ms_per_move = latency_check(scorer)
    gate_ok = ms_per_move < 50.0 and scorer.ready

    lines = [
        "# Distill policy gate",
        "",
        f"- Source: {source}",
        f"- Teacher decisions: {n_decisions}",
        f"- Output: `{out}`",
        f"- Latency: {ms_per_move:.2f} ms/move (budget <50 ms)",
        f"- Gate: **{'PASS' if gate_ok else 'FAIL'}**",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.package_dry_run:
        import subprocess

        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "package_submission.py"),
             "--name", "distilled_probe"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        lines.append(f"- Package dry-run: {'OK' if proc.returncode == 0 else proc.stderr}")
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"distilled to {out}; source={source} decisions={n_decisions} "
          f"latency={ms_per_move:.2f}ms gate={gate_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
