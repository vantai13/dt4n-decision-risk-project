"""n02 (L1.3) — Phân rã regret của sandbox theo NGUỒN sai bằng factorial 2^3 trên THÔNG TIN đưa cho twin.

Thế giới giữ CỐ ĐỊNH (cùng tải OU, cùng thời điểm báo, cùng số ngẫu nhiên của nhiễu đếm → CRN giữa 8 cấu hình).
Chỉ đổi thứ twin được biết:
  S  (cũ)       : bật = cửa sổ đo kết thúc ở bản tin mới nhất (tuổi z, cộng a)  | tắt = cửa sổ kết thúc đúng lúc kiểm t
  M  (đo)       : bật = đếm gói trong cửa sổ W = T_tel (nhiễu đếm + gộp cửa sổ) | tắt = tải tức thời chính xác ở cuối cửa sổ
  P  (tham số)  : bật = twin tin ρ̄_B sai (mặc định 0,80; thật 0,85)           | tắt = tham số đúng
Cả 3 tắt = sandbox LÝ TƯỞNG của L1.2. Luật: duyệt ⇔ Ī > 0. Metric: regret (ms/lần kiểm) so với biết trước.
Ô POS_probeB, luôn ở A, mọi lần kiểm là đề xuất (G_all), thế giới PSA, seed pilot 9101+.
Chạy: python -m experiments.n02_source_factorial --H 0.5 --rho_b_wrong 0.80
"""
import argparse
import csv
import hashlib
import json
import time
from pathlib import Path
import itertools
import math

import numpy as np
from scipy import stats

from experiments.scan.cell import get_curve
from experiments.scan.grid import controls
from experiments.scan.twin import posterior, twin_view
from experiments.scan.world import PKT_BITS, box_avg, simulate_ou

FACTORS = ("S", "M", "P")


def world(seed, cell):
    """Tải OU + lịch báo telemetry (không treo) + số ngẫu nhiên chung cho nhiễu đếm."""
    rng = np.random.default_rng(seed)
    H, a, n = cell["H"], cell["a"], cell["n_epochs"]
    paths = (cell["A"], cell["B"])
    dt = min(min(min(p["T_tel"] for p in paths), H) / 10, min(p["tau"] for p in paths) / 20)
    t_dec = 3 * max(p["T_tel"] for p in paths) + max(p["d"] for p in paths) + H * np.arange(n)
    n_grid = int(np.ceil((t_dec[-1] + a + 2 * H) / dt)) + 1
    tt = np.arange(n_grid) * dt
    out = {}
    for name, p in zip("AB", paths):
        rho = simulate_ou(rng, n_grid, dt, p["rho_bar"], p["sigma"], p["tau"])
        cs = np.concatenate([[0.0], np.cumsum(rho) * dt])
        phase = rng.uniform(0, p["T_tel"])
        r_last = phase + np.floor((t_dec - p["d"] - phase) / p["T_tel"]) * p["T_tel"]   # bản tin mới nhất đã tới
        out[name] = dict(cs=cs, tt=tt, dt=dt, rho=rho, r_last=r_last, t_dec=t_dec,
                         u=rng.uniform(size=n),                                       # CRN cho nhiễu đếm
                         G=box_avg(cs, dt, t_dec + a, t_dec + a + H))
    return out


def twin_info(w, p, cell, s_on, m_on):
    """Trả (rhohat, gap, W, R) mà twin nhận, theo công tắc S và M."""
    s_sec = PKT_BITS / (cell["mbps"] * 1e6)
    end = w["r_last"] if s_on else w["t_dec"]                  # cửa sổ kết thúc ở đâu
    gap = (w["t_dec"] - end) + cell["a"]                       # khoảng từ cuối cửa sổ tới đầu khoảng giữ
    if m_on:
        W = p["T_tel"]
        lam = np.maximum(box_avg(w["cs"], w["dt"], end - W, end), 0) * W / s_sec
        rhohat = stats.poisson.ppf(w["u"], lam) * s_sec / W    # đếm gói, dùng CHUNG số ngẫu nhiên u
        return rhohat, gap, W, None                             # R tính sau theo ρ̄ của twin
    return np.interp(end, w["tt"], w["rho"]), gap, 1e-6, 0.0


def regret_of(cfg, w, cell, curve, eps, rho_b_wrong):
    s_on, m_on, p_on = cfg
    s_sec = PKT_BITS / (cell["mbps"] * 1e6)
    post = {}
    for name in "AB":
        p = cell[name]
        rho_bar = rho_b_wrong if (p_on and name == "B") else p["rho_bar"]
        rhohat, gap, W, R = twin_info(w[name], p, cell, s_on, m_on)
        if R is None:
            R = rho_bar * s_sec / W                             # twin tính nhiễu đếm theo niềm tin của nó
        m, v = posterior(rhohat, gap, W, cell["H"], rho_bar, p["sigma"], p["tau"], R)
        post[name] = (m, np.broadcast_to(v, m.shape).copy())
    ibar = twin_view(curve, *post["A"], *post["B"], eps)[0]
    I = curve(w["A"]["G"]) - curve(w["B"]["G"])
    return float(np.mean(np.maximum(I, 0)) - np.mean((ibar > 0) * I))


