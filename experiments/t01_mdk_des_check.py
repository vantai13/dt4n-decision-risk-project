"""Verify mdk.py independently with workload simulation and 95% CIs."""

import numpy as np
from scipy import stats

from ndtrisk.theory.mdk import mdk

N_PKT, SEEDS = 200_000, range(9001, 9021)
CASES = [(0.5, 2), (0.8, 11), (1.0, 11), (0.95, 100), (0.9, 30), (0.8, 30)]


def simulate(rho, k_sys, seed):
    """Return loss and accepted-packet Wq from workload recursion (S=1)."""
    gaps = np.random.default_rng(seed).exponential(1.0 / rho, N_PKT)
    workload, drops, wait_sum = 0.0, 0, 0.0
    full = k_sys - 1.0
    for gap in gaps:
        workload = max(0.0, workload - gap)
        if workload > full:
            drops += 1
        else:
            wait_sum += workload
            workload += 1.0
    return drops / N_PKT, wait_sum / (N_PKT - drops)


if __name__ == "__main__":
    critical = stats.t.ppf(0.975, len(SEEDS) - 1)
    print(
        f"{'rho':>5} {'K':>4} | {'loss DES (CI95)':>21} {'exact':>9} | "
        f"{'Wq DES (CI95)':>17} {'exact':>7} | trong CI 95%?"
    )
    for rho, k_sys in CASES:
        samples = np.array([simulate(rho, k_sys, seed) for seed in SEEDS])
        mean = samples.mean(axis=0)
        half_width = critical * samples.std(axis=0, ddof=1) / np.sqrt(len(SEEDS))
        exact = mdk(rho, k_sys)
        expected_drops = exact.loss * N_PKT * len(SEEDS)
        wait_ok = abs(mean[1] - exact.wait) <= half_width[1]
        if expected_drops < 100:
            verdict = f"Wq {'có' if wait_ok else 'KHÔNG'}; loss: không đủ sự kiện (~{expected_drops:.0f})"
        else:
            loss_ok = abs(mean[0] - exact.loss) <= half_width[0]
            verdict = f"loss {'có' if loss_ok else 'KHÔNG'}, Wq {'có' if wait_ok else 'KHÔNG'}"
        print(
            f"{rho:5.2f} {k_sys:4d} | {mean[0]:.6f} ± {half_width[0]:.6f} {exact.loss:9.6f} | "
            f"{mean[1]:8.4f} ± {half_width[1]:.4f} {exact.wait:7.4f} | {verdict}"
        )
