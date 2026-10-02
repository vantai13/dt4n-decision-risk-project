"""n02b (L1.3) — Tách nguồn M ("đo") thành hai cơ chế LỒNG NHAU: gộp cửa sổ, rồi nhiễu đếm trên cửa sổ đó.

Ba mức thông tin về một đường (không có "nhiễu mà không gộp": cửa sổ → 0 thì nhiễu đếm → vô hạn):
  inst  : tải tức thời chính xác ở cuối cửa sổ       (không gộp, không nhiễu)
  win   : trung bình chính xác trên cửa sổ T_tel       (gộp, không nhiễu)
  noisy : đếm gói trên cửa sổ T_tel                     (gộp + nhiễu)  ← telemetry thật
Dùng lại thế giới và số ngẫu nhiên của n02 (cùng seed → cùng thế giới). Tham số twin đúng (P tắt). H = 0,5 s.
"""
from pathlib import Path

import numpy as np
from scipy import stats

from experiments.n02_source_factorial import world, world_digest, write_csv
from experiments.scan.cell import get_curve
from experiments.scan.grid import controls
from experiments.scan.twin import posterior, twin_view
from experiments.scan.world import PKT_BITS, box_avg

_, cell = controls()
curve, s_ms = get_curve(cell)
eps = cell["eps_over_s"] * s_ms
s_sec = PKT_BITS / (cell["mbps"] * 1e6)


def regret(w, s_on, mode):
    post = {}
    for name in "AB":
        p, ww = cell[name], w[name]
        end = ww["r_last"] if s_on else ww["t_dec"]
        gap = (ww["t_dec"] - end) + cell["a"]
        if mode[name] == "inst":
            rh, W, R = np.interp(end, ww["tt"], ww["rho"]), 1e-6, 0.0
        else:
            W = p["T_tel"]
            avg = box_avg(ww["cs"], ww["dt"], end - W, end)
            if mode[name] == "win":
                rh, R = avg, 0.0
            else:
                rh = stats.poisson.ppf(ww["u"], np.maximum(avg, 0) * W / s_sec) * s_sec / W
                R = p["rho_bar"] * s_sec / W
        m, v = posterior(rh, gap, W, cell["H"], p["rho_bar"], p["sigma"], p["tau"], R)
        post[name] = (m, np.broadcast_to(v, m.shape).copy())
    ibar = twin_view(curve, *post["A"], *post["B"], eps)[0]
    I = curve(w["A"]["G"]) - curve(w["B"]["G"])
    return np.mean(np.maximum(I, 0)) - np.mean((ibar > 0) * I)


def main():
    worlds = [world(9101 + i, cell) for i in range(10)]
    before = [world_digest(w) for w in worlds]
    rows = []
    cases = [("inst  / inst ", dict(A="inst", B="inst")),
             ("win   / win  ", dict(A="win", B="win")),
             ("noisy / noisy", dict(A="noisy", B="noisy")),
             ("inst  / win  ", dict(A="inst", B="win")),      # chỉ B bị gộp 30 s
             ("noisy / inst ", dict(A="noisy", B="inst"))]    # chỉ A bị nhiễu đếm + gộp 0,5 s
    cases.append(("win   / inst ", dict(A="win", B="inst")))  # bổ sung: tách nhiễu A khỏi gộp A
    print("mức thông tin A / B     regret (ms/lần kiểm)   S tắt (cửa sổ kết thúc lúc t) | S bật (bản tin mới nhất)")
    for label, mode in cases:
        values = [[regret(w, s_on, mode) for w in worlds] for s_on in (0, 1)]
        r0, r1 = map(np.mean, values)
        for s_on, xs in enumerate(values):
            rows.extend(dict(seed=9101+i, S=s_on, A=mode["A"], B=mode["B"], regret_ms=float(x)) for i,x in enumerate(xs))
        print(f"  {label}                                {r0:6.3f}           | {r1:6.3f}")

    assert before == [world_digest(w) for w in worlds]
    assert all(np.isfinite(row["regret_ms"]) and row["regret_ms"] >= -1e-12 for row in rows)
    out=Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    write_csv(out / "n02b_measurement_split_seeds.csv", rows)
    print("Dòng win/inst là chẩn đoán bổ sung; noisy/inst gồm cả gộp và nhiễu A.")
    print("Đã lưu n02b_measurement_split_seeds.csv; kiểm hash thế giới trước/sau: ĐẠT.")


if __name__ == "__main__":
    main()