def contrasts(reg):
    """Hiệu ghép cặp theo seed; giữ vector tới sau khi tính Shapley/CI."""
    def at(levels):
        return reg[tuple(levels[f] for f in FACTORS)]

    effects = {}
    for f in FACTORS:
        rest = [g for g in FACTORS if g != f]
        effects[f"main:{f}"] = np.mean([
            at(dict(zip((f, *rest), (1, u, v)))) - at(dict(zip((f, *rest), (0, u, v))))
            for u, v in itertools.product((0, 1), repeat=2)], axis=0)
    for f, g in itertools.combinations(FACTORS, 2):
        z = next(q for q in FACTORS if q not in (f, g))
        for level in (0, 1):
            effects[f"interaction:{f}*{g}|{z}={level}"] = sum(
                (-1)**(u + v) * at({f: u, g: v, z: level})
                for u, v in itertools.product((0, 1), repeat=2))
    effects["interaction:S*M*P"] = sum((-1)**(3 - sum(c)) * value for c, value in reg.items())
    orders = list(itertools.permutations(FACTORS))
    for order in orders:
        on = dict.fromkeys(FACTORS, 0)
        for f in order:
            before = at(on)
            on[f] = 1
            effects[f"ladder:{''.join(order)}:{f}"] = at(on) - before
    for f in FACTORS:
        effects[f"shapley:{f}"] = np.mean([effects[f"ladder:{''.join(order)}:{f}"] for order in orders], axis=0)
    total = reg[(1, 1, 1)] - reg[(0, 0, 0)]
    np.testing.assert_allclose(sum(effects[f"shapley:{f}"] for f in FACTORS), total, atol=1e-12)
    effects["total:111-000"] = total
    return effects


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def world_digest(w):
    digest = hashlib.sha256()
    for name in "AB":
        for key in sorted(w[name]):
            digest.update(f"{name}:{key}".encode())
            digest.update(np.asarray(w[name][key]).tobytes())
    return digest.hexdigest()


def export(reg, worlds, cell, rho_wrong, elapsed):
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    tag = f"n02_H{cell['H']:g}_rho{rho_wrong:.2f}"
    effects = contrasts(reg)
    write_csv(out / f"{tag}_seeds.csv", [dict(seed=9101+i, S=c[0], M=c[1], P=c[2], regret_ms=float(x))
              for c, xs in reg.items() for i, x in enumerate(xs)])
    write_csv(out / f"{tag}_contrasts_seeds.csv", [dict(seed=9101+i, contrast=name, value_ms=float(x))
              for name, xs in effects.items() for i, x in enumerate(xs)])
    summary = []
    for name, xs in {**{f"regret:{''.join(map(str,c))}": xs for c, xs in reg.items()}, **effects}.items():
        m = float(np.mean(xs))
        half = float(stats.t.ppf(.975, len(xs)-1) * np.std(xs, ddof=1) / np.sqrt(len(xs)))
        summary.append(dict(contrast=name, mean_ms=m, ci95_half_ms=half, ci95_low_ms=m-half, ci95_high_ms=m+half))
    write_csv(out / f"{tag}_summary.csv", summary)
    repeat_count, changed_count = 0, 0
    for w in worlds:
        measured = twin_info(w["B"], cell["B"], cell, 1, 1)[0]
        repeated = np.diff(w["B"]["r_last"]) == 0
        repeat_count += int(repeated.sum())
        changed_count += int((repeated & (np.diff(measured) != 0)).sum())
    (out / f"{tag}_run.json").write_text(json.dumps(dict(
        cell=cell, rho_b_wrong=rho_wrong, seeds=list(range(9101, 9101+len(worlds))),
        elapsed_seconds=elapsed, world_hashes=[world_digest(w) for w in worlds],
        B_repeated_report_adjacent_epochs=repeat_count, B_changed_count_on_same_report=changed_count,
        noise_coupling="per-epoch uniform, not one fixed count per published report",
        ideal="state at t; W=1e-6 approximation; a fixed in every configuration"), indent=2)+"\n")
    print(f"\nĐã lưu {tag}_seeds.csv, _contrasts_seeds.csv, _summary.csv, _run.json; thời gian {elapsed:.3f} s")
    print(f"Kiểm telemetry B: {changed_count}/{repeat_count} cặp epoch cùng r_last có số đếm khác (n02 rút nhiễu theo epoch).")


