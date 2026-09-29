"""t05 (P1v2/L1.4) — Luật bậc hai: bất định trực giao phải lớn cỡ nào thì luật dùng độ rộng mới đáng?

Họ thế giới A của t03: Ī ~ N(0,5; 2²), s = s₀·e^η với s₀ = 1, η = κ·ξ, ξ ~ N(0, 1) độc lập với Ī; ε = 0,5; c = 0.
Luật tĩnh đặt ngưỡng trên TÂM ĐÚNG Ī (= SC), nên gap = K2 − SC là phần THUẦN của độ rộng.
Công thức kiểm: gap ≈ f₀·β²·κ²/(2a′), a′ = 1 + λφ(z₀)/s₀, β = λ·z₀·φ(z₀), z₀ = (−ε − t₀)/s₀, t₀: u(t₀, η = 0) = 0.
  "κ→0": hằng số tính tại λ của κ = 0 (như bảng đối chiếu của PHASE_1v2 L1.4).
  "λ(κ)": cùng công thức nhưng dùng λ thật ở κ đang xét (hiệu chỉnh đề xuất ở L1.4).
CRN: cùng seed → cùng Ī và cùng ξ ở mọi κ, nên đường gap theo κ là so sánh ghép cặp. Ở κ = 0,7, seed 9101 trùng t03-A.
Seed 9101–9110 (toy). KIỂM LÝ THUYẾT, không phải kết quả RQ.
Provenance: Claude (AI) soạn theo L1.4 của PHASE_1v2; tác giả chạy lại, kiểm và chịu trách nhiệm.
Chạy: python experiments/t05_orthogonal_kappa.py | tee experiments/results/t05_orthogonal_kappa_output.txt
"""
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm, t as student_t

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t03_k2_rule as t3

EPS, ALPHA, N = t3.EPS, t3.ALPHA, t3.N
MU, SD = 0.5, 2.0
KAPPAS = (0.0, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0, 1.25, 1.5, 2.0)
SEEDS = tuple(range(9101, 9111))
SENS_SEEDS = SEEDS[:5]                       # phần độ nhạy: 5 seed là đủ để thấy hình dạng


def run(kappa, seed, alpha=ALPHA, spread="median"):
    """Một seed: trả (gap K2 − SC, headroom, λ). spread='median' giữ trung vị s = 1 (đúng đặc tả t05);
    'mean' giữ trung bình s = 1 (mean-preserving spread: s = exp(κξ − κ²/2))."""
    rng = np.random.default_rng(seed)
    i_bar = rng.normal(MU, SD, N)
    eta = kappa * rng.standard_normal(N) - (kappa**2 / 2 if spread == "mean" else 0.0)
    s = np.exp(eta)
    p_minus = norm.cdf((-EPS - i_bar) / s)
    static = t3.static_best(i_bar, p_minus, alpha)      # ngưỡng tĩnh tốt nhất trên Ī (SC)
    adaptive, lam = t3.k2_rule(i_bar, p_minus, alpha)
    return t3.gain(adaptive, i_bar) - t3.gain(static, i_bar), t3.headroom(i_bar, s), lam


def ci(x):
    x = np.asarray(x, float)
    return float(x.mean()), float(student_t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))


def local_constants(lam, s0=1.0):
    """Hằng số tại ranh giới η = 0 cho một λ: (t₀, a′, β, f₀)."""
    t0 = brentq(lambda t: t - lam * norm.cdf((-EPS - t) / s0), 0.0, 20.0)
    z0 = (-EPS - t0) / s0
    return t0, 1.0 + lam * norm.pdf(z0) / s0, lam * z0 * norm.pdf(z0), norm.pdf(t0, MU, SD)


def formula(kappa, lam):
    t0, a1, beta, f0 = local_constants(lam)
    return f0 * beta**2 * kappa**2 / (2.0 * a1)


def lambda_population(alpha=ALPHA):
    """λ khi κ = 0 trên TỔNG THỂ: ngưỡng t₀ làm harm = α, rồi λ = t₀ / Φ(−ε − t₀) (vì u(t₀) = 0)."""
    harm = lambda t: quad(lambda x: norm.pdf(x, MU, SD) * norm.cdf(-EPS - x), t, np.inf)[0]
    t0 = brentq(lambda t: harm(t) - alpha, 0.0, 10.0)
    return t0 / norm.cdf(-EPS - t0)


