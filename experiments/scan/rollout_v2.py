"""rollout_v2 — KHÁM PHÁ (POST HOC). K2 có thắng được BASELINE TĨNH MẠNH NHẤT khi luật thật sự lái luồng không?

Baseline mới (cùng thông tin twin, cùng ngân sách harm, tune bằng rollout trên calibration):
  S0dir  : 2 ngưỡng plug-in theo chiều (A→B, B→A)              — luật vận hành "vào path cũ khó, về path tươi dễ"
  SCdir  : 2 ngưỡng trên Ī theo chiều
  SCtab  : bảng ngưỡng trên Ī theo (chiều × tuổi path ĐÍCH: <2, 2–10, 10–30, ≥30 s) = 8 tham số, coordinate descent
  K2     : (Ī − μ)/p₋ > θ, 2 tham số
Thế giới:
  R1, R2       : y hệt go_test (độ cũ CỐ ĐỊNH theo path: A 1 s, B 60 s)
  R3_outage    : hai ISP giống R1, CẢ HAI streaming 1 s, nhưng collector mất kết nối ngẫu nhiên từng path
                 (bắt đầu Poisson 1 lần/120 s, kéo dài Exp(TB 30 s); trong outage không bản tin nào tới)
                 ⇒ độ cũ thay đổi theo thời gian, KHÔNG gắn với danh tính path.
  R3_outageB   : như R3 nhưng chỉ path B bị outage (bất đối xứng, có cấu trúc).
Seed đã được Claude chạy trong sandbox: calibration 86001–86020, test 87001–87020.
Đây là tái lập POST HOC, không phải kiểm định trên seed chưa từng dùng.
Chạy:  python -m experiments.scan.rollout_v2 | tee results/go_test/rollout_v2_output.txt
"""
import copy
import csv
import json
import time
from pathlib import Path

import numpy as np
from numba import njit
from scipy import stats

from experiments.f04b_des_gap import workload_after
from experiments.scan import go_test as g
from experiments.scan.des_world import N_PROBE, latest_available
from experiments.scan.world import PKT_BITS, simulate_ou

CAL, TEST = range(86001, 86021), range(87001, 87021)
ALPHAS = (0.002, 0.01)
HOLDDOWN_S = (0, 30)
AGE_EDGES = np.array([2.0, 10.0, 30.0])          # tuổi path đích → 4 bucket
NB = len(AGE_EDGES) + 1
MUS = (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0)
N_THR = 40


# ------------------------------------------------------------------ thế giới có outage telemetry
def outage_mask(rng, r, rate, mean_dur):
    """True nếu bản tin đo tại r rơi vào một outage (bị mất)."""
    if rate <= 0:
        return np.zeros(len(r), bool)
    t_end = r[-1] + 1
    starts = np.cumsum(rng.exponential(1 / rate, int(t_end * rate * 2) + 10))
    starts = starts[starts < t_end]
    ends = starts + rng.exponential(mean_dur, len(starts))
    lost = np.zeros(len(r), bool)
    for s, e in zip(starts, ends):
        lost |= (r >= s) & (r < e)
    return lost


