"""rollout_v5 — KHÁM PHÁ (POST HOC), MỘT ô R3_outage. Sửa các điểm phản biện của v4 trước khi đi tiếp:

(1) Nhãn harm NHẤT QUÁN với cửa sổ dự đoán: harm_W của một lần đổi tại e = 1{ mean_{k<T_hd}(D_cũ − D_mới)[e+k] < −ε },
    đúng khoảng bị khoá sau khi đổi. Vẫn báo harm_1s (nhãn cũ) để so.
(2) MỌI luật (kể cả bảng 24) chọn bằng CÙNG bộ chọn: delay TB nhỏ nhất trên calibration với harm_W ≤ α.
    Thêm lượt α = ∞ để kiểm TRỰC TIẾP ràng buộc có cắn không.
(3) Lưới ngưỡng mịn hơn, gồm cả nửa dưới phân bố |Ī|; bảng 24 coordinate descent CÓ ràng buộc, 3 điểm khởi đầu.
(4) Baseline CÙNG SỐ THAM SỐ quyết định với K2: SClin — đổi nếu Ī > h0 + h1·tuổi_path_đích (2 tham số).
    Nếu K2 ≈ SClin thì phần p₋ đóng góp không vượt "ngưỡng tăng tuyến tính theo tuổi".
(5) Chẩn đoán twin: Ī (chân trời 30 s) so với I_W thật (lệch, độ dốc); độ tin cậy của p₋ với harm_W và harm_1s.
Kiến thức của twin (ghi rõ): BIẾT ĐÚNG ρ̄, σ, τ, capacity, buffer, mô hình nhiễu đếm của từng path; KHÔNG biết quá trình
outage (chỉ thấy tuổi bản tin). Mọi luật SC* dùng Ī của cùng twin; S0* chỉ dùng số đo thô.
Seed: cal 86001–86020, test 89001–89020 — test ĐÃ dùng ở v4, KHÔNG còn là holdout mới.
Chạy:  python -m experiments.scan.rollout_v5 | tee results/go_test/rollout_v5_output.txt
"""
import csv
import json
import time
from pathlib import Path

import numpy as np
from numba import njit

from experiments.scan import rollout_v2 as v2
from experiments.scan import rollout_v3 as v3

HD, ALPHA, WORLD = 30, 0.002, "R3_outage"
TEST = range(89001, 89021)
A_EDGES, R_EDGES = np.array([2.0, 10.0, 30.0]), np.array([0.75, 0.90])
NA, NR = len(A_EDGES) + 1, len(R_EDGES) + 1
NT = 2 * NA * NR                                   # 24 ô: (đường hiện tại, tuổi đích, tải đích)
MUS = (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0)
H1S = (0.0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0)  # ms ngưỡng tăng thêm mỗi giây tuổi path đích


@njit(cache=True)
def rollout(ipA, ibA, pdA, puA, agA, agB, rhA, rhB, DA, DB, IWA, eps, kind, mu, h1, tab, a_edges, r_edges, hd):
    """kind 0: Î plug-in theo bảng · 1: Ī theo bảng · 2: K2 (μ, θ = tab[p,0]) · 3: SClin (Ī − h1·tuổi > tab[p,0])."""
    n_pol, n = len(kind), len(DA)
    na, nr = len(a_edges) + 1, len(r_edges) + 1
    delay, h1s, hW, nsw = np.zeros(n_pol), np.zeros(n_pol), np.zeros(n_pol), np.zeros(n_pol)
    for p in range(n_pol):
        cur, last = 0, -10**9
        for e in range(n):
            if cur == 0:
                ip, ib, pd, ag, rh, I1, IW = ipA[e], ibA[e], pdA[e], agB[e], rhB[e], DA[e] - DB[e], IWA[e]
            else:
                ip, ib, pd, ag, rh, I1, IW = -ipA[e], -ibA[e], puA[e], agA[e], rhA[e], DB[e] - DA[e], -IWA[e]
            if e - last >= hd:
                if kind[p] == 2:
                    s, t = ((ib - mu[p]) / max(pd, 1e-300) if ib > mu[p] else -np.inf), tab[p, 0]
                elif kind[p] == 3:
                    s, t = ib - h1[p] * ag, tab[p, 0]
                else:
                    b = 0
                    while b < na - 1 and ag >= a_edges[b]:
                        b += 1
                    c = 0
                    while c < nr - 1 and rh >= r_edges[c]:
                        c += 1
                    s, t = (ip if kind[p] == 0 else ib), tab[p, (cur * na + b) * nr + c]
                if s > t:
                    nsw[p] += 1
                    h1s[p] += I1 < -eps
                    hW[p] += IW < -eps
                    cur, last = 1 - cur, e
            delay[p] += DA[e] if cur == 0 else DB[e]
    return delay, h1s, hW, nsw