def part1():
    lam0 = lambda_population()
    t0, a1, beta, f0 = local_constants(lam0)
    print(f"PHẦN 1 — họ thế giới A, α = {ALPHA:.0%}, {len(SEEDS)} seed {SEEDS[0]}–{SEEDS[-1]}, N = {N}")
    print(f"  Hằng số κ→0 (tổng thể): λ = {lam0:.3f} | t₀ = {t0:.3f} | a′ = {a1:.3f} | β = {beta:.3f} | f₀ = {f0:.3f}")
    print(f"  {'κ':>5s} | {'gap t05 (ms)':>16s} {'headroom':>9s} {'tỉ lệ':>7s} {'λ(κ)':>7s} | "
          f"{'CT κ→0':>7s} {'/t05':>6s} | {'CT λ(κ)':>7s} {'/t05':>6s}")
    table = {}
    for k in KAPPAS:
        runs = [run(k, sd) for sd in SEEDS]
        g, h, lam = (np.array(v) for v in zip(*runs))
        m, half = ci(g)
        table[k] = (m, h.mean(), lam.mean())
        f_0 = formula(k, lam0)
        f_k = formula(k, lam.mean()) if lam.mean() > 0 else 0.0
        r0 = f"{f_0 / m:6.3f}" if m > 0 else "     —"
        rk = f"{f_k / m:6.3f}" if m > 0 else "     —"
        print(f"  {k:5.2f} | {m:9.4f}±{half:.4f} {h.mean():9.4f} {m / h.mean():7.2%} {lam.mean():7.3f} | "
              f"{f_0:7.4f} {r0} | {f_k:7.4f} {rk}")
        if k == 0.0:
            assert np.all(g == 0.0), "Đối chứng κ = 0: độ rộng không đổi thì K2 phải trùng ngưỡng tĩnh"
        if k == 0.7:
            assert abs(runs[0][0] - 0.0952) <= 0.002, "κ = 0,7, seed 9101 phải tái lập t03-A"
        if 0 < k <= 0.2:
            assert abs(f_0 / m - 1) <= 0.15 and abs(f_k / m - 1) <= 0.15, "Công thức lệch > 15% ở κ ≤ 0,2"

    small = [k for k in KAPPAS if 0 < k <= 0.5]
    obs = np.polyfit(np.log(small), np.log([table[k][0] for k in small]), 1)[0]
    prd = np.polyfit(np.log(small), np.log([formula(k, table[k][2]) for k in small]), 1)[0]
    print(f"\n  Độ dốc log–log (κ ≤ 0,5): t05 = {obs:.2f} | công thức λ(κ) = {prd:.2f} | công thức κ→0 = 2,00 (theo cấu trúc)")

    share = np.array([table[k][0] / table[k][1] for k in KAPPAS])
    k_peak = KAPPAS[int(np.argmax(share))]
    print(f"  Tỉ lệ lớn nhất trên lưới: {share.max():.2%} tại κ = {k_peak}")
    for target in (0.05, 0.10, 0.20):
        idx = np.flatnonzero(share >= target)
        if idx.size == 0:
            print(f"  κ* cho {target:.0%} headroom: KHÔNG ĐẠT trong họ này (trần ≈ {share.max():.1%})")
            continue
        j = idx[0]
        k_lo, k_hi, s_lo, s_hi = KAPPAS[j - 1], KAPPAS[j], share[j - 1], share[j]
        slope = np.log(s_hi / s_lo) / np.log(k_hi / k_lo)             # nội suy tuyến tính trên log–log
        print(f"  κ* cho {target:.0%} headroom ≈ {k_lo * (target / s_lo) ** (1 / slope):.2f} "
              f"(nội suy log–log giữa κ = {k_lo} và {k_hi})")


def part2():
    print(f"\nPHẦN 2 — tăng κ mà giữ cái gì? (α = {ALPHA:.0%}, {len(SENS_SEEDS)} seed)")
    print(f"  {'κ':>5s} | {'giữ trung vị s: gap':>20s} {'headroom':>9s} {'tỉ lệ':>7s} | "
          f"{'giữ trung bình s: gap':>21s} {'headroom':>9s} {'tỉ lệ':>7s}")
    for k in KAPPAS[1:]:
        cols = []
        for spread in ("median", "mean"):
            g, h, _ = (np.array(v) for v in zip(*[run(k, sd, spread=spread) for sd in SENS_SEEDS]))
            cols.append((g.mean(), h.mean()))
        (g1, h1), (g2, h2) = cols
        print(f"  {k:5.2f} | {g1:20.4f} {h1:9.3f} {g1 / h1:7.2%} | {g2:21.4f} {h2:9.3f} {g2 / h2:7.2%}")


def part3(kappa=0.35):
    print(f"\nPHẦN 3 — ngân sách harm α là cái núm: κ = {kappa} cố định, {len(SENS_SEEDS)} seed")
    print(f"  {'α':>6s} | {'λ':>7s} {'β':>7s} {'a′':>6s} | {'gap t05':>8s} {'CT λ(α)':>8s} {'tỉ lệ':>7s}")
    for alpha in (0.002, 0.005, 0.01, 0.02, 0.05, 0.10):
        g, h, lam = (np.array(v) for v in zip(*[run(kappa, sd, alpha=alpha) for sd in SENS_SEEDS]))
        if lam.mean() > 0:
            _, a1, beta, _ = local_constants(lam.mean())
            pred = formula(kappa, lam.mean())
        else:
            a1, beta, pred = 1.0, 0.0, 0.0
            assert np.all(g == 0.0), "λ = 0 thì K2 ≡ ngưỡng tĩnh trên Ī: gap phải bằng 0 đúng"
        print(f"  {alpha:6.1%} | {lam.mean():7.3f} {beta:7.3f} {a1:6.2f} | {g.mean():8.4f} {pred:8.4f} "
              f"{g.mean() / h.mean():7.2%}")


if __name__ == "__main__":
    part1()
    part2()
    part3()
