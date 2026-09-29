"""t07 (P1v2/L1.5) — κ dự đoán cho lưới F7 (độ tươi bất đối xứng), tính rẻ bằng lý thuyết, KHÔNG DES.

Mỗi epoch lấy mẫu độc lập cho path hiện tại (cur) và path thay thế (alt):
  trung bình cửa sổ m_W ~ N(μ, V(W)); số đo y = đếm Poisson(m_W·W/S)·S/W (tắt nhiễu: y = m_W).
  cur đọc mỗi T_poll, đồng bộ → khe g_cur = lag + a. alt đọc mỗi T_probe, pha ngẫu nhiên → g_alt = lag + U[0, T_probe) + a.
  Biến thể "refresh": alt vừa là cur trước lần đổi gần nhất → tuổi thêm = min(U·T_probe, thời gian từ lần đổi),
  thời gian từ lần đổi ~ Exp(H/p_sw), p_sw = tỉ lệ đổi mỗi epoch của luật tĩnh trong F2 (surrogate, chỉ để ước lượng).
Hậu nghiệm từng path (T2 §6): G | y ~ N(m, V), m = μ + b(g)(y − μ), V = V(H) − c(g)²/(V(W) + R).
CÁCH CHÍNH — cầu phương Gauss–Hermite 40 nút: Ī = E[T(G_cur)] − E[T(G_alt)], s² = Var[T(G_cur)] + Var[T(G_alt)]
  (T: sojourn dừng M/D/1/K, ms; hai path độc lập). Tôn trọng độ cong và bão hoà của T.
SO SÁNH — delta method của plan: Î = T(m_cur) − T(m_alt), s² = T′(m_cur)²V_cur + T′(m_alt)²V_alt. Hỏng gần knee.
κ: sd(log s) trong 20 bin phân vị của tâm. raw = như sd_log_s_cond; lin = detrend tuyến tính trong bin (L1.3).
Tách kênh: κ(T_probe) − κ(đối chứng) = [κ − κ_tuổi TB] (phân tán tuổi, +) + [κ_tuổi TB − κ(đối chứng)] (sụp chiều, −).
Mô hình bỏ bộ nhớ hàng đợi (như PSA) ⇒ chỉ báo bậc độ lớn và CHIỀU. Không dự đoán tỉ lệ headroom (để tới L1.6).
Seed 11911 (dải toy v2, không giao F7). Provenance: Claude (AI) soạn theo L1.5; tác giả chạy lại, kiểm.
Chạy: python experiments/t07_kappa_pred.py | tee experiments/results/t07_kappa_pred_output.txt
"""
import json
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite_e import hermegauss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ndtrisk.theory.mdk import mdk

S = 1512 * 8 / 4e6                         # thời gian phục vụ (s); 3,024 ms ở 4 Mb/s
W, H, LAG, ACT, K_SYS = 0.5, 0.5, 0.37, 0.05, 100
N, SEED, N_BIN = 400_000, 11911, 20
CELLS = {   # tên: (ρ̄, σ, τ, p_sw, khoá ô trong f02_results.json)
    "P2 K100/0,95/0,10/2": (0.95, 0.10, 2.0, 0.0546, "K100_r0.95_s10t2"),
    "K100/0,85/0,10/2": (0.85, 0.10, 2.0, 0.0505, "K100_r0.85_s10t2"),
    "K100/0,95/0,03/10": (0.95, 0.03, 10.0, 0.0263, "K100_r0.95_s03t10"),
}
GRID = np.arange(0.0, 2.0005, 0.0005)
T_CURVE = np.array([mdk(float(r), K_SYS).sojourn for r in GRID]) * S * 1e3      # ms
T_SLOPE = np.gradient(T_CURVE, GRID)
NODES, WEIGHTS = hermegauss(40)
WEIGHTS = WEIGHTS / WEIGHTS.sum()


def v_avg(length, sigma, tau):
    x = length / tau
    return 2 * sigma**2 * (x - 1 + np.exp(-x)) / x**2


def a_avg(length, tau):
    x = length / tau
    return (1 - np.exp(-x)) / x


def posterior(y, gap, rho_bar, sigma, tau, noise):
    """(m, V) của tải trung bình khoảng giữ (T2 §6); gap = cuối cửa sổ đo → đầu khoảng giữ."""
    r_noise = rho_bar * S / W if noise else 0.0
    c = sigma**2 * a_avg(W, tau) * np.exp(-gap / tau) * a_avg(H, tau)
    denom = v_avg(W, sigma, tau) + r_noise
    return rho_bar + c / denom * (y - rho_bar), v_avg(H, sigma, tau) - c**2 / denom