def window_mean(x, w):
    c = np.r_[0.0, np.cumsum(x)]
    i = np.arange(len(x))
    j = np.minimum(i + w, len(x))
    return (c[j] - c[i]) / (j - i)


def prep(data, worlds_raw, hd):
    for d, w in zip(data, worlds_raw):
        d["rh_A"], d["rh_B"] = w["A"]["rhohat"], w["B"]["rhohat"]
        d["IW_A"] = window_mean(d["DA"] - d["DB"], hd)
    return data


def run(data, kind, mu, h1, tab, eps):
    res = [rollout(d["Iplug_A"], d["Ibar_A"], d["pdn_A"], d["pup_A"], d["age_A"], d["age_B"], d["rh_A"], d["rh_B"],
                   d["DA"], d["DB"], d["IW_A"], eps, kind, mu, h1, tab, A_EDGES, R_EDGES, HD) for d in data]
    n = len(data[0]["DA"])
    return {k: np.array([r[i] for r in res]) / n for i, k in enumerate(("delay", "harm1", "harmW", "nsw"))}


def pick(r, alpha):
    D = np.where(r["harmW"].mean(0) <= alpha, r["delay"].mean(0), np.inf)
    j = int(np.argmin(D))
    return j, D[j]


def grid(x, n=60):
    return np.unique(np.r_[0.0, np.quantile(np.abs(x), np.linspace(0.0, 0.99995, n)), np.inf])


def family(n, kind, mu=0.0, h1=0.0):
    return np.full(n, kind, np.int64), np.full(n, float(mu)), np.full(n, float(h1))


def tables(cal, eps, alpha, g_ip, g_ib):
    """Mọi họ luật trên bảng 24 ô. Trả {tên: (kind, mu, h1, tab)}."""
    out = {}
    for name, kd, gr in (("S0", 0, g_ip), ("SC", 1, g_ib)):
        tab = np.repeat(gr[:, None], NT, 1)
        out[name] = (kd, 0.0, 0.0, tab[pick(run(cal, *family(len(gr), kd), tab, eps), alpha)[0]])
    half = NT // 2
    for name, kd, gr in (("S0dir", 0, g_ip), ("SCdir", 1, g_ib)):
        tA, tB = np.meshgrid(gr, gr, indexing="ij")
        tab = np.c_[np.repeat(tA.reshape(-1, 1), half, 1), np.repeat(tB.reshape(-1, 1), half, 1)]
        out[name] = (kd, 0.0, 0.0, tab[pick(run(cal, *family(len(tab), kd), tab, eps), alpha)[0]])

    def descend(start, groups, rounds):
        best = start.copy()
        for _ in range(rounds):
            for cols in groups:
                tab = np.repeat(best[None, :], len(g_ib) + 1, 0)
                tab[:-1][:, cols] = g_ib[:, None]                       # dòng cuối = giữ nguyên ⇒ không bao giờ tệ đi
                j, v = pick(run(cal, *family(len(tab), 1), tab, eps), alpha)
                if np.isfinite(v):
                    best = tab[j].copy()
        return best, pick(run(cal, *family(1, 1), best[None, :], eps), alpha)[1]

    g8 = [list(range((c * NA + b) * NR, (c * NA + b) * NR + NR)) for c in range(2) for b in range(NA)]
    t8, _ = descend(out["SCdir"][3], g8, 3)
    out["SCtab8"] = (1, 0.0, 0.0, t8)
    starts = [out["SCtab8"][3], out["SCdir"][3], out["SC"][3]]
    cands = [descend(s, [[c] for c in range(NT)], 4) for s in starts]
    out["SCtab24"] = (1, 0.0, 0.0, min(cands, key=lambda x: x[1])[0])

    k, m, h, t = [], [], [], []
    for h1 in H1S:                                                       # SClin: (h0, h1)
        for h0 in g_ib:
            k.append(3); m.append(0.0); h.append(h1); t.append(h0)
    for mu in MUS:                                                       # K2: (μ, θ)
        sc = np.concatenate([((x[x > mu] - mu) / np.maximum(pd[x > mu], 1e-300))
                             for d in cal for x, pd in ((d["Ibar_A"], d["pdn_A"]), (-d["Ibar_A"], d["pup_A"]))])
        for th in np.r_[np.quantile(sc[np.isfinite(sc)], np.linspace(0, 0.9999, 60)), np.inf]:
            k.append(2); m.append(mu); h.append(0.0); t.append(th)
    k, m, h, t = np.array(k), np.array(m), np.array(h), np.array(t)
    r = run(cal, k, m, h, np.repeat(t[:, None], NT, 1), eps)
    for name, kd in (("SClin", 3), ("K2", 2)):
        sel = np.flatnonzero(k == kd)
        j = sel[pick({q: v[:, sel] for q, v in r.items()}, alpha)[0]]
        out[name] = (kd, m[j], h[j], np.full(NT, t[j]))
    return out


