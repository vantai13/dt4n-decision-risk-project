"""Kiểm bộ ước lượng trên OU-box/Poisson tổng hợp, KHÔNG chạy DES/seed v6.

Sinh chính xác trung bình OU từng cửa sổ bằng nhiễu Gaussian joint giữa
OU cuối cửa sổ và tích phân. Mất 20% bản tin độc lập tải, giữ clock gaps.
Chạy: python -m experiments.scan.check_telemetry_fit.
"""
import csv
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

from experiments.scan.telemetry_fit import box_variance, estimate


def synthetic_observations(rng, n, rho, sigma, tau, T, S, missing=.2):
    x = T / tau
    phi = np.exp(-x)
    a = -np.expm1(-x) / x
    cov = np.array([[sigma*sigma * -np.expm1(-2*x),
                     sigma*sigma * a * -np.expm1(-x)],
                    [sigma*sigma * a * -np.expm1(-x),
                     box_variance(T, sigma, tau) - a*a*sigma*sigma]])
    eta, avg_noise = rng.multivariate_normal([0., 0.], cov, size=n).T
    x0 = rng.normal(0., sigma)
    end, _ = lfilter([1.], [1., -phi], eta, zi=[phi*x0])
    previous = np.r_[x0, end[:-1]]
    avg = rho + a*previous + avg_noise
    counts = rng.poisson(np.maximum(avg, 0.) * T / S)
    y = counts * S / T
    keep = rng.random(n) >= missing
    keep[0] = True
    j = np.maximum.accumulate(np.where(keep, np.arange(n), 0))
    message_at = T * (np.arange(n) + 1)
    decision_at = message_at + .1
    return dict(rhohat=y[j], age=decision_at - message_at[j], decision_times=decision_at)


def main():
    cases = ((.8, .14, 60., 1.), (.7, .10, 15., 1.), (.9, .08, 120., 10.))
    S = 1512*8 / 20e6
    rows, detail = [], []
    for i, (rho, sig, tau, T) in enumerate(cases):
        rng = np.random.default_rng([20261001, 42, i])
        observation = synthetic_observations(rng, 100000, rho, sig, tau, T, S)
        result = estimate([observation], T, S)
        row = dict(case=i, T_s=T, true_rho=rho, fit_rho=result.rho_bar,
                   true_sigma=sig, fit_sigma=result.sigma, true_tau_s=tau, fit_tau_s=result.tau,
                   rho_abs_error=abs(result.rho_bar-rho),
                   sigma_error_pct=100*(result.sigma/sig-1), tau_error_pct=100*(result.tau/tau-1),
                   n_fresh_messages=result.n_messages, warnings=";".join(result.warnings))
        rows.append(row)
        detail.append(asdict(result))
        print(f"T={T:g} s | ρ̄ {rho:.3f} → {result.rho_bar:.4f} | "
              f"σ {sig:.3f} → {result.sigma:.4f} ({row['sigma_error_pct']:+.1f}%) | "
              f"τ {tau:g} → {result.tau:.2f} s ({row['tau_error_pct']:+.1f}%) | "
              f"n={result.n_messages}, warnings={result.warnings}", flush=True)
    output = Path("results/go_test")
    output.mkdir(parents=True, exist_ok=True)
    with (output / "telemetry_fit_synthetic.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output / "telemetry_fit_synthetic.json").write_text(json.dumps({
        "classification": "synthetic estimator validation only; not a v6 DES outcome",
        "rng_entropy": [20261001, 42, "case_index"], "epochs_per_case": 100000,
        "missing_message_probability": .2, "results": detail,
        "reserved_des_seed_ranges_not_run": [[90001, 90020], [91001, 91020]],
    }, indent=2, ensure_ascii=False) + "\n")


if __name__ == '__main__':
    main()
