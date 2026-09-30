"""t08b (P1v2/L1.7) — Kiểm lại t08 bằng THẾ GIỚI CHA đối xứng (OFAT đúng). Lý thuyết, KHÔNG DES.

Vì sao cần: bản nháp F7 §2 so W1 (A = K100/0,85/0,10/2, B ổn định) với W0 = P2 (K100/0,95/0,10/2 đối xứng).
W0 và W1 khác nhau HAI thứ (mức tải của A và sự dị loại) ⇒ so sánh bị nhiễu (confounded).
Đối chứng đúng cho W1 là hai thế giới cha: AA (A đối xứng) và BB (B đối xứng). Chỉ đổi đúng một thứ: path thứ hai.
Dùng nguyên máy của t08 (cầu phương t07, đọc đồng bộ như f04b A0, cur = A hoặc B với xác suất 1/2).
  Bảng 1: thế giới W1 của bản nháp (ρ̄_B = 0,931, khớp theo PSA) so với cha của nó.
  Bảng 2: thiết kế đã sửa, ρ̄_B = 0,918 (khớp delay TB trong DES, xem t09).
  Bảng 3: độ nhạy của κ theo ρ̄_B (độ lệch delay TB giữa hai path).
Seed 11922 (dải toy v2, không giao F7). Provenance: Claude (AI) soạn khi review L1.7; tác giả chạy lại, kiểm.
Chạy: python experiments/t08b_parents_kappa.py | tee experiments/results/t08b_parents_kappa_output.txt
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t07_kappa_pred as t7
import t08_heterogeneous_kappa as t8

SEED = 11922
A = "K100/0,85/0,10/2"
for rb in (0.918, 0.931, 0.90, 0.91, 0.925, 0.94):
    t8.PATHS[f"B{rb:.3f}"] = (100, rb, 0.03, 10.0)


def kappas(a, b, tag):
    """κ so với MỘT ngưỡng chung (bin Ī gộp) và so với NGƯỠNG THEO CHIỀU (bin Ī trong từng chiều)."""
    rng = np.random.default_rng([SEED, tag])
    (ea, va), (eb, vb) = t8.path_moments(rng, a), t8.path_moments(rng, b)
    cur_a = rng.random(t8.N) < 0.5
    ibar, s = np.where(cur_a, ea - eb, eb - ea), np.sqrt(va + vb)
    k_all = t7.kappa(ibar, s, True)
    k_dir = (cur_a.mean() * t7.kappa(ibar[cur_a], s[cur_a], True)
             + (~cur_a).mean() * t7.kappa(ibar[~cur_a], s[~cur_a], True))
    return k_all, k_dir, ea.mean() - eb.mean()


def table(title, worlds):
    print(f"\n{title}")
    print(f"{'thế giới':12s} {'path 1':18s} {'path 2':18s} | {'κ_chung':>7s} {'κ_chiều':>7s} | {'E[T]₁ − E[T]₂ (mô hình)':>23s}")
    out = {}
    for i, (lab, a, b) in enumerate(worlds):
        out[lab] = kappas(a, b, i + 10 * len(title))
        print(f"{lab:12s} {a:18s} {b:18s} | {out[lab][0]:7.3f} {out[lab][1]:7.3f} | {out[lab][2]:+20.1f} ms")
    return out


if __name__ == "__main__":
    print(f"t08b — κ của thế giới dị loại so với thế giới cha; N = {t8.N}, seed {SEED}")
    old = table("BẢNG 1 — W1 của bản nháp (ρ̄_B = 0,931, khớp bằng PSA)",
                [("W1 nháp", A, "B0.931"), ("cha AA", A, A), ("cha BB", "B0.931", "B0.931"),
                 ("W0 nháp=P2", "K100/0,95/0,10/2", "K100/0,95/0,10/2")])
    print(f"  Bản nháp so W1 với W0: Δκ_chung = {old['W1 nháp'][0] - old['W0 nháp=P2'][0]:+.3f} (NHIỄU: đổi 2 thứ)")
    print(f"  Phần do mức tải của A (cha AA − W0) = {old['cha AA'][1] - old['W0 nháp=P2'][1]:+.3f}")
    new = table("BẢNG 2 — thiết kế đã sửa (ρ̄_B = 0,918, khớp delay TB trong DES)",
                [("AB (W1)", A, "B0.918"), ("AA (C_A)", A, A), ("BB (C_B)", "B0.918", "B0.918")])
    m1 = new["AB (W1)"][0] - new["AB (W1)"][1]
    m2 = new["AB (W1)"][1] - new["AA (C_A)"][1]
    print(f"  M1 (chiều là biến Z): κ_chung(AB) − κ_chiều(AB) = {m1:+.3f}")
    print(f"  M2 (dị loại có thêm bất định trong chiều?): κ_chiều(AB) − κ_chiều(AA) = {m2:+.3f}")
    print(f"      so với cha ổn định: κ_chiều(AB) − κ_chiều(BB) = {new['AB (W1)'][1] - new['BB (C_B)'][1]:+.3f}")
    table("BẢNG 3 — độ nhạy theo ρ̄_B (A cố định)", [(f"ρ̄_B {rb:.3f}", A, f"B{rb:.3f}") for rb in (0.90, 0.91, 0.918, 0.925, 0.931, 0.94)])
    assert m1 > 0.05, "thiết kế phải tạo được biến Z theo chiều"
    assert m2 < 0, "lý thuyết dự đoán dị loại KHÔNG làm tăng κ trong chiều so với cha biến động"
