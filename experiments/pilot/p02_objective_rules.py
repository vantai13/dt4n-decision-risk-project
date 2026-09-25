# ─── PROVENANCE (2026-09-25, Phase 0 v2 / L0.3) ──────────────────────────
# Tạo bởi : Claude (AI) theo yêu cầu tác giả, khi soạn L0.3; tác giả chạy lại và kiểm
# Sinh ra : experiments/pilot/results/p02_objective_rules_output.txt
# Trích ở : ADR K2, K21; memo notes/meetings/2026-09-25_objective_memo.md
# Trạng thái: PILOT LÝ THUYẾT (exploratory) — KHÔNG phải bằng chứng RQ1/RQ2
# Seed    : 9101, 9102, 9103 (chỉ dùng cho pilot này)
# Chạy lại: python experiments/pilot/p02_objective_rules.py
# ───────────────────────────────────────────────────────────────────────
"""P02 — PILOT LÝ THUYẾT (EXPLORATORY). Kiểm các khẳng định của L0.3; KHÔNG phải bằng chứng RQ1/RQ2.

Thế giới đồ chơi "oracle": mỗi epoch, I | F ~ N(Î, s²) với Î, s đã biết, nên p+ = P(I > ε | F) và
p− = P(I < −ε | F) tính chính xác. Mọi tỉ lệ là KỲ VỌNG chia cho MỌI epoch (không có nhiễu lấy mẫu nhãn).
Seed 9101–9103: chỉ dùng cho pilot này.
"""

import numpy as np
from scipy.stats import norm

EPS, ALPHA, KAPPA, N = 0.5, 0.01, 0.01, 400_000


def world(kind, seed):
    rng = np.random.default_rng(seed)
    if kind == "A_rang_buoc_can":
        i_hat = rng.normal(0.5, 2.0, N)
        s = np.exp(rng.normal(0.0, 0.7, N))
    elif kind == "B_bat_dinh_ti_le":
        i_hat = rng.normal(0.5, 2.0, N)
        s = 0.3 + 0.5 * np.abs(i_hat)
    else:
        i_hat = rng.normal(0.0, 0.3, N)
        s = np.full(N, 0.05)
    return i_hat, norm.sf((EPS - i_hat) / s), norm.cdf((-EPS - i_hat) / s)


def stats(sw, i_hat, p_up, p_dn):
    return (
        np.mean(p_dn * sw),
        np.mean(p_up * ~sw),
        sw.mean(),
        i_hat[sw].sum() / N,
        np.mean(sw & (p_up < 0.05)),
    )


def fill_budget(score, p_dn):
    """Bẫy 1: đổi theo score tới khi tiêu hết ngân sách alpha*N."""
    order = np.argsort(-score, kind="stable")
    sw = np.zeros(N, bool)
    sw[order[np.cumsum(p_dn[order]) <= ALPHA * N]] = True
    return sw


def fixed_common(i_hat, p_up, p_dn, kappa):
    """Ngưỡng tĩnh H theo min missed + kappa*switch, harm <= alpha."""
    best, best_sw = np.inf, np.zeros(N, bool)
    for h in np.quantile(i_hat, np.linspace(0, 1, 801)):
        sw = i_hat > h
        harm, missed, rate = np.mean(p_dn * sw), np.mean(p_up * ~sw), sw.mean()
        if harm <= ALPHA and missed + kappa * rate < best:
            best, best_sw = missed + kappa * rate, sw
    return best_sw


def odds_kkt(p_up, p_dn, kappa):
    """Doi iff p+ - lambda*p- > kappa, lambda >= 0 nho nhat de harm <= alpha."""
    harm = lambda lam: np.mean(p_dn * ((p_up - lam * p_dn) > kappa))
    if harm(0.0) <= ALPHA:
        return p_up > kappa, 0.0
    lo, hi = 0.0, 1e6
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if harm(mid) <= ALPHA else (mid, hi)
    return (p_up - hi * p_dn) > kappa, hi


def precision(p_up, p_dn):
    """Mục tiêu (c): sum_switch (p- - alpha) <= 0."""
    w = p_dn - ALPHA
    sw = w <= 0
    risky = np.flatnonzero(~sw)
    order = risky[np.argsort(-(p_up[risky] / w[risky]))]
    sw[order[np.cumsum(w[order]) <= -w[sw].sum()]] = True
    return sw


if __name__ == "__main__":
    print(f"ε = {EPS} ms, α = {ALPHA:.0%} (trên mọi epoch), κ = {KAPPA}, N = {N}")
    for kind, seed in (
        ("A_rang_buoc_can", 9101),
        ("B_bat_dinh_ti_le", 9102),
        ("C_mang_ranh", 9103),
    ):
        i_hat, p_up, p_dn = world(kind, seed)
        lo = np.log(p_up + 1e-300) - np.log(p_dn + 1e-300)
        sw_k0, lam0 = odds_kkt(p_up, p_dn, 0.0)
        sw_k1, lam1 = odds_kkt(p_up, p_dn, KAPPA)
        rules = [
            ("(a) E[I|F] > 0", i_hat > 0),
            ("(b) tĩnh H, tiêu chí chung", fixed_common(i_hat, p_up, p_dn, KAPPA)),
            ("(b) odds, tiêu hết ngân sách", fill_budget(lo, p_dn)),
            (f"(b) odds, KKT, κ=0 (λ={lam0:.2f})", sw_k0),
            (f"(b) odds, KKT, κ={KAPPA} (λ={lam1:.2f})", sw_k1),
            ("(c) precision", precision(p_up, p_dn)),
        ]
        print(f"\n== {kind}")
        print(f"{'luật':34s} {'harm':>7s} {'missed':>8s} {'đổi':>7s} {'lợi ms':>7s} {'vô ích':>7s}")
        for name, sw in rules:
            h, m, r, g, u = stats(sw, i_hat, p_up, p_dn)
            print(f"{name:34s} {h:7.3%} {m:8.3%} {r:7.2%} {g:7.4f} {u:7.2%}")
