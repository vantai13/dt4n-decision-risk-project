"""f04 (spike L1.7, phần 1) — Trên MỘT link DES thật: số đếm cửa sổ có phải "nhiễu" không, và PSA lệch DES bao nhiêu?

Câu hỏi: surrogate F2 giả định delay = PSA(cường độ tải) và số đếm = cường độ + nhiễu độc lập.
Trong DES, số đếm chính là số gói đã đổ vào hàng đợi, nên có thể mang thông tin về trạng thái hàng đợi V.
Cấu hình: P2 (4 Mb/s, K=100, rho_bar=0,95, sigma=0,10, tau=2 s), tuổi CLEAN cố định. Seed pilot 9721–9724.
Chỉ là spike định hướng (không phải e00, không phải RQ). R² tính NGOÀI MẪU: fit trên 2 seed, chấm trên 2 seed kia.
"""
import sys
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from f02_existence_surrogate import PSA, trap_w

S = 1512 * 8 / 4e6
K, RHO_BAR, SIGMA, TAU = 100, 0.95, 0.10, 2.0
W, LAG, ACT, HOLD, DT = 0.5, 0.37, 0.05, 0.5, 0.01
T_TOTAL, BURN_IN = 1500.0, 20.0
SEEDS = (9721, 9722, 9723, 9724)
N_PROBE = 251


def ou_path(rng, n):
    """OU rời rạc CHÍNH XÁC (T2 §2), khởi tạo dừng."""
    r = np.exp(-DT / TAU)
    x0 = SIGMA * rng.standard_normal()
    e = SIGMA * np.sqrt(1 - r * r) * rng.standard_normal(n - 1)
    x = np.concatenate([[x0], lfilter([1.0], [1.0, -r], e, zi=[r * x0])[0]])
    return np.clip(RHO_BAR + x, 0.0, None)


def run_seed(seed, psa):
    rng = np.random.default_rng(seed)
    n = int(T_TOTAL / DT)
    rho = ou_path(rng, n)
    t_grid = np.arange(n + 1) * DT
    cum_lam = np.concatenate([[0.0], np.cumsum(rho / S * DT)])
    u = np.cumsum(rng.exponential(1.0, int(cum_lam[-1] * 1.1) + 1000))
    arrivals = np.interp(u[u < cum_lam[-1]], cum_lam, t_grid)

    full = (K - 1) * S
    v_after = np.empty(len(arrivals))
    v, t_prev = 0.0, 0.0
    for i, t in enumerate(arrivals):
        v = max(0.0, v - (t - t_prev))
        t_prev = t
        if v <= full:
            v += S
        v_after[i] = v

    def workload_at(ts):
        j = np.searchsorted(arrivals, ts, side="right") - 1
        jj = np.maximum(j, 0)
        return np.where(j >= 0, np.maximum(v_after[jj] - (ts - arrivals[jj]), 0.0), 0.0)

    t_dec = np.arange(BURN_IN, T_TOTAL - 2.0, HOLD)
    t_m = t_dec - LAG
    count = np.searchsorted(arrivals, t_m) - np.searchsorted(arrivals, t_m - W)
    cum_rho = np.concatenate([[0.0], np.cumsum(rho * DT)])
    m_true = (np.interp(t_m, t_grid, cum_rho) - np.interp(t_m - W, t_grid, cum_rho)) / W

    s = (t_dec + ACT)[:, None] + np.linspace(0.0, HOLD, N_PROBE)[None, :]
    v_s = workload_at(s.ravel()).reshape(s.shape)
    accepted = v_s <= full
    n_acc = accepted.sum(1)
    d_des = np.where(n_acc > 0, np.where(accepted, v_s + S, 0.0).sum(1) / np.maximum(n_acc, 1), np.nan)

    idx = np.minimum((((t_dec + ACT)[:, None] + np.linspace(0, HOLD, 11)[None, :]) / DT).astype(int), n - 1)
    d_psa = psa.hold(rho[idx], trap_w(11))
    return dict(rho_hat=count * S / W, m_true=m_true, v_tm=workload_at(t_m) * 1e3,
                d_des=d_des * 1e3, d_psa=d_psa * S * 1e3)


