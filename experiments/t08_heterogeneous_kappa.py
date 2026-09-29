"""t08 (P1v2/L1.7) — κ dự đoán cho hai path KHÁC LOẠI (câu hỏi 2 của F6), để GVHD chọn spike ở mốc 13/10. KHÔNG DES.

Hai path độc lập, tham số khác nhau; path hiện tại là A hoặc B với xác suất 1/2; cả hai đọc đồng bộ (như f04b A0).
Hậu nghiệm và cầu phương dùng lại t07 (T5 §1, §3), mỗi path dùng đường sojourn M/D/1/K của chính K của nó.
  κ_chung  : bin theo Ī gộp cả hai chiều — thước đo so với MỘT ngưỡng chung.
  κ_theo_chiều: κ tính riêng trong từng chiều (cur = A, cur = B), trung bình có trọng số — so với ngưỡng THEO CHIỀU.
  κ_chung ≫ κ_theo_chiều ⇔ danh tính path là Z trực giao chính, và họ tĩnh theo chiều hấp thụ được nó (T5 §5).
Hai loại cặp: (a) delay TB khác xa ⇒ Ī tách theo chiều; (b) delay TB KHỚP (ρ̄ của path ổn định giải bằng brentq trên
E[T] của mô hình này, ghi cố định 0,9309 và 0,9793) nhưng khác độ biến động ⇒ đúng kịch bản "khác nhau về rủi ro" của F6.
Đối chứng: hai path giống hệt nhau ⇒ κ_chung ≈ κ_theo_chiều. Seed 11921 (dải toy v2).
Provenance: Claude (AI) soạn cho L1.7; tác giả chạy lại, kiểm.
Chạy: python experiments/t08_heterogeneous_kappa.py | tee experiments/results/t08_heterogeneous_kappa_output.txt
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t07_kappa_pred as t7
from ndtrisk.theory.mdk import mdk

N, SEED = 400_000, 11921
CURVES = {k: np.array([mdk(float(r), k).sojourn for r in t7.GRID]) * t7.S * 1e3 for k in (11, 100)}
PATHS = {   # tên: (K, ρ̄, σ, τ)
    "K100/0,95/0,10/2": (100, 0.95, 0.10, 2.0),
    "K100/0,85/0,03/10": (100, 0.85, 0.03, 10.0),
    "K11/0,85/0,03/10": (11, 0.85, 0.03, 10.0),
    "K11/0,95/0,10/2": (11, 0.95, 0.10, 2.0),
    "K100/0,931/0,03/10": (100, 0.9309, 0.03, 10.0),     # E[T] khớp K100/0,85/0,10/2 (30,6 ms), ổn định hơn
    "K100/0,85/0,10/2": (100, 0.85, 0.10, 2.0),
    "K100/0,979/0,03/10": (100, 0.9793, 0.03, 10.0),     # E[T] khớp K100/0,95/0,10/2 (98,9 ms), ổn định hơn
}
PAIRS = [("K100/0,95/0,10/2", "K100/0,95/0,10/2"),       # đối chứng: giống hệt
         ("K100/0,95/0,10/2", "K100/0,85/0,03/10"),      # cùng buffer, khác tải/độ biến động
         ("K100/0,95/0,10/2", "K11/0,95/0,10/2"),        # cùng tải, khác buffer
         ("K100/0,95/0,10/2", "K11/0,85/0,03/10"),       # khác mọi thứ
         ("K100/0,85/0,10/2", "K100/0,931/0,03/10"),     # CÙNG delay TB, khác rủi ro (đúng kịch bản F6 câu 2)
         ("K100/0,95/0,10/2", "K100/0,979/0,03/10")]     # CÙNG delay TB, khác rủi ro, sát knee


def path_moments(rng, name):
    k, rho_bar, sigma, tau = PATHS[name]
    y = t7.measure(rng, rho_bar, sigma, tau, True)
    m, v = t7.posterior(y, t7.LAG + t7.ACT, rho_bar, sigma, tau, True)
    g = np.clip(m[:, None] + np.sqrt(v) * t7.NODES[None, :], 0, t7.GRID[-1])
    t = np.interp(g, t7.GRID, CURVES[k])
    mean = t @ t7.WEIGHTS
    return mean, np.maximum((t**2) @ t7.WEIGHTS - mean**2, 1e-12)


if __name__ == "__main__":
    print(f"t08 — κ_lin (bin theo Ī, detrend) cho hai path khác loại; N = {N}, seed {SEED}")
    print(f"{'path A':18s} {'path B':18s} | {'κ_chung':>8s} {'κ_theo_chiều':>12s} {'chênh':>7s} | {'TB Ī khi cur=A':>14s} {'cur=B':>8s}")
    for i, (a, b) in enumerate(PAIRS):
        rng = np.random.default_rng([SEED, i])
        (ea, va), (eb, vb) = path_moments(rng, a), path_moments(rng, b)
        cur_a = rng.random(N) < 0.5
        ibar = np.where(cur_a, ea - eb, eb - ea)
        s = np.sqrt(va + vb)
        k_all = t7.kappa(ibar, s, True)
        k_dir = (cur_a.mean() * t7.kappa(ibar[cur_a], s[cur_a], True)
                 + (~cur_a).mean() * t7.kappa(ibar[~cur_a], s[~cur_a], True))
        print(f"{a:18s} {b:18s} | {k_all:8.3f} {k_dir:12.3f} {k_all - k_dir:+7.3f} | "
              f"{ibar[cur_a].mean():+11.1f} ms {ibar[~cur_a].mean():+8.1f}")
        if a == b:
            assert abs(k_all - k_dir) < 0.02, "đối chứng hai path giống hệt: chung ≈ theo chiều"
