"""f04_benchmark (F4, L1.7) — Engine DES có đúng và đủ nhanh cho lưới tầng 1 không?

Bốn phép đo: (1) engine Numba trùng từng bit với vòng lặp Python; (2) tốc độ (gói/giây);
(3) engine khớp nghiệm dừng mdk.py (CI 95% qua seed); (4) thời gian một cặp seed f04b → ước lượng CPU cho lưới.
Seed: 9731–9740 (pilot, còn trống). Thời gian đo phụ thuộc máy: chạy trên ĐÚNG máy chính, ĐÚNG Python sẽ dùng.
"""
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f02_existence_surrogate as f
import f04b_des_gap as g
from ndtrisk.theory.mdk import mdk

SEEDS = tuple(range(9731, 9741))


def workload_python(arrivals, service, full):
    """Cùng thuật toán với g.workload_after, viết bằng Python thuần để đối chiếu."""
    out = np.empty(len(arrivals))
    v, t_prev = 0.0, 0.0
    for i, t in enumerate(arrivals):
        v = max(0.0, v - (t - t_prev))
        t_prev = t
        if v <= full:
            v += service
        out[i] = v
    return out


def poisson_arrivals(rng, rho, n):
    return np.cumsum(rng.exponential(1.0 / rho, n))          # đơn vị S = 1


def loss_and_wait(arrivals, v_after, k):
    """Suy lại V ngay TRƯỚC mỗi gói đến từ V ngay SAU gói trước: không cần sửa engine."""
    gaps = np.diff(np.concatenate([[0.0], arrivals]))
    v_before = np.maximum(0.0, np.concatenate([[0.0], v_after[:-1]]) - gaps)
    accepted = v_before <= k - 1.0
    return 1.0 - accepted.mean(), v_before[accepted].mean()


if __name__ == "__main__":
    print(f"engine: {g.ENGINE} | Python {sys.version.split()[0]} | NumPy {np.__version__}")
    rng = np.random.default_rng(SEEDS[0])
    arr = poisson_arrivals(rng, 0.95, 300_000)
    g.workload_after(arr[:10], 1.0, 99.0)                     # lần gọi đầu: biên dịch JIT, không tính giờ
    same = np.array_equal(workload_python(arr, 1.0, 99.0), g.workload_after(arr, 1.0, 99.0))
    print(f"(1) Numba trùng từng bit với Python thuần trên 300.000 gói: {same}")

    t = time.perf_counter(); workload_python(arr, 1.0, 99.0); t_py = time.perf_counter() - t
    big = poisson_arrivals(rng, 0.95, 5_000_000)
    t = time.perf_counter(); g.workload_after(big, 1.0, 99.0); t_nb = time.perf_counter() - t
    print(f"(2) tốc độ: Python {len(arr)/t_py/1e6:.2f} triệu gói/s | engine {len(big)/t_nb/1e6:.1f} triệu gói/s "
          f"(nhanh hơn {len(big)/t_nb/(len(arr)/t_py):.0f}×)")

    t975 = stats.t.ppf(0.975, len(SEEDS) - 1)
    print("(3) khớp nghiệm dừng mdk.py (10 seed × 1.000.000 gói, đơn vị S):")
    for rho, k in ((0.8, 11), (0.95, 100), (1.0, 11)):
        samples = []
        for s in SEEDS:
            a = poisson_arrivals(np.random.default_rng(s), rho, 1_000_000)
            samples.append(loss_and_wait(a, g.workload_after(a, 1.0, k - 1.0), k))
        m, h = np.mean(samples, 0), t975 * np.std(samples, 0, ddof=1) / np.sqrt(len(SEEDS))
        ex = mdk(rho, k)
        ok_w = abs(m[1] - ex.wait) <= h[1]
        drops = ex.loss * 1_000_000 * len(SEEDS)
        loss_txt = (f"loss {m[0]:.5f}±{h[0]:.5f} vs {ex.loss:.5f} {'khớp' if abs(m[0]-ex.loss) <= h[0] else 'LỆCH'}"
                    if drops >= 100 else f"loss: không đủ sự kiện (~{drops:.0f} drop)")
        print(f"    ρ={rho:.2f} K={k:3d}: W_q {m[1]:.4f}±{h[1]:.4f} vs {ex.wait:.4f} "
              f"{'khớp' if ok_w else 'LỆCH'} | {loss_txt}")

    print("(4) thời gian một cặp seed f04b (2 path × 1500 epoch, gồm sinh tải, gói, hàng đợi, nhãn):")
    for name in ("P2", "P1"):
        cell, stream = g.CELLS[name]
        psa = f.PSA(cell.k)
        g.simulate_pair(cell, psa, SEEDS[0], stream)
        t = time.perf_counter()
        for s in SEEDS:
            g.simulate_pair(cell, psa, s, stream)
        per = (time.perf_counter() - t) / len(SEEDS)
        n_seed = len(f.CAL_SEEDS) + len(f.TEST_SEEDS) + len(f.ORACLE_SEEDS)
        print(f"    {name} (ρ̄={cell.rho_bar}): {per:.3f} s/cặp seed → một ô ({n_seed} seed) ≈ {per*n_seed:.0f} s mô phỏng; "
              f"16 ô ≈ {16*per*n_seed/3600:.2f} CPU-giờ (chưa gồm phần đánh giá)")
