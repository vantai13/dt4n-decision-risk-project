"""t10 (P1v2/L1.7, phục vụ L1.11) — TOY định hướng Phase 2, mô hình t07/t08, KHÔNG DES, KHÔNG phải bằng chứng.

Luật bậc hai: gap_thuần ≈ f₀·β²·κ²/(2a′). β do MỤC TIÊU + NGÂN SÁCH HARM quyết định; κ do THÔNG TIN × độ cong quyết định.
  Bảng 1 (trục mục tiêu): phần thuần của độ rộng dưới (i) mục tiêu hiện tại (TB, harm ≤ α = 1%, ε = 1,5 ms) và
          (ii) mục tiêu SLO min P(D_chọn > d). Tĩnh cho phép ngưỡng theo chiều. Tính theo kỳ vọng hậu nghiệm.
  Bảng 2 (trục thông tin × α): share thuần = (K2 − SC)/E[I⁺] khi bật/tắt nhiễu đếm và α ∈ {2; 1; 0,5; 0,2}%.
Giới hạn: không có quỹ đạo tham chiếu ⇒ f₀ lạc quan. Đối chiếu ở K100/0,85, α = 1%: DES (f05c) 1,80% so với toy ≈ 2,1%
(cùng mẫu số E[I⁺]). Chỉ đọc CHIỀU và bậc độ lớn. Mọi share ở đây chia cho headroom của CHÍNH mục tiêu đó.
CẢNH BÁO OFAT (chốt 30/09): Bảng 1 so "TB + harm α" với "SLO KHÔNG có ngân sách harm" — đổi HAI thứ cùng lúc.
Kết luận về trục mục tiêu chỉ đúng cho SLO không ràng buộc; kiểm SLO có ràng buộc ở Phase 2 trước khi dùng cho DP0.
Seed 11931–11932 (dải toy v2). Provenance: Claude (AI) soạn khi review L1.7; tác giả chạy lại, kiểm.
Chạy: python experiments/t10_objective_information.py | tee experiments/results/t10_objective_information_output.txt
"""
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t07_kappa_pred as t7
import t08_heterogeneous_kappa as t8

N, ALPHA = 200_000, 0.01
EPS = 0.5 * t7.S * 1e3
CURVE, GRID, NODES, WTS = t8.CURVES[100], t7.GRID, t7.NODES, t7.WEIGHTS


def T(g):
    return np.interp(np.clip(g, 0, GRID[-1]), GRID, CURVE)


def T_inv(x):
    return np.interp(x, CURVE, GRID)


def posterior(rng, rho_bar, sigma, tau, noise=True):
    y = t7.measure(rng, rho_bar, sigma, tau, noise)[:N]
    m, v = t7.posterior(y, t7.LAG + t7.ACT, rho_bar, sigma, tau, noise)
    return m, np.full(N, v)


def moments(m, v):
    t = T(m[:, None] + np.sqrt(v)[:, None] * NODES[None, :])
    mu = t @ WTS
    return mu, np.maximum((t * t) @ WTS - mu * mu, 1e-12)


def p_minus(mc, vc, ma, va):
    """P(T(G_cur) − T(G_alt) < −ε | F), chính xác bằng cầu phương theo G_alt (hai path độc lập)."""
    t_alt = T(ma[:, None] + np.sqrt(va)[:, None] * NODES[None, :])
    p = norm.cdf((T_inv(np.maximum(t_alt - EPS, CURVE[0])) - mc[:, None]) / np.sqrt(vc)[:, None])
    return np.where(t_alt - EPS <= CURVE[0], 0.0, p) @ WTS


def k2_total(ibar, pm, budget):
    """Tổng gain của luật K2 (u = Ī − λp− > 0) với λ nhỏ nhất đạt Σp− ≤ budget."""
    if np.sum((ibar > 0) * pm) <= budget:
        return np.sum(np.maximum(ibar, 0))
    lo, hi = 0.0, 1.0
    while np.sum(((ibar - hi * pm) > 0) * pm) > budget:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if np.sum(((ibar - mid * pm) > 0) * pm) <= budget else (mid, hi)
    return np.sum(((ibar - hi * pm) > 0) * ibar)


def static_dir_total(score, gain, harm, dirs, budget):
    """Tĩnh THEO CHIỀU tốt nhất: mỗi chiều chọn một tập mức trên của score; tối đa Σgain với Σharm ≤ budget."""
    curves = []
    for d in (0, 1):
        idx = np.where(dirs == d)[0]
        o = idx[np.argsort(-score[idx])]
        curves.append((np.concatenate([[0], np.cumsum(gain[o])]), np.concatenate([[0], np.cumsum(harm[o])])) )
    (g0, h0), (g1, h1) = curves
    best = -np.inf
    for k0 in np.unique(np.linspace(0, len(g0) - 1, 800).astype(int)):
        if h0[k0] > budget:
            break
        k1 = np.searchsorted(h1, budget - h0[k0], side="right") - 1
        best = max(best, g0[k0] + np.max(g1[:k1 + 1]))
    return best


