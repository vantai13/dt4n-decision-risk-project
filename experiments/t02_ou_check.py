"""Kiểm công thức T2 bằng Monte Carlo; không phải thí nghiệm RQ1/RQ2.

Seed: 9201-9220 (C1), 9401-9420 / 9501-9520 / 9601-9620 (C2-C5).
"""

import numpy as np
from scipy import stats


MU, SIGMA = 0.9, 0.03
S = 1512 * 8 / 4e6
W, H, A_ACT, LAG = 0.5, 0.5, 0.05, 0.45
G = LAG + A_ACT
DT = 0.002
N_PATH, N_SEED = 20_000, 20
T975 = stats.t.ppf(0.975, N_SEED - 1)


def v_avg(length, sigma, tau):
    """Phương sai của trung bình OU trên một khoảng."""
    x = length / tau
    return sigma**2 if length == 0 else 2 * sigma**2 * (x - 1 + np.exp(-x)) / x**2


def a_avg(length, tau):
    """Trung bình của exp(-u/tau) trên [0, length]."""
    x = length / tau
    return 1.0 if length == 0 else (1 - np.exp(-x)) / x


def hold_posterior(mu, sigma, tau, window, noise_var, gap, hold):
    """Trả về beta, phương sai hậu nghiệm và phương sai tiên nghiệm của G."""
    cov = sigma**2 * np.exp(-gap / tau) * a_avg(window, tau) * a_avg(hold, tau)
    var_y = v_avg(window, sigma, tau) + noise_var
    var_prior = v_avg(hold, sigma, tau)
    return cov / var_y, var_prior - cov**2 / var_y, var_prior


def ou_paths(rng, n_path, n_steps, dt, mu, sigma, tau):
    """Sinh quỹ đạo OU bằng chuyển tiếp rời rạc chính xác."""
    memory = np.exp(-dt / tau)
    innovation = sigma * np.sqrt(1 - memory * memory)
    paths = np.empty((n_path, n_steps + 1))
    paths[:, 0] = mu + sigma * rng.standard_normal(n_path)
    for step in range(n_steps):
        paths[:, step + 1] = (
            mu + memory * (paths[:, step] - mu) + innovation * rng.standard_normal(n_path)
        )
    return paths


def trap_mean(segment):
    """Trung bình thời gian bằng quy tắc hình thang."""
    return (segment[:, 1:] + segment[:, :-1]).mean(axis=1) / 2


def confidence_interval(values):
    values = np.asarray(values)
    return values.mean(), T975 * values.std(ddof=1) / np.sqrt(len(values))


RESULTS = []
CONTROLS = []


def report(name, values, theory, negative_control=False):
    mean, half_width = confidence_interval(values)
    matches = abs(mean - theory) <= half_width
    (CONTROLS if negative_control else RESULTS).append(matches)
    tag = "khớp" if matches else "LỆCH"
    if negative_control:
        tag += "  <- đối chứng âm: phải LỆCH"
    print(f"  {name:38s} MC {mean:.4e} ± {half_width:.1e}   lý thuyết {theory:.4e}   {tag}")


if __name__ == "__main__":
    tau, delta = 2.0, 1.0
    print(f"C1  Một bước Delta = tau/2 từ phân phối dừng (tau = {tau} s)")
    for method in ("chính xác", "Euler"):
        variances, correlations = [], []
        for seed_offset in range(N_SEED):
            rng = np.random.default_rng(9201 + seed_offset)
            x0 = MU + SIGMA * rng.standard_normal(200_000)
            xi = rng.standard_normal(200_000)
            if method == "chính xác":
                memory = np.exp(-delta / tau)
                x1 = MU + memory * (x0 - MU) + SIGMA * np.sqrt(1 - memory * memory) * xi
            else:
                x1 = x0 + (delta / tau) * (MU - x0) + SIGMA * np.sqrt(2 * delta / tau) * xi
            variances.append(x1.var() / SIGMA**2)
            correlations.append(np.corrcoef(x0, x1)[0, 1])
        is_control = method == "Euler"
        report(f"[{method}] Var/sigma^2 (đúng = 1)", variances, 1.0, is_control)
        report(
            f"[{method}] tương quan (đúng = e^-0,5)",
            correlations,
            np.exp(-delta / tau),
            is_control,
        )

    n_window, n_gap, n_hold = round(W / DT), round(G / DT), round(H / DT)
    for tau, base_seed in ((0.5, 9401), (2.0, 9501), (10.0, 9601)):
        print(f"\nC2-C5  tau = {tau} s   (W = {W}, g = {G}, H = {H}, S = {S*1e3:.3f} ms)")
        noise_var = MU * S / W
        rows = {key: [] for key in ("point", "window", "noise", "post0", "post1")}
        for seed_offset in range(N_SEED):
            rng = np.random.default_rng(base_seed + seed_offset)
            paths = ou_paths(
                rng, N_PATH, n_window + n_gap + n_hold, DT, MU, SIGMA, tau
            )
            window = trap_mean(paths[:, : n_window + 1])
            hold = trap_mean(paths[:, n_window + n_gap :])
            count = rng.poisson(W * np.maximum(window, 0) / S)
            rho_hat = count * S / W
            memory_gap = np.exp(-G / tau)
            rows["point"].append(
                (paths[:, n_window + n_gap] - MU - memory_gap * (paths[:, n_window] - MU)).var()
            )
            rows["window"].append(window.var())
            rows["noise"].append((rho_hat - window).var())
            for key, observation, measurement_noise in (
                ("post0", window, 0.0),
                ("post1", rho_hat, noise_var),
            ):
                beta, _, _ = hold_posterior(
                    MU, SIGMA, tau, W, measurement_noise, G, H
                )
                rows[key].append((hold - MU - beta * (observation - MU)).var())
        report(
            "C2 Var(rho(t+g) | rho(t))",
            rows["point"],
            SIGMA**2 * (1 - np.exp(-2 * G / tau)),
        )
        report("C3 Var(trung bình cửa sổ)", rows["window"], v_avg(W, SIGMA, tau))
        report("C4 Var(nhiễu đếm)", rows["noise"], MU * S / W)
        report(
            "C5 Var(G | y), không nhiễu",
            rows["post0"],
            hold_posterior(MU, SIGMA, tau, W, 0.0, G, H)[1],
        )
        report(
            "C5 Var(G | y), có nhiễu",
            rows["post1"],
            hold_posterior(MU, SIGMA, tau, W, noise_var, G, H)[1],
        )

    n_bad = len(RESULTS) - sum(RESULTS)
    print(f"\nĐối chứng âm: {len(CONTROLS) - sum(CONTROLS)}/{len(CONTROLS)} LỆCH đúng như phải thế.")
    print(
        f"Công thức: {len(RESULTS)} phép kiểm, {n_bad} LỆCH. "
        f"Ở mức 95%, kỳ vọng khoảng {0.05*len(RESULTS):.1f} phép lệch do may rủi."
    )
    print("Dòng LỆCH -> chạy lại riêng dòng đó với seed mới và N lớn hơn TRƯỚC khi kết luận có lỗi.")
