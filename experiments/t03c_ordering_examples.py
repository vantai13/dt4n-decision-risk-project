"""t03c (P1v2/L1.3) — Thông tin làm đổi thứ tự: ví dụ tay 6 epoch + năm thế giới đồ chơi.

Câu hỏi: khi nào ngưỡng tĩnh (đã tune) trên một thống kê điểm là tối ưu, và các chỉ số κ, rd_score có đo đúng
điều kiện đó không? Đây là KIỂM LÝ THUYẾT trên toy, không phải kết quả RQ, không đổi phán quyết F6.
Tái dùng k2_rule, gain, harm, headroom, static_best của t03 (cùng ε = 0,5; α = 1%; c = 0; N = 400.000).
Seed: 9101, 9102 (tái lập A, B của t03); 11901, 11902, 11903 (thế giới mới D, E, F — dải toy của v2).
Provenance: Claude (AI) soạn theo L1.3 của PHASE_1v2; tác giả chạy lại, kiểm và chịu trách nhiệm.
Chạy: python experiments/t03c_ordering_examples.py | tee experiments/results/t03c_ordering_examples_output.txt
"""
import itertools
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t03_k2_rule as t3

EPS, ALPHA, C, N = t3.EPS, t3.ALPHA, t3.C, t3.N

# ======================= PHẦN 1 — ví dụ tay 6 epoch =======================
# Mỗi epoch: (Ī, p−); ở đây Î = Ī (tâm đúng) để chỉ còn câu hỏi thứ tự. Î giảm dần e1 → e6.
# Ngân sách tính bằng TỔNG p− của các epoch được đổi (tương đương α·N với N = 6).
HAND_BUDGET = 0.25
HAND = {
    "H1 đơn điệu":       [(6, .02), (5, .04), (4, .06), (3, .10), (2, .15), (1, .25)],
    "H2 đảo xa biên":    [(6, .08), (5, .02), (4, .06), (3, .10), (2, .15), (1, .25)],
    "H3 cắt ngang biên": [(6, .02), (5, .04), (4, .20), (3, .10), (2, .03), (1, .25)],
}


def hand_static(v, p, budget):
    """Luật ngưỡng chỉ được chọn một TIỀN TỐ theo Î giảm dần: thử mọi tiền tố, giữ tiền tố khả thi gain lớn nhất."""
    best, n_best = 0.0, 0
    for n in range(1, len(v) + 1):
        if p[:n].sum() <= budget + 1e-12 and v[:n].sum() > best:
            best, n_best = float(v[:n].sum()), n
    return n_best, best


def hand_k2(v, p, budget):
    """λ nhỏ nhất đạt ngân sách (chia đôi), rồi đổi ⇔ u = Ī − λ·p− > 0 (hoà thì GIỮ, định nghĩa §4.3)."""
    harm_at = lambda lam: p[(v - lam * p) > 0].sum()
    lo, hi = 0.0, 1.0
    while harm_at(hi) > budget:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if harm_at(mid) <= budget else (mid, hi)
    act = (v - hi * p) > 0
    return hi, act, float(v[act].sum())


def hand_bruteforce(v, p, budget):
    """Tối ưu thật của bài toán 0/1 (duyệt 64 tập con): kiểm K2 không thua bất kỳ luật nào."""
    return max(float(v[list(sub)].sum()) for r in range(len(v) + 1)
               for sub in itertools.combinations(range(len(v)), r) if p[list(sub)].sum() <= budget + 1e-12)