def main():
    started = time.perf_counter()
    ap = argparse.ArgumentParser()
    ap.add_argument("--H", type=float, default=0.5)
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--rho_b_wrong", type=float, default=0.80)
    args = ap.parse_args()
    if not np.isfinite(args.H) or args.H <= 0 or not 2 <= args.seeds <= 899:
        ap.error("H phải >0, hữu hạn; seeds từ 2 đến 899 để tính CI và chỉ dùng pilot 9101–9999")
    if not np.isfinite(args.rho_b_wrong) or args.rho_b_wrong <= 0:
        ap.error("rho_b_wrong phải hữu hạn và >0")
    _, cell = controls()
    cell["H"] = args.H
    curve, s_ms = get_curve(cell)
    eps = cell["eps_over_s"] * s_ms
    cfgs = list(itertools.product((0, 1), repeat=3))
    worlds = [world(9101 + i, cell) for i in range(args.seeds)]
    before = [world_digest(w) for w in worlds]
    R = np.array([[regret_of(c, w, cell, curve, eps, args.rho_b_wrong) for c in cfgs] for w in worlds])
    assert before == [world_digest(w) for w in worlds], "Các công tắc không được sửa thế giới"
    assert np.isfinite(R).all() and (R >= -1e-12).all()
    reg = dict(zip(cfgs, R.T))                                                     # mỗi cấu hình: vector theo seed
    t = stats.t.ppf(0.975, args.seeds - 1)
    ci = lambda x: (x.mean(), t * x.std(ddof=1) / math.sqrt(len(x)))

    def at(**lv):                                                  # regret (vector theo seed) tại một cấu hình
        return reg[tuple(lv[f] for f in FACTORS)]

    print(f"H={args.H} s, {args.seeds} seed, twin tin ρ̄_B={args.rho_b_wrong} khi P bật.")
    print("Regret (ms/lần kiểm) của 8 cấu hình  [S M P; 1 = bật nguồn sai]")
    for c in cfgs:
        m, h = ci(reg[c])
        print(f"  {c}  {m:7.3f} ± {h:.3f}")

    print("\nHiệu ứng (± CI95 ghép cặp theo seed: mọi cấu hình dùng CÙNG thế giới nên trừ nhau theo seed được):")
    for f in FACTORS:                                              # chính: TB qua 4 tổ hợp mức của 2 nguồn kia
        o1, o2 = [g for g in FACTORS if g != f]
        diffs = [at(**{f: 1, o1: u, o2: v}) - at(**{f: 0, o1: u, o2: v}) for u in (0, 1) for v in (0, 1)]
        m, h = ci(np.mean(diffs, axis=0))
        print(f"  chính {f}        {m:+7.3f} ± {h:.3f}")
    for f, g in itertools.combinations(FACTORS, 2):                # tương tác = phần dư so với cộng tính
        z = next(q for q in FACTORS if q not in (f, g))
        for lz in (0, 1):
            dd = (at(**{f: 1, g: 1, z: lz}) - at(**{f: 1, g: 0, z: lz})
                  - at(**{f: 0, g: 1, z: lz}) + at(**{f: 0, g: 0, z: lz}))
            m, h = ci(dd)
            print(f"  {f}×{g} khi {z}={lz}    {m:+7.3f} ± {h:.3f}   (y11 − y10 − y01 + y00)")
    # Ghi chú: giáo trình thiết kế 2^k (Jain 1991; Montgomery) báo tương tác bằng MỘT NỬA "hiệu của hiệu" này.

    contrib = {f: {} for f in FACTORS}                             # phần góp của f theo từng thứ tự
    for order in itertools.permutations(FACTORS):
        on = dict.fromkeys(FACTORS, 0)
        for f in order:
            before = at(**on).mean()
            on[f] = 1
            contrib[f][order] = at(**on).mean() - before
    print("\nBậc thang (thêm từng nguồn từ LÝ TƯỞNG) theo vài thứ tự — phần 'góp' của mỗi nguồn:")
    for order in (("S", "M", "P"), ("P", "M", "S"), ("M", "P", "S")):
        print(f"  {'→'.join(order)}   " + "  ".join(f"{f}:{contrib[f][order]:+.3f}" for f in order))
    print("\nShapley (trung bình phần góp qua cả 6 thứ tự):")
    for f in FACTORS:
        print(f"  {f}: {np.mean(list(contrib[f].values())):+.3f}")
    total = sum(np.mean(list(contrib[f].values())) for f in FACTORS)
    print(f"  tổng {total:+.3f} = regret(bật hết) − regret(lý tưởng) = {(at(S=1, M=1, P=1) - at(S=0, M=0, P=0)).mean():+.3f}")
    export(reg, worlds, cell, args.rho_b_wrong, time.perf_counter() - started)


if __name__ == "__main__":
    main()