def des_path_outage(rng, rng_out, mbps, k, H, a, p, t_dec, t_end, dt):
    """Như des_world.des_path (cùng cách sinh tải, gói, hàng đợi, nhãn), thêm outage của collector."""
    s = PKT_BITS / (mbps * 1e6)
    n_grid = int(np.ceil(t_end / dt)) + 1
    rho = simulate_ou(rng, n_grid, dt, p["rho"], p["sigma"], p["tau"])
    t_grid = np.arange(n_grid + 1) * dt
    cum_lam = np.concatenate([[0.0], np.cumsum(np.clip(rho, 0.0, None) / s * dt)])
    u = np.cumsum(rng.exponential(1.0, int(cum_lam[-1] * 1.05) + 1000))
    arrivals = np.interp(u[u < cum_lam[-1]], cum_lam, t_grid)
    full = (k - 1) * s
    v_after = workload_after(arrivals, s, full)
    T = p["T_tel"]
    r = np.arange(rng.uniform(0, T) + T, t_end, T)
    count = np.searchsorted(arrivals, r) - np.searchsorted(arrivals, r - T)
    keep = ~outage_mask(rng_out, r, p.get("out_rate", 0.0), p.get("out_mean", 0.0))
    keep[0] = True
    rhohat, age = latest_available(r[keep], (count * s / T)[keep], r[keep] + p["d"], t_dec)
    probes = (t_dec + a)[:, None] + np.linspace(0.0, H, N_PROBE)[None, :]
    j = np.maximum(np.searchsorted(arrivals, probes, side="right") - 1, 0)
    v = np.maximum(v_after[j] - (probes - arrivals[j]), 0.0)
    v = np.where(probes >= arrivals[0], v, 0.0)
    ok = v <= full
    n_ok = ok.sum(1)
    D = np.where(n_ok > 0, np.where(ok, v + s, 0.0).sum(1) / np.maximum(n_ok, 1), k * s) * 1e3
    return dict(rhohat=rhohat, age=age, D=D)


def simulate(seed, sc):
    if not any(sc[q].get("out_rate", 0) > 0 for q in "AB"):
        return g.simulate(seed, sc)                      # R1/R2: đúng code đã kiểm của go_test
    rng = np.random.default_rng(seed)
    rng_out = np.random.default_rng([seed, 777])
    H, a = sc["H"], sc["a"]
    paths = (sc["A"], sc["B"])
    n = max(4000, int(100 * max(p["tau"] for p in paths) / H))
    dt = min(min(min(p["T_tel"] for p in paths), H) / 10, min(p["tau"] for p in paths) / 20)
    warm = 3 * max(p["T_tel"] for p in paths) + max(p["d"] for p in paths)
    t_dec = warm + H * np.arange(n)
    t_end = t_dec[-1] + a + 2 * H
    return {nm: des_path_outage(rng, rng_out, p["mbps"], p["k"], H, a, p, t_dec, t_end, dt) for nm, p in zip("AB", paths)}


def worlds():
    base, _ = g.scenarios()
    R1, R2 = base
    R3 = copy.deepcopy(R1); R3["name"] = "R3_outage"
    for q in "AB":
        R3[q]["T_tel"] = 1.0; R3[q]["out_rate"] = 1 / 120; R3[q]["out_mean"] = 30.0
    R3B = copy.deepcopy(R3); R3B["name"] = "R3_outageB"
    R3B["A"]["out_rate"] = 0.0
    return [R1, R2, R3, R3B]


# ------------------------------------------------------------------ rollout với bảng ngưỡng (Numba)
@njit(cache=True)
def rollout(ipA, ibA, pdA, puA, agA, agB, DA, DB, eps, kind, mu, tab, edges, hd):
    """kind: 0 = plug-in (Î), 1 = tâm (Ī), 2 = K2. tab[p, dir*NB + bucket(tuổi path đích)] = ngưỡng.
    Với K2 chỉ dùng tab[p, 0] (θ). Trả tổng delay trải qua, số harm, số lần đổi."""
    n_pol, n, nb = len(kind), len(DA), len(edges) + 1
    delay, harm, nsw = np.zeros(n_pol), np.zeros(n_pol), np.zeros(n_pol)
    for p in range(n_pol):
        cur, last = 0, -10**9
        for e in range(n):
            if cur == 0:
                ip, ib, pd, I, age_dst = ipA[e], ibA[e], pdA[e], DA[e] - DB[e], agB[e]
            else:
                ip, ib, pd, I, age_dst = -ipA[e], -ibA[e], puA[e], DB[e] - DA[e], agA[e]
            if e - last >= hd:
                b = 0
                while b < nb - 1 and age_dst >= edges[b]:
                    b += 1
                if kind[p] == 2:
                    s = (ib - mu[p]) / max(pd, 1e-300) if ib > mu[p] else -np.inf
                    t = tab[p, 0]
                else:
                    s = ip if kind[p] == 0 else ib
                    t = tab[p, cur * nb + b]
                if s > t:
                    nsw[p] += 1
                    if I < -eps:
                        harm[p] += 1
                    cur, last = 1 - cur, e
            delay[p] += DA[e] if cur == 0 else DB[e]
    return delay, harm, nsw