def evaluate(data, pol, eps):
    return {n: run(data, *[np.array([v]) for v in p[:3]], p[3][None, :], eps) for n, p in pol.items()}


def twin_check(test, eps, writer=None, h_tw=HD):
    I = np.concatenate([np.r_[d["IW_A"], -d["IW_A"]] for d in test])
    I1 = np.concatenate([np.r_[d["DA"] - d["DB"], d["DB"] - d["DA"]] for d in test])
    Ib = np.concatenate([np.r_[d["Ibar_A"], -d["Ibar_A"]] for d in test])
    pd = np.concatenate([np.r_[d["pdn_A"], d["pup_A"]] for d in test])
    # KHÔNG lấy lệch TB trên dữ liệu gộp hai chiều: I và Ī đối xứng nên trung bình = 0 theo cấu trúc.
    print(f"  [twin] corr(Ī, I_W) {np.corrcoef(Ib, I)[0, 1]:.3f}; lệch có điều kiện (Ī > 0):")
    for lo, hi in ((0, 2), (2, 5), (5, 10), (10, 20), (20, np.inf)):
        m = (Ib > lo) & (Ib <= hi)
        print(f"     Ī ∈ ({lo}, {hi}]: n={m.sum():6d} | Ī TB {Ib[m].mean():6.2f} | I_W TB {I[m].mean():6.2f} | "
              f"lệch {I[m].mean() - Ib[m].mean():+6.2f} ms")
        if writer is not None:
            writer.writerow([h_tw, "center_bias", lo, hi, int(m.sum()), Ib[m].mean(),
                             I[m].mean(), I1[m].mean(), I[m].mean() - Ib[m].mean()])
    edges = [0, 0.001, 0.01, 0.05, 0.2, 1.0001]
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (pd >= lo) & (pd < hi) & (Ib > 0)
        if m.sum() > 50:
            print(f"     p₋ ∈ [{lo}, {hi}) (Ī > 0, n={m.sum():6d}): p₋ TB {pd[m].mean():.4f} | "
                  f"tần suất harm_W {np.mean(I[m] < -eps):.4f} | harm_1s {np.mean(I1[m] < -eps):.4f}")
            if writer is not None:
                writer.writerow([h_tw, "risk_calibration", lo, hi, int(m.sum()), pd[m].mean(),
                                 np.mean(I[m] < -eps), np.mean(I1[m] < -eps), ""])


def policy_record(p):
    kd, mu, h1, tab = p
    return dict(kind=int(kd), mu_ms=float(mu), age_slope_ms_per_s=float(h1),
                thresholds=[float(x) if np.isfinite(x) else str(x) for x in tab])


def same_policy(p, q):
    return p[:3] == q[:3] and np.array_equal(p[3], q[3])