def objective_axis(label, path_a, path_b, tag):
    rng = np.random.default_rng([11931, tag])
    (m_a, v_a), (m_b, v_b) = posterior(rng, *path_a), posterior(rng, *path_b)
    cur_a = rng.random(N) < 0.5
    mc, vc = np.where(cur_a, m_a, m_b), np.where(cur_a, v_a, v_b)
    ma, va = np.where(cur_a, m_b, m_a), np.where(cur_a, v_b, v_a)
    ibar = moments(mc, vc)[0] - moments(ma, va)[0]
    pm, dirs = p_minus(mc, vc, ma, va), (~cur_a).astype(int)
    I_real = T(mc + np.sqrt(vc) * rng.standard_normal(N)) - T(ma + np.sqrt(va) * rng.standard_normal(N))
    head_mean = np.sum(np.maximum(I_real, 0))
    pure_mean = k2_total(ibar, pm, ALPHA * N) - static_dir_total(ibar, ibar, pm, dirs, ALPHA * N)
    cols = [f"TB+harm: {100 * pure_mean / head_mean:5.2f}%"]
    for d in (50.0, 100.0, 150.0):
        pc = 1 - norm.cdf((T_inv(d) - mc) / np.sqrt(vc))
        pa = 1 - norm.cdf((T_inv(d) - ma) / np.sqrt(va))
        gain_slo = pc - pa
        head = np.sum(pc * (1 - pa))
        pure = np.sum(np.maximum(gain_slo, 0)) - static_dir_total(ibar, gain_slo, np.zeros(N), dirs, 1.0)
        cols.append(f"SLO {d:.0f} ms: {100 * pure / head:5.2f}%")
    print(f"{label:9s} | " + " | ".join(cols))


def information_alpha(label, rho_bar, sigma, tau, noise):
    rng = np.random.default_rng([11932, int(rho_bar * 1000), int(noise)])
    (mc, vc), (ma, va) = posterior(rng, rho_bar, sigma, tau, noise), posterior(rng, rho_bar, sigma, tau, noise)
    (ec, xc), (ea, xa) = moments(mc, vc), moments(ma, va)
    ibar, pm = ec - ea, p_minus(mc, vc, ma, va)
    I_real = T(mc + np.sqrt(vc) * rng.standard_normal(N)) - T(ma + np.sqrt(va) * rng.standard_normal(N))
    head = np.mean(np.maximum(I_real, 0))
    kap = t7.kappa(ibar, np.sqrt(xc + xa), True)
    cols = []
    for alpha in (0.02, 0.01, 0.005, 0.002):
        order = np.argsort(-ibar)
        feasible = (np.cumsum(pm[order]) <= alpha * N) & (ibar[order] > 0)
        n_sel = int(np.argmin(feasible)) if not feasible.all() else N
        pure = (k2_total(ibar, pm, alpha * N) - ibar[order][:n_sel].sum()) / N
        cols.append(f"α {100 * alpha:.1f}%: {100 * pure / head:5.2f}% ({pure:.3f} ms)")
    print(f"{label:30s} κ {kap:.3f} | " + " | ".join(cols))


if __name__ == "__main__":
    print("t10 — TOY định hướng (không DES). Bảng 1: phần thuần của độ rộng theo mục tiêu (% headroom tương ứng)")
    objective_axis("AA", (0.85, 0.10, 2.0), (0.85, 0.10, 2.0), 1)
    objective_axis("AB", (0.85, 0.10, 2.0), (0.918, 0.03, 10.0), 2)
    objective_axis("P2", (0.95, 0.10, 2.0), (0.95, 0.10, 2.0), 3)
    print("\nBảng 2: share thuần (K2 − SC)/E[I⁺] theo nhiễu đếm × ngân sách harm α (đối xứng)")
    information_alpha("K100/0,85/0,10/2 nhiễu bật", 0.85, 0.10, 2.0, True)
    information_alpha("K100/0,85/0,10/2 tắt nhiễu", 0.85, 0.10, 2.0, False)
    information_alpha("K100/0,95/0,03/10 nhiễu bật", 0.95, 0.03, 10.0, True)
    information_alpha("K100/0,95/0,03/10 tắt nhiễu", 0.95, 0.03, 10.0, False)
