# ─── PROVENANCE (thêm 2026-09-25, Phase 0 v2 / L0.1) ────────────────────────────
# Tạo bởi : tác giả và công cụ AI, ngày 2026-09-24, khi viết thuyết minh v14
# Sinh ra : results/switch_or_stay_diagnostic.txt (trích ở thuyết minh v14 §6.1)
# Trạng thái: PILOT/CHẨN ĐOÁN trước plan — KHÔNG phải bằng chứng cho RQ1/RQ2
# Seed    : 1 cho mô phỏng hàng đợi; 42 cho kiểm tra quyết định
# Đã biết : số "M/D/1/K" trong output là 1 seed; nghiệm chính xác: decision log
# Chạy lại: python experiments/pilot/switch_or_stay_diagnostic.py
# ──────────────────────────────────────────────────────────────────────────
"""Foundation checks for stale-telemetry path switching.

This validates queueing assumptions and the one-step decision mechanism.  It is
not the complete sequential DES used to answer the research questions.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtr


def mm1k_exact(rho: float, capacity: int) -> tuple[float, float]:
    """Return (loss, mean time in system) in service-time units."""
    states = np.arange(capacity + 1)
    weights = rho**states
    probs = weights / weights.sum()
    loss = float(probs[-1])
    admitted_rate = rho * (1.0 - loss)
    mean_number = float(np.dot(states, probs))
    return loss, mean_number / admitted_rate


def simulate_queue(
    rho: float,
    capacity: int,
    service: str,
    packets: int = 300_000,
    seed: int = 1,
) -> tuple[float, float]:
    """Return (loss, mean waiting time) in service-time units for M/?/1/K."""
    rng = np.random.default_rng(seed)
    arrivals = np.cumsum(rng.exponential(1.0 / rho, packets))
    services = (
        np.ones(packets)
        if service == "det"
        else rng.exponential(1.0, packets)
    )
    departures: deque[float] = deque()
    last_departure = 0.0
    drops = 0
    waits: list[float] = []
    for arrival, duration in zip(arrivals, services):
        while departures and departures[0] <= arrival:
            departures.popleft()
        if len(departures) >= capacity:
            drops += 1
            continue
        start = max(arrival, last_departure)
        last_departure = start + duration
        departures.append(last_departure)
        waits.append(start - arrival)
    return drops / packets, float(np.mean(waits))


def print_queue_checks(mininet_path: Path) -> None:
    print("[1] Queue model check: K counts packets in system; testbed packets are fixed")
    print("rho  MM1K_loss  MM1K_wait_S  MD1K_loss  MD1K_wait_S")
    for rho in (0.80, 0.90, 1.00):
        mm_loss, _ = mm1k_exact(rho, 11)
        _, mm_wait = simulate_queue(rho, 11, "exp")
        md_loss, md_wait = simulate_queue(rho, 11, "det")
        print(
            f"{rho:0.2f}  {mm_loss:10.4%}  {mm_wait:11.3f}  "
            f"{md_loss:10.4%}  {md_wait:11.3f}"
        )

    print("\n[2] Validation against Mininet poisson|4Mbps|q=10 (K=q+1=11)")
    frame = pd.read_parquet(mininet_path)
    measured = frame[
        (frame["mode"] == "poisson")
        & (frame["bw"] == 4.0)
        & (frame["q"] == 10)
    ].set_index("rho")
    service_ms = 1512 * 8 / 4e6 * 1e3
    print("rho  MD1K_loss  Mininet_loss  MD1K_wait_S  Mininet_wait_S")
    for rho in (0.80, 0.90, 1.00):
        md_loss, md_wait = simulate_queue(rho, 11, "det")
        row = measured.loc[rho]
        print(
            f"{rho:0.2f}  {md_loss:10.4%}  {row['loss']:12.4%}  "
            f"{md_wait:11.3f}  {row['delay_mean_ms']/service_ms:14.3f}"
        )


def calibrated_threshold(
    score: np.ndarray, harmful: np.ndarray, budget_per_epoch: float
) -> float:
    """Largest switching set satisfying harmful events / all epochs <= budget."""
    order = np.argsort(score)[::-1]
    cumulative_harm = np.cumsum(harmful[order])
    valid = np.flatnonzero(cumulative_harm <= budget_per_epoch * score.size)
    if valid.size == 0:
        return float(np.nextafter(score.max(), np.inf))
    return float(score[order[valid[-1]]])


def print_decision_check() -> None:
    print("\n[3] One-step decision check (rates use all decision epochs)")
    print("harm budget=1%; missed means missed events / all epochs")
    print("sd_log_s  method     harmful    missed    switch")
    n = 400_000
    split = n // 2
    eps = 0.5
    for spread in (0.00, 0.25, 0.50, 1.00):
        rng = np.random.default_rng(42)
        scale = np.exp(rng.normal(-spread * spread / 2.0, spread, n))
        scale = np.clip(scale, 0.25, 4.0)
        truth = rng.normal(1.0, 3.0, n)
        observed = truth + rng.normal(size=n) * scale

        posterior_var = 1.0 / (1.0 / 9.0 + 1.0 / scale**2)
        posterior_mean = posterior_var * (1.0 / 9.0 + observed / scale**2)
        posterior_sd = np.sqrt(posterior_var)
        p_up = 1.0 - ndtr((eps - posterior_mean) / posterior_sd)
        p_down = ndtr((-eps - posterior_mean) / posterior_sd)
        posterior_score = np.log(np.maximum(p_up, 1e-300)) - np.log(
            np.maximum(p_down, 1e-300)
        )

        harmful = truth < -eps
        beneficial = truth > eps
        scores = (
            ("fixed", observed),
            ("scaled", observed / scale),
            ("posterior", posterior_score),
        )
        for name, score in scores:
            threshold = calibrated_threshold(
                score[:split], harmful[:split], budget_per_epoch=0.01
            )
            switch = score[split:] > threshold
            harm_rate = np.mean(harmful[split:] & switch)
            missed_rate = np.mean(beneficial[split:] & ~switch)
            print(
                f"{spread:8.2f}  {name:9s}  {harm_rate:8.4%}  "
                f"{missed_rate:8.4%}  {switch.mean():8.4%}"
            )


def parse_args() -> argparse.Namespace:
    default_data = Path(__file__).resolve().parents[2] / "data/mininet_calibration/truth_table.parquet"
    parser = argparse.ArgumentParser()
    parser.add_argument("--mininet", type=Path, default=default_data)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print_queue_checks(args.mininet)
    print_decision_check()
