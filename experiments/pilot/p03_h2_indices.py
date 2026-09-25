# ─── PROVENANCE (2026-09-25, Phase 0 v2 / L0.4) ──────────────────────────
# Tạo bởi : Claude (AI) theo yêu cầu tác giả, khi soạn L0.4; tác giả chạy lại và kiểm
# Sinh ra : experiments/pilot/results/p03_h2_indices_output.txt
# Trích ở : 06_definitions.md v2 (Phần 5), ADR K17 bổ sung
# Trạng thái: PILOT LÝ THUYẾT (exploratory) — KHÔNG phải bằng chứng RQ1/RQ2
# Seed    : 9101–9103 (dùng lại thế giới P02), 9104 (thế giới D, mới)
# Chạy lại: python experiments/pilot/p03_h2_indices.py
# ────────────────────────────────────────────────────────────────────────
"""P03 — PILOT LÝ THUYẾT (EXPLORATORY). Kiểm định nghĩa chỉ số H2 (K17) trước khi đưa vào 06_definitions.md.

Câu hỏi: chỉ số nào theo đúng khoảng cách ngưỡng tĩnh–oracle? Dùng lại thế giới A, B, C và luật của P02
(cùng seed 9101–9103), thêm thế giới D (seed 9104): bất định chỉ không đồng đều ở vùng không ai đổi.
KHÔNG phải bằng chứng RQ1/RQ2.
"""

import numpy as np
from scipy.stats import norm, spearmanr

from p02_objective_rules import EPS, KAPPA, N, fixed_common, odds_kkt


def world(kind, seed):
    rng = np.random.default_rng(seed)
    if kind == "A_rang_buoc_can":
        i_hat = rng.normal(0.5, 2.0, N)
        s = np.exp(rng.normal(0.0, 0.7, N))
    elif kind == "B_bat_dinh_ti_le":
        i_hat = rng.normal(0.5, 2.0, N)
        s = 0.3 + 0.5 * np.abs(i_hat)
    elif kind == "C_mang_ranh":
        i_hat = rng.normal(0.0, 0.3, N)
        s = np.full(N, 0.05)
    else:
        i_hat = rng.normal(0.5, 2.0, N)
        s = np.where(i_hat > -2.0, 1.0, np.exp(rng.normal(0.0, 0.7, N)))
    return i_hat, s, norm.sf((EPS - i_hat) / s), norm.cdf((-EPS - i_hat) / s)


def indices(i_hat, s, p_up, p_dn, m_mc=10_000, bins=20):
    floor = 1.0 / (m_mc + 1)
    log_odds = np.log(np.clip(p_up, floor, 1)) - np.log(np.clip(p_dn, floor, 1))
    log_s = np.log(s)
    edges = np.quantile(i_hat, np.linspace(0, 1, bins + 1))
    b = np.clip(np.searchsorted(edges, i_hat, side="right") - 1, 0, bins - 1)
    cond = sum(np.sum(b == k) * np.std(log_s[b == k]) for k in range(bins)) / len(i_hat)
    keep = p_up > KAPPA
    rd_all = 1 - spearmanr(i_hat, log_odds)[0]
    rd_kappa = 1 - spearmanr(i_hat[keep], log_odds[keep])[0] if keep.sum() > 2 else 0.0
    return np.std(log_s), cond, rd_all, rd_kappa


if __name__ == "__main__":
    print(f"{'thế giới':18s} {'gap điểm %':>10s} {'sd_log_s':>9s} {'sd_cond':>8s} {'rd_all':>8s} {'rd_kappa':>9s}")
    for kind, seed in (
        ("A_rang_buoc_can", 9101),
        ("B_bat_dinh_ti_le", 9102),
        ("C_mang_ranh", 9103),
        ("D_chi_vung_giu", 9104),
    ):
        i_hat, s, p_up, p_dn = world(kind, seed)
        sw_fix = fixed_common(i_hat, p_up, p_dn, KAPPA)
        sw_orc, _ = odds_kkt(p_up, p_dn, KAPPA)
        j = lambda sw: np.mean(p_up * ~sw) + KAPPA * sw.mean()
        gap = 100 * (j(sw_fix) - j(sw_orc))
        sd, cond, rd_all, rd_k = indices(i_hat, s, p_up, p_dn)
        print(f"{kind:18s} {gap:10.3f} {sd:9.3f} {cond:8.3f} {rd_all:8.4f} {rd_k:9.4f}")