def run(data, kind, mu, tab, eps, hd):
    res = [rollout(d["Iplug_A"], d["Ibar_A"], d["pdn_A"], d["pup_A"], d["age_A"], d["age_B"], d["DA"], d["DB"],
                   eps, kind, mu, tab, AGE_EDGES, hd) for d in data]
    n = len(data[0]["DA"])
    return tuple(np.array([r[i] for r in res]) / n for i in range(3))     # (seed, policy) mỗi mảng


def pick(delay, harm, alpha):
    D = np.where(harm.mean(0) <= alpha, delay.mean(0), np.inf)
    j = int(np.argmin(D))
    return j, D[j]


def thr_grid(x):
    return np.r_[0.0, np.quantile(np.abs(x), np.linspace(0.5, 0.99995, N_THR)), np.inf]


def tune(cal, eps, alpha, hd):
    """Trả về {tên luật: (kind, mu, tab)} — mỗi họ chọn luật delay TB nhỏ nhất trên calibration, harm ≤ α."""
    ip = np.concatenate([d["Iplug_A"] for d in cal]); ib = np.concatenate([d["Ibar_A"] for d in cal])
    gi, gb = thr_grid(ip), thr_grid(ib)
    out = {}
    for name, kd, grid in (("S0", 0, gi), ("SC", 1, gb)):                 # một ngưỡng chung
        tab = np.repeat(grid[:, None], 2 * NB, 1)
        j, _ = pick(*run(cal, np.full(len(grid), kd), np.zeros(len(grid)), tab, eps, hd)[:2], alpha)
        out[name] = (kd, 0.0, tab[j])
    for name, kd, grid in (("S0dir", 0, gi), ("SCdir", 1, gb)):           # hai ngưỡng theo chiều
        tA, tB = np.meshgrid(grid, grid, indexing="ij")
        tab = np.concatenate([np.repeat(tA.reshape(-1, 1), NB, 1), np.repeat(tB.reshape(-1, 1), NB, 1)], 1)
        j, _ = pick(*run(cal, np.full(len(tab), kd), np.zeros(len(tab)), tab, eps, hd)[:2], alpha)
        out[name] = (kd, 0.0, tab[j])
    best = out["SCdir"][2].copy()                                         # SCtab: coordinate descent từ SCdir
    for _ in range(3):
        for c in range(2 * NB):
            tab = np.repeat(best[None, :], len(gb), 0)
            tab[:, c] = gb
            j, _ = pick(*run(cal, np.ones(len(gb), np.int64), np.zeros(len(gb)), tab, eps, hd)[:2], alpha)
            best = tab[j].copy()
    out["SCtab"] = (1, 0.0, best)
    kinds, mus, tabs = [], [], []                                         # K2: (μ, θ)
    for m in MUS:
        sc = []
        for d in cal:
            for x, pdx in ((d["Ibar_A"], d["pdn_A"]), (-d["Ibar_A"], d["pup_A"])):
                k = x > m
                sc.append((x[k] - m) / np.maximum(pdx[k], 1e-300))
        sc = np.concatenate(sc); sc = sc[np.isfinite(sc)]
        for t in np.r_[np.quantile(sc, np.linspace(0, 0.9999, 60)), np.inf]:
            kinds.append(2); mus.append(m); tabs.append(np.full(2 * NB, t))
    kinds, mus, tabs = np.array(kinds), np.array(mus), np.array(tabs)
    j, _ = pick(*run(cal, kinds, mus, tabs, eps, hd)[:2], alpha)
    out["K2"] = (2, mus[j], tabs[j])
    return out


def ci(x):
    x = np.asarray(x)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - h, x.mean() + h


def load(sc, seeds):
    out = []
    for s in seeds:
        w = simulate(s, sc)
        d = g.decisions(w, sc, {}, sc["eps_ms"])
        d["DA"], d["DB"] = w["A"]["D"], w["B"]["D"]
        out.append(d)
    return out


