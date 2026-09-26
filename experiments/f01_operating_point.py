"""F1: locate the measured-AoI anchor in dimensionless operating space.

[đo] fields come from data/aoi_measured. [giả định] fields are sweep axes
whose rationale is documented in notes/feasibility/F1_operating_point.md.
No random seed is needed.
"""

import json
from pathlib import Path

import numpy as np

AOI_FILE = Path("data/aoi_measured/aoi_v7_estimates.json")

A_ACT = 0.05
TAUS = (0.5, 2.0, 10.0, 60.0)
SIGMAS = (0.01, 0.03, 0.06, 0.10)
RHO_BARS = (0.5, 0.7, 0.85, 0.95)
SPEEDS_MBPS = (4, 8, 100)
PKT_BYTES = 1512


def v_avg(length, sigma, tau):
    x = length / tau
    return 2 * sigma**2 * (x - 1 + np.exp(-x)) / x**2


def a_avg(length, tau):
    x = length / tau
    return (1 - np.exp(-x)) / x


def hold_posterior(sigma, tau, window, noise_var, gap, hold):
    covariance = sigma**2 * np.exp(-gap / tau) * a_avg(window, tau) * a_avg(hold, tau)
    var_y = v_avg(window, sigma, tau) + noise_var
    var_prior = v_avg(hold, sigma, tau)
    return covariance / var_y, var_prior - covariance**2 / var_y, var_prior


def load_anchor(mode):
    """Load AoI=t-t_m and infer the sawtooth pipeline offset."""
    estimates = json.loads(AOI_FILE.read_text())["modes"][mode]
    aoi = estimates["aoi"]
    t_poll = estimates["effective_period"]["median_s"]
    pipeline_delay = aoi["p05"] - 0.05 * t_poll
    return {
        "mode": mode,
        "t_poll": t_poll,
        "W": t_poll,
        "H": t_poll,
        "d": pipeline_delay,
        "lag_p05": aoi["p05"],
        "lag_p50": aoi["p50"],
        "lag_mean": aoi["mean"],
        "lag_p95": aoi["p95"],
        "lag_p99": aoi["p99"],
        "lag_max": aoi["max"],
        "sd": aoi["sd"],
        "corr_rho": estimates["aoi_rho"]["pearson"],
    }


if __name__ == "__main__":
    beta, _, _ = hold_posterior(
        0.03, 10.0, 0.5, 0.9 * 1512 * 8 / 4e6 / 0.5, 0.5, 0.5
    )
    assert abs(beta - 0.129) < 0.001, beta

    for mode in ("clean", "prod"):
        anchor = load_anchor(mode)
        uniform_sd = anchor["t_poll"] / np.sqrt(12)
        print(f"\n== Điểm neo [{mode}]  (nhãn: đo)")
        print(
            f"  T_poll = W = H = {anchor['t_poll']:.4f} s;  "
            f"d = P05 − 0,05·T = {anchor['d']:.4f} s;  "
            f"corr(AoI, ρ) = {anchor['corr_rho']:+.3f}"
        )
        print(
            f"  t − t_m: p05 {anchor['lag_p05']:.3f} | p50 {anchor['lag_p50']:.3f} | "
            f"TB {anchor['lag_mean']:.3f} | p95 {anchor['lag_p95']:.3f} | "
            f"p99 {anchor['lag_p99']:.3f} | max {anchor['lag_max']:.3f} s"
        )
        print(
            f"  Kiểm răng cưa: TB dự đoán d + T/2 = "
            f"{anchor['d'] + anchor['t_poll']/2:.4f} (đo {anchor['lag_mean']:.4f}); "
            f"sd dự đoán T/√12 = {uniform_sd:.4f} "
            f"(đo {anchor['sd']:.4f}, ×{anchor['sd']/uniform_sd:.3f})"
        )
        for key in ("lag_p05", "lag_mean", "lag_p95"):
            z = anchor[key] + anchor["W"] / 2
            print(
                f"  {key[4:]:>4}: z = {z:.3f} s,  "
                f"z_eff = z + a + H/2 = {z + A_ACT + anchor['H']/2:.3f} s"
            )

    anchor = load_anchor("clean")
    z_eff = anchor["lag_mean"] + anchor["W"] / 2 + A_ACT + anchor["H"] / 2
    print(
        f"\n== Bảng Π tại điểm neo [clean], z_eff (TB) = {z_eff:.3f} s, "
        f"a = {A_ACT} s (giả định)"
    )
    print(f"{'tau':>5} | {'Π_age':>6} {'Π_hold':>6}")
    for tau in TAUS:
        print(f"{tau:5.1f} | {z_eff/tau:6.3f} {anchor['H']/tau:6.3f}")

    print(f"\n{'Mb/s':>5} {'S ms':>6} {'rho':>5} | {'T_relax s':>9} | Π_relax theo tau {TAUS}")
    for mbps in SPEEDS_MBPS:
        service = PKT_BYTES * 8 / (mbps * 1e6)
        for rho in RHO_BARS:
            relaxation = service / (1 - np.sqrt(rho)) ** 2
            ratios = " ".join(f"{relaxation/tau:7.3f}" for tau in TAUS)
            print(
                f"{mbps:5d} {service*1e3:6.3f} {rho:5.2f} | "
                f"{relaxation:9.3f} | {ratios}"
            )

    print("\n== Ba đại lượng chính xác (T2 §10.2), ρ̄ = 0,9; tuổi đo được p05 / p95")
    print(
        f"{'Mb/s':>5} {'sigma':>5} {'tau':>5} | {'R/V(W)':>7} "
        f"{'giải thích':>10} {'sd_p95/sd_p05':>13} | {'Π_noise':>7}"
    )
    for mbps in SPEEDS_MBPS:
        service = PKT_BYTES * 8 / (mbps * 1e6)
        noise_var = 0.9 * service / anchor["W"]
        for sigma in SIGMAS:
            for tau in TAUS:
                posterior_sds = []
                for lag in (anchor["lag_p05"], anchor["lag_p95"]):
                    _, var_post, _ = hold_posterior(
                        sigma, tau, anchor["W"], noise_var, lag + A_ACT, anchor["H"]
                    )
                    posterior_sds.append(np.sqrt(var_post))
                _, var_post_mean, var_prior = hold_posterior(
                    sigma,
                    tau,
                    anchor["W"],
                    noise_var,
                    anchor["lag_mean"] + A_ACT,
                    anchor["H"],
                )
                sd_age = sigma * np.sqrt(1 - np.exp(-2 * z_eff / tau))
                print(
                    f"{mbps:5d} {sigma:5.2f} {tau:5.1f} | "
                    f"{noise_var/v_avg(anchor['W'], sigma, tau):7.2f} "
                    f"{1-var_post_mean/var_prior:10.1%} "
                    f"{posterior_sds[1]/posterior_sds[0]:13.3f} | "
                    f"{np.sqrt(noise_var)/sd_age:7.2f}"
                )
