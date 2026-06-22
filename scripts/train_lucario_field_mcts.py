"""Local field-opponent RL+MCTS training for Mega Lucario ex.

Trains our Lucario deck vs field opponents. Opponents use **official Kaggle rule
samples** per archetype (Lucario / Dragapult / Iono / Abomasnow). Decks without
an official sample (mined Alakazam, Trevenant) use `--non-official-brain` (default
random) — never invented RuleCore pilots.

Matchup weakness levers (`agent/matchup_levers.py`) bias our MCTS root picks during
training via LucarioScorer.

  python scripts/train_lucario_field_mcts.py --device cpu --cycles 5

Fetch missing official kernels first (Iono, Abomasnow):

  powershell -File scripts/fetch_official_rule_samples.ps1
  python scripts/extract_public_agents.py
  python scripts/bootstrap_official_rule_agents.py

Outputs: rl_mcts_field/<work>/model{cycle}.pth, model_best.pth, metrics.csv, run_meta.json
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent import lucario_mcts_runtime as rt  # noqa: E402
from agent.lucario_policy import is_lucario_deck  # noqa: E402
from agent.native_opponent import make_opponent_brain, native_brain_label  # noqa: E402
from agent.official_registry import list_missing_official_samples  # noqa: E402

DEFAULT_OPPONENTS = [
    "real_mega_lucario_ex",
    "real_dragapult_ex",
    "real_mega_abomasnow_ex",
    "real_iono",
    "top_mined_alakazam",
    "top_mined_trevenant",
    "top_mined_dragapult_ex",
    "top_mined_iono",
    "top_mined_mega_abomasnow_ex",
    "top_mined_mega_lucario_ex",
]

METRICS_HEADER = [
    "cycle", "opponent", "phase", "wins", "losses", "draws", "wr_pct",
    "n_samples", "loss", "promoted", "elapsed_s",
]


def load_deck(path: Path) -> list[int]:
    ids = [int(line.strip()) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(ids) != 60:
        raise ValueError(f"{path} has {len(ids)} cards, expected 60")
    return ids


def discover_opponents(decks_dir: Path, names: list[str] | None) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    wanted = set(names or DEFAULT_OPPONENTS)
    for csv_path in sorted(decks_dir.glob("*.csv")):
        stem = csv_path.stem
        if stem not in wanted:
            continue
        out[stem] = load_deck(csv_path)
    missing = wanted - set(out)
    if missing:
        raise FileNotFoundError(f"missing opponent decks in {decks_dir}: {sorted(missing)}")
    return out


def games_for_opponent(opp_deck: list[int], base: int, lucario_mult: int) -> int:
    if lucario_mult > 1 and is_lucario_deck(opp_deck):
        return base * lucario_mult
    return base


def collect_vs_opponent(deck, opp_deck, opp_move, model, n_games: int) -> list:
    out: list = []
    for g in range(n_games):
        your_index = g % 2
        decks = (deck, opp_deck) if your_index == 0 else (opp_deck, deck)
        obs, start = rt.battle_start(*decks)
        if start.errorPlayer >= 0:
            raise ValueError(f"deck error type={start.errorType}")
        mine, ply = [], 0
        while obs["current"]["result"] < 0:
            if obs["current"]["yourIndex"] == your_index:
                temp = 1.0 if ply < rt.TEMP_PLIES else 0.0
                selected, sample = rt.mcts_agent(
                    obs, deck, model, opp_deck=opp_deck, add_noise=True, temperature=temp,
                )
                mine.append(sample)
            else:
                selected = opp_move(obs)
            obs = rt.battle_select(selected)
            ply += 1
        rt.battle_finish()
        rt.label_samples(mine, obs["current"]["result"], your_index, out)
    return out


def eval_matchup(deck, opp_deck, opp_move, model, games: int) -> tuple[int, int, int]:
    wins = losses = draws = 0
    model.eval()
    with torch.inference_mode():
        for i in range(games):
            your_index = i % 2
            decks = (deck, opp_deck) if your_index == 0 else (opp_deck, deck)
            obs, start = rt.battle_start(*decks)
            if start.errorPlayer >= 0:
                raise ValueError(f"deck error type={start.errorType}")
            while obs["current"]["result"] < 0:
                if obs["current"]["yourIndex"] == your_index:
                    selected, _ = rt.mcts_agent(obs, deck, model, opp_deck=opp_deck)
                else:
                    selected = opp_move(obs)
                obs = rt.battle_select(selected)
            rt.battle_finish()
            r = obs["current"]["result"]
            if r == 2:
                draws += 1
            elif r == your_index:
                wins += 1
            else:
                losses += 1
    return wins, losses, draws


def _append_metrics_row(metrics_path: Path, row: list) -> None:
    with metrics_path.open("a", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(row)
        fh.flush()


def opponents_without_official_sample(opponents: dict[str, list[int]]) -> set[str]:
    from agent.official_registry import official_archetype_for_opponent

    return {
        name for name, deck in opponents.items()
        if official_archetype_for_opponent(name, deck) is None
    }


def brain_kind(cli: str) -> str:
    """Map CLI brain flag to native_opponent kind."""
    if cli == "random":
        return "random"
    if cli == "non_official":
        return "non_official"
    return "native"


def preload_opponent_pilots(
    opponents: dict[str, list[int]],
    decks_dir: Path,
    args,
) -> dict[str, str]:
    """Build each opponent pilot once; fail fast if official sample missing."""
    resolved: dict[str, str] = {}
    for kind_attr in ("opponent_brain", "eval_opponent"):
        kind = brain_kind(getattr(args, kind_attr))
        for name, opp_deck in opponents.items():
            opp_path = str(decks_dir / f"{name}.csv")
            _, label = make_opponent_brain(
                kind,
                opp_path,
                opp_deck,
                opp_name=name,
                random_agent=rt.random_agent,
                non_official_brain=args.non_official_brain,
            )
            resolved[name] = label
    return resolved


def write_run_meta(
    work: Path,
    train_deck_path: Path,
    opponents: dict[str, list[int]],
    args,
    *,
    completed_cycles: int,
    source_checkpoint: str | None,
    opponent_brains: dict[str, str],
) -> None:
    meta = {
        "train_deck": str(train_deck_path.relative_to(ROOT)),
        "opponents": list(opponents.keys()),
        "cycles": args.cycles,
        "completed_cycles": completed_cycles,
        "source_checkpoint": source_checkpoint,
        "opponent_brains": opponent_brains,
        "config": {
            "LUC_D_MODEL": rt.D_MODEL,
            "LUC_HEADS": rt.NUM_HEADS,
            "LUC_D_FF": rt.D_FF,
            "LUC_ENC_LAYERS": rt.ENC_LAYERS,
            "LUC_DEC_LAYERS": rt.DEC_LAYERS,
            "LUC_SEARCH_COUNT": rt.SEARCH_COUNT,
            "opponent_brain": args.opponent_brain,
            "eval_opponent": args.eval_opponent,
            "mirror_brain": args.mirror_brain,
            "lucario_game_mult": args.lucario_game_mult,
            "lever_blend": args.lever_blend,
            "non_official_brain": args.non_official_brain,
        },
    }
    with (work / "run_meta.json").open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--train-deck", default="agent_decks/real_mega_lucario_ex.csv")
    ap.add_argument("--decks-dir", default="agent_decks")
    ap.add_argument("--opponents", default="", help="Comma-separated stems; default = 10 field decks")
    ap.add_argument("--cycles", type=int, default=5)
    ap.add_argument("--start-cycle", type=int, default=0)
    ap.add_argument("--games-per-opponent", type=int, default=20)
    ap.add_argument("--lucario-game-mult", type=int, default=2,
                    help="Extra training games vs Lucario mirror decks (meta ~53%%)")
    ap.add_argument("--selfplay-games", type=int, default=40)
    ap.add_argument("--eval-games", type=int, default=20)
    ap.add_argument(
        "--opponent-brain", default="non_official",
        choices=("native", "non_official", "random"),
        help="native=official samples only; non_official=official + random for Alakazam/Trevenant",
    )
    ap.add_argument(
        "--eval-opponent", default="non_official",
        choices=("native", "non_official", "random"),
    )
    ap.add_argument(
        "--non-official-brain", default="random", choices=("random",),
        help="Pilot for decks with no official Kaggle sample (Alakazam, Trevenant)",
    )
    ap.add_argument(
        "--lever-blend", type=float, default=0.35,
        help="Matchup-lever bias on our MCTS root picks (0=off, LucarioScorer levers)",
    )
    ap.add_argument(
        "--mirror-brain", default="native",
        choices=("native", "mcts", "random"),
        help="Mirror practice: MCTS vs native Lucario rules (default), MCTS self-play, or random",
    )
    ap.add_argument("--search-count", type=int, default=12)
    ap.add_argument("--gate-games", type=int, default=20)
    ap.add_argument("--gate-winrate", type=float, default=0.55)
    ap.add_argument("--replay-iters", type=int, default=2)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--device", default="cpu", choices=("cpu", "cuda", "auto"))
    ap.add_argument("--work", default="rl_mcts_field/lucarioex_v2")
    ap.add_argument("--resume-from", default="", help="Load model weights from .pth before training")
    ap.add_argument("--append-metrics", action="store_true",
                    help="Append to existing metrics.csv instead of overwriting")
    ap.add_argument("--time-budget-sec", type=float, default=0.0, help="0 = no limit")
    ap.add_argument("--smoke", action="store_true", help="1 cycle, 2 games/opponent")
    args = ap.parse_args(argv)

    if args.smoke:
        args.cycles = 1
        args.games_per_opponent = 2
        args.selfplay_games = 4
        args.eval_games = 2
        args.gate_games = 4
        args.lucario_game_mult = 1

    rt.SEARCH_COUNT = args.search_count
    rt.GATE_GAMES = args.gate_games
    rt.GATE_WINRATE = args.gate_winrate
    rt.REPLAY_ITERS = args.replay_iters
    rt.BATCH_SIZE = args.batch_size
    rt.LR = args.lr
    rt.SELFPLAY_GAMES = args.selfplay_games
    rt.EVAL_GAMES = args.eval_games

    random.seed(rt.SEED)
    torch.manual_seed(rt.SEED)

    train_deck_path = ROOT / args.train_deck
    deck = load_deck(train_deck_path)
    decks_dir = ROOT / args.decks_dir
    opp_names = [s.strip() for s in args.opponents.split(",") if s.strip()] or None
    opponents = discover_opponents(decks_dir, opp_names)

    allow_non_official = opponents_without_official_sample(opponents)
    if args.opponent_brain == "native" and args.eval_opponent == "native":
        allow_non_official = set()
    missing = list_missing_official_samples(opponents, allow_non_official=allow_non_official)
    if missing:
        print(
            "ERROR: no official Kaggle rule sample for: " + ", ".join(sorted(missing)),
            flush=True,
        )
        print(
            "Fetch kernels: powershell -File scripts/fetch_official_rule_samples.ps1",
            flush=True,
        )
        print(
            "Or use --opponent-brain non_official (random only for Alakazam/Trevenant).",
            flush=True,
        )
        return 2

    try:
        preload_opponent_pilots(opponents, decks_dir, args)
    except (FileNotFoundError, ModuleNotFoundError, ValueError) as exc:
        print(f"ERROR: cannot load official opponent pilot: {exc}", flush=True)
        print("Run: powershell -File scripts/fetch_official_rule_samples.ps1", flush=True)
        print("     python scripts/extract_public_agents.py", flush=True)
        return 2

    work = ROOT / args.work
    work.mkdir(parents=True, exist_ok=True)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    opponent_brains: dict[str, str] = {
        name: native_brain_label(ids, name) for name, ids in opponents.items()
    }

    train_deck_str = str(train_deck_path)
    rt.set_lucario_lever_teaching(train_deck_str, blend=args.lever_blend)
    print(f"lever_blend={args.lever_blend} (matchup_levers via LucarioScorer)", flush=True)

    print(
        f"device={device} search={rt.SEARCH_COUNT} cycles={args.cycles} "
        f"start_cycle={args.start_cycle} opponents={len(opponents)} work={work}",
        flush=True,
    )
    for name, label in sorted(opponent_brains.items()):
        print(f"  opponent {name}: native={label}", flush=True)

    model = rt.MyModel(rt.D_MODEL, rt.NUM_HEADS, rt.D_FF, rt.ENC_LAYERS, rt.DEC_LAYERS).to(device)
    champion = rt.MyModel(rt.D_MODEL, rt.NUM_HEADS, rt.D_FF, rt.ENC_LAYERS, rt.DEC_LAYERS).to(device)

    source_checkpoint: str | None = None
    resume_path = args.resume_from.strip()
    if resume_path:
        ckpt = ROOT / resume_path if not Path(resume_path).is_absolute() else Path(resume_path)
        model.load_state_dict(torch.load(ckpt, map_location=device, weights_only=True))
        source_checkpoint = str(ckpt.relative_to(ROOT)) if ckpt.is_relative_to(ROOT) else str(ckpt)
        print(f"resumed weights from {ckpt}", flush=True)

    best_path = work / "model_best.pth"
    if best_path.exists() and not resume_path:
        champion.load_state_dict(torch.load(best_path, map_location=device, weights_only=True))
        print(f"loaded champion from {best_path}", flush=True)
    else:
        champion.load_state_dict(model.state_dict())

    mirror_move = None
    if args.mirror_brain == "native":
        mirror_move, _ = make_opponent_brain(
            "native",
            train_deck_str,
            deck,
            opp_name="mirror",
            random_agent=rt.random_agent,
            non_official_brain=args.non_official_brain,
        )
    elif args.mirror_brain == "random":
        mirror_move = rt.random_agent

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    remaining = max(1, (args.cycles - args.start_cycle) * len(opponents))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=remaining)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    loss_fn_enc = torch.nn.HuberLoss(delta=0.2)
    loss_fn_dec = torch.nn.HuberLoss(reduction="none", delta=0.1)

    metrics_path = work / "metrics.csv"
    if args.append_metrics and metrics_path.exists():
        pass
    else:
        with metrics_path.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(METRICS_HEADER)

    replay: list[list] = []
    t0 = time.time()
    completed_cycles = args.start_cycle
    interrupted = False

    try:
        for cycle in range(args.start_cycle, args.cycles):
            if args.time_budget_sec > 0 and time.time() - t0 > args.time_budget_sec:
                print(f"time budget reached before cycle {cycle}", flush=True)
                break

            torch.save(model.state_dict(), work / f"model{cycle}.pth")
            eval_summary: dict[str, float] = {}

            for opp_name, opp_deck in opponents.items():
                opp_path = str(decks_dir / f"{opp_name}.csv")
                opp_move, brain = make_opponent_brain(
                    brain_kind(args.eval_opponent),
                    opp_path,
                    opp_deck,
                    opp_name=opp_name,
                    random_agent=rt.random_agent,
                    non_official_brain=args.non_official_brain,
                )
                w, l, d = eval_matchup(deck, opp_deck, opp_move, champion, args.eval_games)
                wr = 100.0 * w / max(1, w + l)
                eval_summary[opp_name] = wr
                print(
                    f"[cycle {cycle}] eval {opp_name} ({brain}): {wr:.1f}% (W{w}/L{l}/D{d})",
                    flush=True,
                )
                _append_metrics_row(metrics_path, [
                    cycle, opp_name, "eval", w, l, d, round(wr, 1), 0, "", 0,
                    round(time.time() - t0, 1),
                ])

            cycle_samples: list = []
            if args.mirror_brain == "mcts":
                for _ in rt.progress(args.selfplay_games, f"[cycle {cycle}] mirror mcts"):
                    cycle_samples.extend(rt.selfplay_game(model, deck))
            elif mirror_move is not None:
                n_mirror = args.selfplay_games
                for _ in rt.progress(n_mirror, f"[cycle {cycle}] mirror vs rules"):
                    got = collect_vs_opponent(deck, deck, mirror_move, model, 1)
                    cycle_samples.extend(got)
            else:
                for _ in rt.progress(args.selfplay_games, f"[cycle {cycle}] mirror vs random"):
                    got = collect_vs_opponent(deck, deck, rt.random_agent, model, 1)
                    cycle_samples.extend(got)

            for opp_name, opp_deck in opponents.items():
                opp_path = str(decks_dir / f"{opp_name}.csv")
                opp_move, brain = make_opponent_brain(
                    brain_kind(args.opponent_brain),
                    opp_path,
                    opp_deck,
                    opp_name=opp_name,
                    random_agent=rt.random_agent,
                    non_official_brain=args.non_official_brain,
                )
                n_games = games_for_opponent(opp_deck, args.games_per_opponent, args.lucario_game_mult)
                got = collect_vs_opponent(deck, opp_deck, opp_move, model, n_games)
                cycle_samples.extend(got)
                print(
                    f"[cycle {cycle}] +{len(got)} samples vs {opp_name} ({brain}, {n_games}g)",
                    flush=True,
                )

            replay.append(cycle_samples)
            if len(replay) > args.replay_iters:
                replay.pop(0)
            train_pool = [s for chunk in replay for s in chunk]

            loss = rt.train_on_samples(
                model, optimizer, scheduler, scaler, device, loss_fn_enc, loss_fn_dec, train_pool,
            )
            gate_wr = rt.eval_vs_model(model, champion, deck, args.gate_games)
            promoted = gate_wr >= args.gate_winrate
            if promoted:
                champion.load_state_dict(model.state_dict())

            torch.save(model.state_dict(), work / "model_latest.pth")
            if promoted:
                torch.save(champion.state_dict(), work / "model_best.pth")

            mean_wr = sum(eval_summary.values()) / max(1, len(eval_summary))
            completed_cycles = cycle + 1
            print(
                f"[cycle {cycle}] loss={loss:.4f} gate={gate_wr:.3f} promoted={int(promoted)} "
                f"mean_eval_wr={mean_wr:.1f}% samples={len(train_pool)}",
                flush=True,
            )
            _append_metrics_row(metrics_path, [
                cycle, "ALL", "train", "", "", "", round(mean_wr, 1),
                len(train_pool), round(loss, 5), int(promoted), round(time.time() - t0, 1),
            ])

            write_run_meta(
                work, train_deck_path, opponents, args,
                completed_cycles=completed_cycles,
                source_checkpoint=source_checkpoint,
                opponent_brains=opponent_brains,
            )
    except KeyboardInterrupt:
        interrupted = True
        torch.save(model.state_dict(), work / "model_latest.pth")
        if not (work / "model_best.pth").exists():
            torch.save(champion.state_dict(), work / "model_best.pth")
        write_run_meta(
            work, train_deck_path, opponents, args,
            completed_cycles=completed_cycles,
            source_checkpoint=source_checkpoint,
            opponent_brains=opponent_brains,
        )
        print(f"\nINTERRUPTED at completed_cycles={completed_cycles} -> saved latest", flush=True)
        return 130

    if not (work / "model_best.pth").exists():
        torch.save(champion.state_dict(), work / "model_best.pth")

    write_run_meta(
        work, train_deck_path, opponents, args,
        completed_cycles=completed_cycles,
        source_checkpoint=source_checkpoint,
        opponent_brains=opponent_brains,
    )

    print(f"DONE -> {work}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