def binned_mean_fit(x_fit, y_fit, n_bin=40):
    edges = np.unique(np.quantile(x_fit, np.linspace(0, 1, n_bin + 1)))
    b = np.clip(np.searchsorted(edges, x_fit, side="right") - 1, 0, len(edges) - 2)
    cnt = np.bincount(b, minlength=len(edges) - 1)
    means = np.bincount(b, y_fit, len(edges) - 1) / np.maximum(cnt, 1)
    means[cnt == 0] = y_fit.mean()
    return lambda x: means[np.clip(np.searchsorted(edges, x, side="right") - 1, 0, len(edges) - 2)]


def r2_out_of_sample(parts, xkey, ykey):
    """Fit E[y|x] bằng bin trên một nửa seed, chấm trên nửa kia, rồi đổi vai; trả về R² trung bình."""
    halves = (parts[:2], parts[2:])
    scores = []
    for fit, test in ((halves[0], halves[1]), (halves[1], halves[0])):
        xf, yf = (np.concatenate([p[k] for p in fit]) for k in (xkey, ykey))
        xt, yt = (np.concatenate([p[k] for p in test]) for k in (xkey, ykey))
        okf, okt = np.isfinite(yf), np.isfinite(yt)
        pred = binned_mean_fit(xf[okf], yf[okf])(xt[okt])
        scores.append(1 - np.mean((yt[okt] - pred) ** 2) / yt[okt].var())
    return float(np.mean(scores))


if __name__ == "__main__":
    psa = PSA(K)
    parts = [run_seed(s, psa) for s in SEEDS]
    for p in parts:
        p["count_resid"] = p["rho_hat"] - p["m_true"]
    cat = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
    ok = np.isfinite(cat["d_des"])
    print(f"Epoch: {ok.sum()} | delay DES TB {cat['d_des'][ok].mean():.1f} ms, sd {cat['d_des'][ok].std():.1f} ms")
    print("\n(1) Cái gì dự báo delay trong khoảng giữ (R² NGOÀI MẪU)?")
    for key, label in (("m_true", "cường độ tải thật m (trần của surrogate)"),
                       ("rho_hat", "số đếm ρ̂ (thứ twin thật sự thấy)"),
                       ("v_tm", "workload V lúc cuối cửa sổ (không có trong F)")):
        print(f"    R²(D_DES | {label:44s}) = {r2_out_of_sample(parts, key, 'd_des'):.3f}")
    print("\n(2) 'Nhiễu đếm' có tương quan với trạng thái hàng đợi không?")
    print(f"    corr(ρ̂ − m, V(t_m)) = {np.corrcoef(cat['count_resid'], cat['v_tm'])[0, 1]:+.3f}"
          "   (surrogate giả định = 0)")
    for p in parts:
        p["d_resid"] = p["d_des"] - binned_mean_fit(p["m_true"][np.isfinite(p["d_des"])],
                                                    p["d_des"][np.isfinite(p["d_des"])])(p["m_true"])
    cr = np.concatenate([p["count_resid"] for p in parts])
    dr = np.concatenate([p["d_resid"] for p in parts])
    okr = np.isfinite(dr)
    print(f"    corr(ρ̂ − m, D − E[D|m]) = {np.corrcoef(cr[okr], dr[okr])[0, 1]:+.3f}   (surrogate giả định = 0)")
    print("\n(3) PSA (surrogate) so với DES trên CÙNG quỹ đạo tải")
    d, q = cat["d_des"][ok], cat["d_psa"][ok]
    print(f"    TB: DES {d.mean():.1f} | PSA {q.mean():.1f} ms;  corr(DES, PSA) = {np.corrcoef(d, q)[0, 1]:.3f}")
    print(f"    R²(D | ρ̂) ngoài mẫu: DES {r2_out_of_sample(parts, 'rho_hat', 'd_des'):.3f} | "
          f"PSA {r2_out_of_sample(parts, 'rho_hat', 'd_psa'):.3f}")
    for lo, hi in ((0, 30), (30, 150), (150, 400)):
        sel = (q >= lo) & (q < hi)
        print(f"    PSA ∈ [{lo:3d},{hi:3d}) ms: n = {sel.sum():5d}, DES − PSA = {np.mean(d[sel] - q[sel]):+6.1f} ms")