def main():
    t0 = time.time()
    sc = {w["name"]: w for w in v2.worlds()}[WORLD]
    eps = sc["eps_ms"]
    cal_w = [v2.simulate(s, sc) for s in v2.CAL]
    test_w = [v2.simulate(s, sc) for s in TEST]
    cal = prep(v3.twin_for(cal_w, sc, HD), cal_w, HD)
    test = prep(v3.twin_for(test_w, sc, HD), test_w, HD)
    output = Path("results/go_test")
    output.mkdir(parents=True, exist_ok=True)
    print(f"######## {WORLD} | hold-down {HD} s, twin {HD} s | nhãn harm theo cửa sổ khoá | {time.time() - t0:.0f} s")
    with (output / "rollout_v5_diagnostics.csv").open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["twin_horizon_s", "diagnostic", "lo", "hi", "n_oriented_epochs",
                         "predicted", "observed_window", "observed_1s", "bias_ms"])
        print("  Chẩn đoán twin 1 s so với nhãn cửa sổ 30 s:")
        twin_check(prep(v3.twin_for(test_w, sc, 1), test_w, HD), eps, writer, 1)
        print("  Chẩn đoán twin 30 s so với nhãn cửa sổ 30 s:")
        twin_check(test, eps, writer, HD)
    g_ip = grid(np.concatenate([d["Iplug_A"] for d in cal]))
    g_ib = grid(np.concatenate([d["Ibar_A"] for d in cal]))
    with (output / "rollout_v5_seeds.csv").open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerow([
            "world", "alpha", "split", "seed", "rule", "delay_ms", "harm_1s_per_epoch",
            "harm_window_per_epoch", "switches_per_epoch", "policy",
        ])
    selected = {}
    for alpha in (ALPHA, np.inf):
        pol = tables(cal, eps, alpha, g_ip, g_ib)
        selected[str(alpha)] = pol
        rc, rt = evaluate(cal, pol, eps), evaluate(test, pol, eps)
        with (output / "rollout_v5_seeds.csv").open("a", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            for split, seeds, res in (("calibration", v2.CAL, rc), ("test", TEST, rt)):
                for name, p in pol.items():
                    for i, seed in enumerate(seeds):
                        writer.writerow([WORLD, alpha, split, seed, name,
                                         res[name]["delay"][i, 0], res[name]["harm1"][i, 0],
                                         res[name]["harmW"][i, 0], res[name]["nsw"][i, 0],
                                         json.dumps(policy_record(p))])
        print(f"\n  α = {alpha} | {time.time() - t0:.0f} s")
        print(f"  {'luật':8s} {'delay cal':>9s} {'harm_W cal':>10s} | {'delay test':>10s} {'harm_W':>7s} {'harm_1s':>7s} "
              f"{'đổi/ph':>6s} | {'luật − K2 trên test, ms [CI95]':>34s}")
        for n in pol:
            m, lo, hi = v2.ci(rt[n]["delay"][:, 0] - rt["K2"]["delay"][:, 0])
            print(f"  {n:8s} {rc[n]['delay'].mean():9.3f} {100 * rc[n]['harmW'].mean():9.3f}% | "
                  f"{rt[n]['delay'].mean():10.3f} {100 * rt[n]['harmW'].mean():6.3f}% {100 * rt[n]['harm1'].mean():6.3f}% "
                  f"{60 * rt[n]['nsw'].mean():6.2f} | {m:+.3f} [{lo:+.3f}; {hi:+.3f}] ({100 * m / rt[n]['delay'].mean():+.1f}%)")
        print(f"  K2: μ = {pol['K2'][1]}, θ = {pol['K2'][3][0]:.4g} | SClin: h0 = {pol['SClin'][3][0]:.3f} ms, "
              f"h1 = {pol['SClin'][2]} ms/s", flush=True)
    equal = {r: same_policy(selected[str(ALPHA)][r], selected[str(np.inf)][r])
             for r in selected[str(ALPHA)]}
    print(f"\n  Kiểm α={ALPHA} so với α=∞: cùng chính sách {sum(equal.values())}/{len(equal)} họ: {equal}", flush=True)
    (output / "rollout_v5_policies.json").write_text(json.dumps({
        "classification": "POST HOC; previously used calibration/test and Claude sandbox run",
        "world": WORLD, "calibration_seeds": [86001, 86020], "test_seeds": [89001, 89020],
        "hold_down_s": HD, "twin_horizon_s": HD, "same_policy_finite_vs_infinite_alpha": equal,
        "tail_caveat": "Last HD-1 epochs use shortened windows, as supplied code; not full 30 s",
        "policies": {a: {r: policy_record(p) for r, p in pol.items()} for a, pol in selected.items()},
    }, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
