# batch_compare.py
import argparse
import csv
import importlib
import math
import os
import statistics
import sys
import time
from dataclasses import dataclass

import matplotlib.pyplot as plt

from my_lstar.learner import LStar
from my_ttt.learner import TTTLearner
from api_alphabet import ALPHABET

# We will NOT edit equivalence.py. We'll monkey-patch it at runtime.
import equivalence as eq


# -------------------------------
# Config
# -------------------------------
ORACLE_MODULES = {
    "simple": "oracle_simple",
    "medium": "oracle_medium",
    "complex": "oracle",
}


@dataclass
class RunResult:
    mode: str
    trial: int
    algo: str
    status: str          # OK / TIMEOUT / ERROR
    seconds: float
    mq: int
    rpc: int
    error: str = ""


# -------------------------------
# Timeout runner (Unix only, but you're on Ubuntu VM)
# -------------------------------
def run_with_timeout(fn, timeout_s: int):
    """
    Run fn() with a hard timeout. Returns (status, value_or_errstr).
    status: "OK" | "TIMEOUT" | "ERROR"
    """
    import signal

    class _Timeout(Exception):
        pass

    def _handler(signum, frame):
        raise _Timeout()

    old = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(timeout_s)

    try:
        v = fn()
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
        return "OK", v
    except _Timeout:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
        return "TIMEOUT", f"timeout>{timeout_s}s"
    except Exception as e:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
        return "ERROR", repr(e)


# -------------------------------
# Single run
# -------------------------------
def run_once(mode: str, algo: str, timeout_s: int, seed: int, num_tests: int, max_len: int) -> RunResult:
    # load oracle module
    omod = importlib.import_module(ORACLE_MODULES[mode])

    membership_oracle = getattr(omod, "membership_oracle")
    reset_counter = getattr(omod, "reset_counter")
    API_CALL_COUNT = getattr(omod, "API_CALL_COUNT")
    RPC_CALL_COUNT = getattr(omod, "RPC_CALL_COUNT")

    # monkey-patch equivalence.py to use THIS mode's membership_oracle
    eq.membership_oracle = membership_oracle

    # reset counts + cache
    reset_counter()

    def _learn():
        # IMPORTANT: use eq.equivalence_oracle (function), not module
        # Also: keep your equivalence.py unchanged; we only patch membership_oracle used inside it.
        if algo == "L*":
            learner = LStar(ALPHABET, membership_oracle, eq.equivalence_oracle)
        elif algo == "TTT":
            learner = TTTLearner(ALPHABET, membership_oracle, eq.equivalence_oracle)
        else:
            raise ValueError(algo)
        return learner.learn()

    t0 = time.time()
    status, val = run_with_timeout(_learn, timeout_s=timeout_s)
    t1 = time.time()

    if status == "OK":
        # learned DFA is in val, but we don't need it here
        return RunResult(
            mode=mode,
            trial=trial_global(),  # placeholder, will overwrite outside
            algo=algo,
            status="OK",
            seconds=t1 - t0,
            mq=int(API_CALL_COUNT()),
            rpc=int(RPC_CALL_COUNT()),
            error=""
        )
    else:
        return RunResult(
            mode=mode,
            trial=trial_global(),  # placeholder, will overwrite outside
            algo=algo,
            status=status,
            seconds=t1 - t0,
            mq=int(API_CALL_COUNT()),
            rpc=int(RPC_CALL_COUNT()),
            error=str(val)
        )


# A tiny helper so we can set trial later without threading globals through.
_TRIAL = 0
def set_trial_global(x: int):
    global _TRIAL
    _TRIAL = x

def trial_global() -> int:
    return _TRIAL


# -------------------------------
# Summary helpers
# -------------------------------
def mean_std(values):
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return float(values[0]), 0.0
    return float(statistics.mean(values)), float(statistics.stdev(values))


def write_csv_results(path: str, results: list[RunResult]):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "trial", "algo", "status", "seconds", "mq", "rpc", "error"])
        for r in results:
            w.writerow([r.mode, r.trial, r.algo, r.status, f"{r.seconds:.6f}", r.mq, r.rpc, r.error])