def part1():
    print(f"PHẦN 1 — ví dụ tay 6 epoch, ngân sách Σp− ≤ {HAND_BUDGET}")
    for name, rows in HAND.items():
        v, p = np.array([r[0] for r in rows], float), np.array([r[1] for r in rows], float)
        n_s, g_s = hand_static(v, p, HAND_BUDGET)
        lam, act, g_k = hand_k2(v, p, HAND_BUDGET)
        u = v - lam * p
        chosen = ",".join(f"e{i + 1}" for i in np.flatnonzero(act))
        print(f"  {name:18s} | tĩnh: e1..e{n_s} gain {g_s:4.1f} | K2: λ* = {lam:5.2f}, chọn {{{chosen}}} gain {g_k:4.1f}"
              f" | tối ưu 0/1 {hand_bruteforce(v, p, HAND_BUDGET):4.1f} | gap {g_k - g_s:3.1f}"
              f" | Spearman(Î,u) {spearmanr(v, u).statistic:+.3f}")
        cells = [f"e{i + 1}: {'0 (hoà)' if abs(x) < 1e-9 else f'{x:+.2f}'}" for i, x in enumerate(u)]
        print(f"  {'':18s} | u = " + "   ".join(cells))
        print(f"  {'':18s} | Ī/p− = " + "   ".join(f"e{i + 1}: {a / b:.1f}" for i, (a, b) in enumerate(zip(v, p))))


# ======================= PHẦN 2 — năm thế giới liên tục =======================
def world(kind, seed):
    """Trả (Î, Ī, s) với I | F ~ N(Ī, s²). Î luôn ~ N(0,5; 2²) như t03."""
    rng = np.random.default_rng(seed)
    ihat = rng.normal(0.5, 2.0, N)
    if kind == "A":        # t03-A: độ rộng TRỰC GIAO (log s độc lập với tâm)
        return ihat, ihat, np.exp(rng.normal(0.0, 0.7, N))
    if kind == "B":        # t03-B: độ rộng CÙNG HƯỚNG, tăng chậm theo |Ī|
        return ihat, ihat, 0.3 + 0.5 * np.abs(ihat)
    if kind == "D":        # độ rộng cùng hướng nhưng tăng NHANH (∝ Ī²) → u không đơn điệu dù κ = 0
        return ihat, ihat, 0.3 + 0.25 * ihat**2
    if kind == "E":        # TÂM trực giao: Ī = Î + 0,8·Z; độ rộng là hàm của Ī (như B)
        ibar = ihat + 0.8 * rng.standard_normal(N)
        return ihat, ibar, 0.3 + 0.5 * np.abs(ibar)
    if kind == "F":        # cả hai: tâm trực giao + độ rộng trực giao
        ibar = ihat + 0.8 * rng.standard_normal(N)
        return ihat, ibar, np.exp(rng.normal(0.0, 0.7, N))
    raise ValueError(kind)


def threshold_best(key, ibar, p_minus, alpha, c=C):
    """Ngưỡng tốt nhất CHÍNH XÁC trên thống kê `key` (tiền tố theo key giảm dần, harm ≤ α·N, gain lớn nhất).
    Khi key = ibar thì trùng t03.static_best."""
    order = np.argsort(-key, kind="stable")
    n_max = int(np.searchsorted(np.cumsum(p_minus[order]), alpha * len(key) + 1e-9, side="right"))
    cum_gain = np.concatenate([[0.0], np.cumsum(ibar[order] - c)])[: n_max + 1]
    act = np.zeros(len(key), bool)
    act[order[: int(np.argmax(cum_gain))]] = True
    return act


def kappa(key, s, n_bin=20, detrend=False):
    """sd(log s) trong n_bin bin phân vị của `key`, trung bình có trọng số theo số epoch.
    detrend=False: đúng cách tính sd_log_s_cond của f02. detrend=True: trừ xu hướng tuyến tính của log s theo key
    TRONG mỗi bin trước khi lấy sd (bỏ 'sàn' do độ rộng bin)."""
    edges = np.quantile(key, np.linspace(0, 1, n_bin + 1))
    b = np.clip(np.searchsorted(edges, key, side="right") - 1, 0, n_bin - 1)
    log_s, groups = np.log(s), []
    for k in range(n_bin):
        m = b == k
        if m.sum() < (3 if detrend else 2):          # f02 bỏ bin có ≤ 1 epoch
            continue
        y = log_s[m]
        if detrend:
            x = np.vstack([np.ones(m.sum()), key[m]]).T
            y = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
        groups.append((y.std(), m.sum()))
    return float(np.average([g[0] for g in groups], weights=[g[1] for g in groups]))