def t_moments(m, v):
    """E[T(G)], Var[T(G)] với G ~ N(m, v), cầu phương Gauss–Hermite (xác suất học)."""
    g = np.clip(np.asarray(m)[:, None] + np.sqrt(np.broadcast_to(v, np.shape(m)))[:, None] * NODES[None, :], 0, GRID[-1])
    t = np.interp(g, GRID, T_CURVE)
    mean = t @ WEIGHTS
    return mean, np.maximum((t**2) @ WEIGHTS - mean**2, 1e-12)


def kappa(key, s, detrend, mask=None):
    if mask is not None:
        key, s = key[mask], s[mask]
    edges = np.quantile(key, np.linspace(0, 1, N_BIN + 1))
    b = np.clip(np.searchsorted(edges, key, side="right") - 1, 0, N_BIN - 1)
    log_s, groups = np.log(s), []
    for k in range(N_BIN):
        m = b == k
        if m.sum() < 3:
            continue
        y = log_s[m]
        if detrend:
            x = np.vstack([np.ones(m.sum()), key[m]]).T
            y = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
        groups.append((y.std(), m.sum()))
    return float(np.average([g[0] for g in groups], weights=[g[1] for g in groups]))


def measure(rng, rho_bar, sigma, tau, noise):
    m_w = rho_bar + np.sqrt(v_avg(W, sigma, tau)) * rng.standard_normal(N)
    return rng.poisson(np.maximum(m_w, 0) * W / S) * S / W if noise else m_w


def sample(cell, t_probe, noise=True):
    rho_bar, sigma, tau, p_sw, _ = CELLS[cell]
    rng = np.random.default_rng([SEED, list(CELLS).index(cell), int(round(t_probe * 100)), int(noise)])
    y_cur, y_alt = measure(rng, rho_bar, sigma, tau, noise), measure(rng, rho_bar, sigma, tau, noise)
    extra = t_probe * rng.random(N)
    since_switch = rng.exponential(H / p_sw, N)
    return y_cur, y_alt, extra, since_switch


def center_width(cell, y_cur, y_alt, extra, noise=True, delta=False):
    rho_bar, sigma, tau, _, _ = CELLS[cell]
    m_c, v_c = posterior(y_cur, LAG + ACT, rho_bar, sigma, tau, noise)
    m_a, v_a = posterior(y_alt, LAG + extra + ACT, rho_bar, sigma, tau, noise)
    if delta:
        m_c, m_a = np.clip(m_c, 0, GRID[-1]), np.clip(m_a, 0, GRID[-1])
        center = np.interp(m_c, GRID, T_CURVE) - np.interp(m_a, GRID, T_CURVE)
        return center, np.sqrt(np.interp(m_c, GRID, T_SLOPE) ** 2 * v_c + np.interp(m_a, GRID, T_SLOPE) ** 2 * v_a)
    (e_c, var_c), (e_a, var_a) = t_moments(m_c, v_c), t_moments(m_a, v_a)
    return e_c - e_a, np.sqrt(var_c + var_a)


def main_table():
    f02 = json.loads((ROOT / "experiments/results/f02/f02_results.json").read_text(encoding="utf-8"))
    print(f"t07 — κ dự đoán cho lưới F7 (N = {N}, seed {SEED}); z̄_alt tính từ TÂM cửa sổ (definitions §1)")
    print("BẢNG 1 — cầu phương (chính), nhiễu đếm bật, tuổi alt dừng U[0, T_probe)")
    print(f"{'ô':20s} {'T_probe':>7s} {'z̄_alt':>6s} | {'κ_raw':>6s} {'κ_lin':>6s} {'κ_lin(Ī>0)':>10s} | "
          f"{'Δ tổng':>7s} {'= phân tán':>10s} {'+ sụp chiều':>11s} | {'delta: κ_raw':>12s} {'s TB cầu phương/delta':>22s}")
    for cell, (rho_bar, sigma, tau, _, f02_key) in CELLS.items():
        k_control = None
        for t_probe in (0.5, tau, 4 * tau, np.inf):
            y_c, y_a, extra, _ = sample(cell, t_probe if np.isfinite(t_probe) else 0.5)
            if not np.isfinite(t_probe):
                extra = np.full(N, 1e6)                        # giới hạn: alt cũ vô hạn ⇒ hậu nghiệm = tiên nghiệm
            center, s = center_width(cell, y_c, y_a, extra)
            k_raw, k_lin, k_pos = kappa(center, s, False), kappa(center, s, True), kappa(center, s, True, center > 0)
            k_mean_age = kappa(*center_width(cell, y_c, y_a, np.full(N, extra.mean())), True)
            k_control = k_lin if k_control is None else k_control
            c_d, s_d = center_width(cell, y_c, y_a, extra, delta=True)
            label = "∞" if not np.isfinite(t_probe) else f"{t_probe:.1f}"
            z_bar = "∞" if not np.isfinite(t_probe) else f"{LAG + extra.mean() + W / 2:.2f}"
            print(f"{cell:20s} {label:>7s} {z_bar:>6s} | {k_raw:6.3f} {k_lin:6.3f} {k_pos:10.3f} | "
                  f"{k_lin - k_control:+7.3f} {k_lin - k_mean_age:+10.3f} {k_mean_age - k_control:+11.3f} | "
                  f"{kappa(c_d, s_d, False):12.3f} {np.mean(s):11.1f}/{np.mean(s_d):.1f}")
            if label == "0.5":
                ref = f02[f02_key]["0.0"]["sd_log_s_cond"][0]
                print(f"{'':20s} {'':7s} {'':6s}   ↳ đối chứng so F2 (sd_log_s_cond surrogate {ref:.3f}): "
                      f"cầu phương/F2 = {k_raw / ref:.2f} | delta/F2 = {kappa(c_d, s_d, False) / ref:.2f}")
                assert 0.5 <= k_raw / ref <= 2.0, "κ_pred đối chứng phải cùng bậc với F2 (validation L1.5)"
            if label == "∞":
                assert k_lin < 0.02, "giới hạn alt cũ vô hạn: bất định thành hàm của một biến ⇒ κ về sàn"