def write_csv_summary(path: str, results: list[RunResult]):
    # group by (mode, algo)
    groups = {}
    for r in results:
        groups.setdefault((r.mode, r.algo), []).append(r)

    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mode", "algo",
                    "ok_runs", "timeouts", "errors",
                    "time_mean", "time_std",
                    "mq_mean", "mq_std",
                    "rpc_mean", "rpc_std"])
        for (mode, algo), rs in sorted(groups.items()):
            ok = [x for x in rs if x.status == "OK"]
            timeouts = sum(1 for x in rs if x.status == "TIMEOUT")
            errors = sum(1 for x in rs if x.status == "ERROR")

            tvals = [x.seconds for x in ok]
            mqvals = [x.mq for x in ok]
            rpcvals = [x.rpc for x in ok]

            t_mean, t_std = mean_std(tvals)
            mq_mean, mq_std = mean_std(mqvals)
            rpc_mean, rpc_std = mean_std(rpcvals)

            w.writerow([mode, algo,
                        len(ok), timeouts, errors,
                        f"{t_mean:.6f}", f"{t_std:.6f}",
                        f"{mq_mean:.3f}", f"{mq_std:.3f}",
                        f"{rpc_mean:.3f}", f"{rpc_std:.3f}"])


def add_bar_labels(ax, bars, fmt="{:.2f}", y_pad_ratio=0.02):
    y_min, y_max = ax.get_ylim()
    y_range = y_max - y_min if y_max != y_min else 1.0
    pad = y_range * y_pad_ratio
    for bar in bars:
        h = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2.0
        ax.text(x, h + pad, fmt.format(h), ha="center", va="bottom", fontsize=9)


def plot_pdf(path: str, results: list[RunResult], trials: int):
    # compute means for OK runs
    modes = ["simple", "medium", "complex"]
    algos = ["L*", "TTT"]

    # metric -> dict[(mode,algo)] = mean
    mean_time = {}
    mean_mq = {}
    mean_rpc = {}

    for mode in modes:
        for algo in algos:
            ok = [r for r in results if r.mode == mode and r.algo == algo and r.status == "OK"]
            mean_time[(mode, algo)] = statistics.mean([r.seconds for r in ok]) if ok else float("nan")
            mean_mq[(mode, algo)] = statistics.mean([r.mq for r in ok]) if ok else float("nan")
            mean_rpc[(mode, algo)] = statistics.mean([r.rpc for r in ok]) if ok else float("nan")

    fig, axes = plt.subplots(3, 3, figsize=(12, 9))
    fig.suptitle(f"Batch Comparison (trials/mode={trials})", fontsize=14)

    metrics = [
        ("Execution Time (s)", mean_time, "{:.2f}"),
        ("Membership Queries (MQ)", mean_mq, "{:.0f}"),
        ("JSON-RPC Calls", mean_rpc, "{:.0f}"),
    ]
    for i, mode in enumerate(modes):
        for j, (title, mdict, fmt) in enumerate(metrics):
            ax = axes[i][j]
            vals = [mdict[(mode, "L*")], mdict[(mode, "TTT")]]

            bars = ax.bar(["L*", "TTT"], vals)
            ax.set_title(f"{mode} — {title}")
            add_bar_labels(ax, bars, fmt=fmt)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(path)
    plt.close(fig)


# -------------------------------
# Main
# -------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=15)      # per run
    ap.add_argument("--num-tests", type=int, default=200)   # (not used by eq.py directly; kept for future)
    ap.add_argument("--max-len", type=int, default=6)       # (not used by eq.py directly; kept for future)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    print("[batch] starting...")
    print("[batch] ALPHABET =", ALPHABET)
    print("[batch] oracle modules =", ORACLE_MODULES)
    print(f"[batch] trials/mode={args.trials}, timeout/run={args.timeout}s")

    results: list[RunResult] = []

    # NOTE: your equivalence.py sets random.seed(0) globally, and uses its own templates + random.
    # We'll still vary seed only for our own reproducibility if you later extend eq.py.
    base_seed = args.seed

    for mode in ["complex", "medium", "simple"]:
        for trial in range(1, args.trials + 1):
            set_trial_global(trial)
            seed = base_seed + trial

            rL = run_once(mode, "L*", args.timeout, seed, args.num_tests, args.max_len)
            rL.trial = trial
            rT = run_once(mode, "TTT", args.timeout, seed, args.num_tests, args.max_len)
            rT.trial = trial

            results.append(rL)
            results.append(rT)

            if rL.status == "OK":
                ltxt = f"{rL.seconds:.2f}s MQ={rL.mq} RPC={rL.rpc}"
            else:
                ltxt = rL.status
            if rT.status == "OK":
                ttxt = f"{rT.seconds:.2f}s MQ={rT.mq} RPC={rT.rpc}"
            else:
                ttxt = rT.status

            print(f"[{mode} trial {trial:02d}] L*: {ltxt} | TTT: {ttxt}")

    write_csv_results("batch_results.csv", results)
    write_csv_summary("batch_summary.csv", results)
    plot_pdf("batch_comparison.pdf", results, trials=args.trials)

    print("[batch] wrote batch_results.csv and batch_summary.csv")
    print("[batch] wrote batch_comparison.pdf")


if __name__ == "__main__":
    main()
