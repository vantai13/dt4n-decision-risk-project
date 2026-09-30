"""t09 (P1v2/L1.7) — HIỆU CHỈNH THIẾT KẾ cho F7b trong DES: chọn ρ̄_B để hai path CÙNG delay TB thật.

Vì sao cần: t08 khớp delay TB bằng mô hình dừng (PSA). f04 đã cho thấy PSA lệch DES hàng chục ms gần bão hoà,
nên "cùng delay TB" phải được khớp bằng chính DES (công cụ sẽ đo kết quả).
Vì sao KHÔNG vi phạm niêm phong F7: script chỉ đo TÍNH CHẤT CỦA TỪNG PATH RIÊNG LẺ (delay TB, p95, độ lệch của twin
plug-in). Không chạy luật nào, không quỹ đạo tham chiếu, không oracle, không κ, không gap.
Seed THIẾT KẾ 11801–11848 (ngoài mọi dải F7: 11001–11697). CRN: mọi mức ρ̄_B dùng cùng seed + cùng luồng ⇒ đường mượt.
Mức 0,931 của bản nháp (khớp PSA) được ĐO THẲNG, không ngoại suy.
Provenance: Claude (AI) soạn khi review L1.7; sửa 30/09 (đo thẳng 0,931); tác giả chạy lại, kiểm.
Chạy: python experiments/t09_des_mean_match.py | tee experiments/results/t09_des_mean_match_output.txt  (≈ 30 s)
"""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f02_existence_surrogate as f
import f04b_des_gap as fb

DESIGN_SEEDS = tuple(range(11801, 11849))
N_EP, STREAM_A, STREAM_B = 1500, 71, 72
A = (100, 0.85, 0.10, 2.0)
B_GRID = (0.908, 0.912, 0.916, 0.920, 0.924)
_psa = {}


def path_stats(k, rho_bar, sigma, tau, stream):
    """Delay TB theo seed (ms), p95 delay, TB twin plug-in T(ρ̂)·S."""
    cell = f.Cell("design", 4, k, rho_bar, sigma, tau)
    psa = _psa.setdefault(k, f.PSA(k))
    t_dec = fb.BURN_IN + cell.lag + cell.win + cell.hold * np.arange(N_EP)
    per_seed, d_all, plug_all = [], [], []
    for s in DESIGN_SEEDS:
        rng = np.random.default_rng(np.random.SeedSequence([s, stream]))
        rho_hat, d_des, _, n_full_epochs, _ = fb.one_path(rng, cell, psa, t_dec)
        per_seed.append(d_des.mean())
        d_all.append(d_des)
        plug_all.append(psa.point(rho_hat) * cell.s_ms)
    per_seed, d_all, plug_all = np.array(per_seed), np.concatenate(d_all), np.concatenate(plug_all)
    half = stats.t.ppf(0.975, len(per_seed) - 1) * per_seed.std(ddof=1) / np.sqrt(len(per_seed))
    return dict(mean=per_seed.mean(), half=half, p95=np.percentile(d_all, 95), plug=plug_all.mean())


if __name__ == "__main__":
    print(f"t09 — khớp delay TB trong DES; {len(DESIGN_SEEDS)} seed thiết kế × {N_EP} epoch; không luật, không κ, không gap")
    a = path_stats(*A, STREAM_A)
    print(f"A  K100/0,850/0,10/2  : E[D] = {a['mean']:6.2f} ± {a['half']:.2f} ms | p95 {a['p95']:6.1f} | "
          f"twin plug-in TB {a['plug']:6.2f} (lệch {a['plug'] - a['mean']:+6.2f})")
    means = []
    for rb in B_GRID:
        b = path_stats(100, rb, 0.03, 10.0, STREAM_B)
        means.append(b["mean"])
        print(f"B  K100/{rb:.3f}/0,03/10: E[D] = {b['mean']:6.2f} ± {b['half']:.2f} ms | p95 {b['p95']:6.1f} | "
              f"twin plug-in TB {b['plug']:6.2f} (lệch {b['plug'] - b['mean']:+6.2f})")
    assert np.all(np.diff(means) > 0), "delay TB phải tăng theo ρ̄_B (nếu không: lỗi hoặc quá ít seed)"
    star = float(np.interp(a["mean"], means, B_GRID))
    lo, hi = (float(np.interp(a["mean"] + d, means, B_GRID)) for d in (-a["half"], a["half"]))
    print(f"ρ̄_B khớp DES = {star:.4f} (khoảng theo CI của E[D_A]: {lo:.4f}–{hi:.4f}) → CHỐT 0,918 cho F7b")
    old = path_stats(100, 0.931, 0.03, 10.0, STREAM_B)
    print(f"Mức bản nháp 0,931 (khớp PSA), đo thẳng trong DES: E[D] = {old['mean']:.2f} ± {old['half']:.2f} ms "
          f"⇒ lệch A {old['mean'] - a['mean']:+.2f} ms")