def sensitivity():
    print("\nBẢNG 2 — độ nhạy (κ_lin, cầu phương)")
    print(f"{'ô':20s} {'T_probe':>7s} | {'chính':>6s} {'refresh':>8s} {'tắt nhiễu':>9s}")
    for cell, (rho_bar, sigma, tau, _, _) in CELLS.items():
        for t_probe in (0.5, tau, 4 * tau):
            y_c, y_a, extra, since = sample(cell, t_probe)
            k_main = kappa(*center_width(cell, y_c, y_a, extra), True)
            k_ref = kappa(*center_width(cell, y_c, y_a, np.minimum(extra, since)), True)
            y_c0, y_a0, extra0, _ = sample(cell, t_probe, noise=False)
            k_off = kappa(*center_width(cell, y_c0, y_a0, extra0, noise=False), True)
            print(f"{cell:20s} {t_probe:7.1f} | {k_main:6.3f} {k_ref:8.3f} {k_off:9.3f}")


def information_curve():
    """κ theo lượng thông tin q của số đo (hai path cùng q, hậu nghiệm Gauss: m ~ N(μ, qV_G), V = (1 − q)V_G).
    q lấy từ t06: 1 cửa sổ, lịch sử 20 cửa sổ, và 1 cửa sổ tắt nhiễu đếm."""
    import t06_history_information as t6
    print("\nBẢNG 3 — κ_lin theo lượng thông tin q (đối chứng đối xứng; lịch sử và tắt nhiễu đều là 'tăng q')")
    print(f"{'ô':20s} | {'1 cửa sổ: q':>12s} {'κ':>6s} | {'20 cửa sổ: q':>13s} {'κ':>6s} | {'tắt nhiễu: q':>13s} {'κ':>6s}")
    for idx, (cell, (rho_bar, sigma, tau, _, _)) in enumerate(CELLS.items()):
        v_g = v_avg(H, sigma, tau)
        rng = np.random.default_rng([SEED, 99, idx])
        z_c, z_a = rng.standard_normal(N), rng.standard_normal(N)
        cols = []
        for q in (t6.r2(1, rho_bar, sigma, tau, t6.cov_closed), t6.r2(20, rho_bar, sigma, tau, t6.cov_closed),
                  t6.r2(1, 0.0, sigma, tau, t6.cov_closed)):      # ρ̄ = 0 trong r2 ⇔ R = 0 (tắt nhiễu)
            m_c, m_a = rho_bar + np.sqrt(q * v_g) * z_c, rho_bar + np.sqrt(q * v_g) * z_a
            (e_c, var_c), (e_a, var_a) = t_moments(m_c, (1 - q) * v_g), t_moments(m_a, (1 - q) * v_g)
            cols.append((q, kappa(e_c - e_a, np.sqrt(var_c + var_a), True)))
        print(f"{cell:20s} | " + " | ".join(f"{q:12.3f} {k:6.3f}" for q, k in cols))
        assert cols[1][1] >= cols[0][1] and cols[2][1] >= cols[0][1], "thêm thông tin phải không làm giảm κ ở đây"


if __name__ == "__main__":
    main_table()
    sensitivity()
    information_curve()