def part2():
    print(f"\nPHẦN 2 — thế giới liên tục, N = {N}, ε = {EPS}, α = {ALPHA:.0%}, c = {C}  (gain: ms/epoch)")
    print(f"{'':3s} | {'S_Î':>6s} {'SC':>6s} {'K2':>6s} {'K2∞':>6s} {'head':>6s} | {'tâm':>7s} {'thuần':>7s} {'tổng':>7s}"
          f" | {'κ_Î':>5s} {'κ_Ī':>5s} {'κ_Ī,lin':>7s} | {'rd':>5s} {'K2≠SC':>6s} {'λ':>6s}")
    for kind, seed in (("A", 9101), ("B", 9102), ("D", 11901), ("E", 11902), ("F", 11903)):
        ihat, ibar, s = world(kind, seed)
        p_minus = norm.cdf((-EPS - ibar) / s)
        s_hat = threshold_best(ihat, ibar, p_minus, ALPHA)    # ngưỡng tĩnh trên thống kê điểm Î
        sc = threshold_best(ibar, ibar, p_minus, ALPHA)       # ngưỡng tĩnh trên tâm đúng Ī
        k2, lam = t3.k2_rule(ibar, p_minus, ALPHA)
        g = {k: t3.gain(a, ibar) for k, a in (("S", s_hat), ("SC", sc), ("K2", k2), ("INF", ibar > C))}
        for a in (s_hat, sc, k2):
            assert t3.harm(a, p_minus) <= ALPHA + 1e-9
        assert g["S"] <= g["K2"] + 1e-9 and g["SC"] <= g["K2"] + 1e-9   # K2 tối ưu trong MỌI luật khả thi
        if kind in ("A", "B"):                                             # đối chứng tái lập t03 (cùng seed)
            assert np.array_equal(sc, t3.static_best(ibar, p_minus, ALPHA))
        u, ec = ibar - lam * p_minus, ibar > C
        rd = 1.0 - spearmanr(ihat[ec], u[ec]).statistic                  # rd_score như f02 (trên tập cân nhắc)
        print(f"{kind:3s} | {g['S']:6.4f} {g['SC']:6.4f} {g['K2']:6.4f} {g['INF']:6.4f} {t3.headroom(ibar, s):6.4f} | "
              f"{g['SC'] - g['S']:+7.4f} {g['K2'] - g['SC']:+7.4f} {g['K2'] - g['S']:+7.4f} | "
              f"{kappa(ihat, s):5.3f} {kappa(ibar, s):5.3f} {kappa(ibar, s, detrend=True):7.3f} | "
              f"{rd:5.3f} {np.mean(k2 != sc):6.2%} {lam:6.2f}")


# ======================= PHẦN 3 — hình dạng u(Ī) và sàn của κ =======================
def part3():
    print("\nPHẦN 3 — hình dạng của u(Ī) = Ī − λ·p−(Ī) trên lưới Ī ∈ [0, 8], tại λ vận hành")
    x = np.linspace(0.0, 8.0, 8001)
    for kind, seed, s_fn in (("B", 9102, lambda i: 0.3 + 0.5 * i), ("D", 11901, lambda i: 0.3 + 0.25 * i**2)):
        ihat, ibar, s = world(kind, seed)
        lam = t3.k2_rule(ibar, norm.cdf((-EPS - ibar) / s), ALPHA)[1]
        pm = norm.cdf((-EPS - x) / s_fn(x))
        u = x - lam * pm
        edges = np.flatnonzero(np.diff((u > 0).astype(int)))
        print(f"  {kind}: λ = {lam:5.2f} | p− tăng ở {np.mean(np.diff(pm) > 0):6.1%} lưới | u giảm ở "
              f"{np.mean(np.diff(u) < 0):6.1%} lưới | u đổi dấu tại Ī ≈ " + ", ".join(f"{x[i]:.2f}" for i in edges))
    print("\n  Sàn của κ khi s là HÀM XÁC ĐỊNH của Ī (thế giới B, κ thật = 0):")
    ihat, ibar, s = world("B", 9102)
    for nb in (10, 20, 50, 100):
        print(f"    {nb:3d} bin: κ = {kappa(ibar, s, nb):.3f} | trừ xu hướng tuyến tính: {kappa(ibar, s, nb, True):.3f}")


if __name__ == "__main__":
    part1()
    part2()
    part3()