RULES = ("S0", "SC", "S0dir", "SCdir", "SCtab", "K2")


def begin_results(stage):
    """Lưu số từng seed và tham số đã tune, ngoài log màn hình."""
    path = Path(f"results/go_test/{stage}_seeds.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        csv.writer(f, lineterminator="\n").writerow([
            "stage", "world", "alpha", "hold_down_s", "twin_horizon_s",
            "split", "seed", "rule", "delay_ms", "harm_per_epoch",
            "switches_per_epoch", "mu_ms", "thresholds",
        ])
    return path


def record_results(path, sc, alpha, hd, h_tw, pol, cal, test, test_seeds, extra=()):
    """Không thay đổi tune; xuất cả calibration/test để kiểm gap trong/ngoài mẫu.

    extra chứa (tên, kind, mu, tab, kết quả cal, kết quả test) cho SCtab24.
    Ngưỡng vô hạn được ghi bằng chuỗi, không bằng JSON Infinity không chuẩn.
    """
    entries = []
    for r in RULES:
        kd, m, tab = pol[r]
        args = (np.array([kd]), np.array([m]), tab[None, :], sc["eps_ms"], hd)
        entries.append((r, kd, m, tab, run(cal, *args), run(test, *args)))
    entries.extend(extra)
    with path.open("a", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for r, kd, m, tab, cal_res, test_res in entries:
            thresholds = json.dumps([float(x) if np.isfinite(x) else str(x) for x in tab])
            for split, seeds, res in (("calibration", CAL, cal_res), ("test", test_seeds, test_res)):
                for i, seed in enumerate(seeds):
                    writer.writerow([
                        path.stem.removesuffix("_seeds"), sc["name"], alpha, hd, h_tw,
                        split, seed, r, res[0][i, 0], res[1][i, 0], res[2][i, 0], m, thresholds,
                    ])


def main():
    t0 = time.time()
    output = begin_results("rollout_v2")
    for sc in worlds():
        eps = sc["eps_ms"]
        cal, test = load(sc, CAL), load(sc, TEST)
        ages = np.concatenate([np.r_[d["age_A"], d["age_B"]] for d in test])
        print(f"\n######## {sc['name']} | {time.time() - t0:.0f} s | tuổi bản tin: TB {ages.mean():.1f} s, "
              f"p95 {np.quantile(ages, .95):.1f} s, P(>10 s) {np.mean(ages > 10):.1%}", flush=True)
        for alpha in ALPHAS:
            for hd in HOLDDOWN_S:
                pol = tune(cal, eps, alpha, hd)
                record_results(output, sc, alpha, hd, 1, pol, cal, test, TEST)
                res = {}
                for r in RULES:
                    kd, m, tab = pol[r]
                    res[r] = run(test, np.array([kd]), np.array([m]), tab[None, :], eps, hd)
                dl = {r: res[r][0][:, 0] for r in RULES}
                strongest = min(("S0", "SC", "S0dir", "SCdir", "SCtab"),
                                key=lambda r: pick(*run(cal, np.array([pol[r][0]]), np.array([pol[r][1]]),
                                                        pol[r][2][None, :], eps, hd)[:2], alpha)[1])
                m1, lo1, hi1 = ci(dl["SC"] - dl["K2"])
                m2, lo2, hi2 = ci(dl[strongest] - dl["K2"])
                print(f"  α={alpha:.1%} hold-down {hd:2d} s | delay TB " +
                      " ".join(f"{r} {dl[r].mean():.2f}" for r in RULES) +
                      f" | harm% " + "/".join(f"{100 * res[r][1].mean():.2f}" for r in RULES) +
                      f" | đổi/phút " + "/".join(f"{60 * res[r][2].mean():.2f}" for r in RULES))
                print(f"      SC − K2 = {m1:+.3f} [{lo1:+.3f}; {hi1:+.3f}] ms | baseline mạnh nhất (chọn trên cal) = "
                      f"{strongest}: {strongest} − K2 = {m2:+.3f} [{lo2:+.3f}; {hi2:+.3f}] ms", flush=True)


if __name__ == "__main__":
    main()
