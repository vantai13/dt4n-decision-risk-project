"""f04b (L1.7, bước 2) — Kết luận F2 có sống sót khi "sự thật" là hàng đợi DES thay vì PSA không?

Thiết kế GHÉP CẶP THẾ GIỚI (một thí nghiệm, đổi đúng một thứ):
  cùng quỹ đạo tải OU, cùng gói đến, cùng số đếm ρ̂  =>  dự đoán Î của twin GIỐNG HỆT giữa hai thế giới;
  chỉ delay "thật" D khác: thế giới 'psa' = PSA trên quỹ đạo tải (như F2), thế giới 'des' = hàng đợi M/D/1/K thật.
  Toàn bộ đánh giá (tune luật tĩnh theo J, quỹ đạo tham chiếu, oracle bin, λ theo KKT) dùng NGUYÊN hàm của f02.
Chạy theo thứ tự, commit sau mỗi bước:  --mode validity  →  (ghi prereg)  →  --mode power  →  --mode outcome
Seed: dùng lại danh sách seed của F2 với khoá luồng mới 710–713 (không trùng thế giới nào của F2).
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.signal import lfilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f02_existence_surrogate as f

try:
    from numba import njit
    ENGINE = "numba"
except ImportError:                                     # vẫn chạy được, chỉ chậm hơn
    njit = lambda fn: fn
    ENGINE = "python"

BURN_IN, N_PROBE, N_PSA = 20.0, 251, 11
CELLS = {                                               # chọn theo trần chặt surrogate (f02b), KHÔNG theo gap
    "P1": (f.PRIMARY["P1"], 710),                                          # neo đã khoá
    "P2": (f.PRIMARY["P2"], 711),                                          # tương phản đã khoá
    "K100_r0.85_s10t2": (f.Cell("K100_r0.85_s10t2", 4, 100, 0.85, 0.10, 2.0), 712),
    "K100_r0.95_s03t10": (f.Cell("K100_r0.95_s03t10", 4, 100, 0.95, 0.03, 10.0), 713),
}


@njit
def workload_after(arrivals, service, full):
    """Đệ quy workload (T1 §9): V ngay sau mỗi lần gói đến; drop khi V > (K−1)S."""
    out = np.empty(arrivals.shape[0])
    v, t_prev = 0.0, 0.0
    for i in range(arrivals.shape[0]):
        v = max(0.0, v - (arrivals[i] - t_prev))
        t_prev = arrivals[i]
        if v <= full:
            v += service
        out[i] = v
    return out


def one_path(rng, cell, psa, t_dec):
    """Một link: tải OU chính xác → gói Poisson không đồng nhất → hàng đợi. Trả về ρ̂, D_des, D_psa (ms)."""
    s = cell.s_ms * 1e-3
    n = int(np.ceil((t_dec[-1] + cell.act + cell.hold + 1.0) / f.DT))
    r = np.exp(-f.DT / cell.tau)
    x0 = cell.sigma * rng.standard_normal()
    e = cell.sigma * np.sqrt(1 - r * r) * rng.standard_normal(n - 1)
    rho_raw = cell.rho_bar + np.concatenate([[x0], lfilter([1.0], [1.0, -r], e, zi=[r * x0])[0]])
    rho = np.clip(rho_raw, 0.0, None)
    t_grid = np.arange(n + 1) * f.DT
    cum_lam = np.concatenate([[0.0], np.cumsum(rho / s * f.DT)])
    u = np.cumsum(rng.exponential(1.0, int(cum_lam[-1] * 1.1) + 1000))
    arrivals = np.interp(u[u < cum_lam[-1]], cum_lam, t_grid)
    full = (cell.k - 1) * s
    v_after = workload_after(arrivals, s, full)

    t_m = t_dec - cell.lag
    count = np.searchsorted(arrivals, t_m) - np.searchsorted(arrivals, t_m - cell.win)
    rho_hat = count * s / cell.win

    probes = (t_dec + cell.act)[:, None] + np.linspace(0.0, cell.hold, N_PROBE)[None, :]
    j = np.searchsorted(arrivals, probes, side="right") - 1
    jj = np.maximum(j, 0)
    v = np.where(j >= 0, np.maximum(v_after[jj] - (probes - arrivals[jj]), 0.0), 0.0)
    ok = v <= full
    n_ok = ok.sum(1)
    d_des = np.where(n_ok > 0, np.where(ok, v + s, 0.0).sum(1) / np.maximum(n_ok, 1), cell.k * s) * 1e3

    idx = np.rint(((t_dec + cell.act)[:, None] + np.linspace(0.0, cell.hold, N_PSA)[None, :]) / f.DT).astype(int)
    d_psa = psa.hold(rho[np.minimum(idx, n - 1)], f.trap_w(N_PSA)) * cell.s_ms
    return rho_hat, d_des, d_psa, int((n_ok == 0).sum()), float(np.mean(rho_raw < 0))


def simulate_pair(cell, psa, seed, stream):
    """Một seed: hai path độc lập; trả về (ep_des, ep_psa) có đúng các khoá mà hàm đánh giá của f02 cần."""
    t_dec = BURN_IN + cell.lag + cell.win + cell.hold * np.arange(f.N_EPOCH)
    rng_a, rng_b = (np.random.default_rng(q) for q in np.random.SeedSequence([seed, stream]).spawn(2))
    rh_a, des_a, psa_a, nan_a, clip_a = one_path(rng_a, cell, psa, t_dec)
    rh_b, des_b, psa_b, nan_b, clip_b = one_path(rng_b, cell, psa, t_dec)
    dhat_a, dhat_b = psa.point(rh_a) * cell.s_ms, psa.point(rh_b) * cell.s_ms     # twin plug-in, như F2
    common = dict(Ihat_A=dhat_a - dhat_b, Chat_A=dhat_a, Chat_B=dhat_b, rh_A=rh_a, rh_B=rh_b,
                  clip=max(clip_a, clip_b), n_nan=nan_a + nan_b)
    ep_des = dict(common, D_A=des_a, D_B=des_b, I_A=des_a - des_b)
    ep_psa = dict(common, D_A=psa_a, D_B=psa_b, I_A=psa_a - psa_b)
    return ep_des, ep_psa


def evaluate(pairs, which, cell):
    """Đúng pipeline run_cell của f02 (c = 0), chạy trên thế giới 'des' (0) hoặc 'psa' (1)."""
    eps_ms = f.EPS_OVER_S * cell.s_ms
    cal, test, orc = ([p[which] for p in pairs[k]] for k in ("cal", "test", "orc"))
    tuned = {kd: f.tune_static(cal, kd, 0.0, eps_ms) for kd in ("abs", "rel")}
    kind = min(tuned, key=lambda kd: tuned[kd][1])
    thr = tuned[kind][0]
    ref = lambda ep: f.orient(ep, f.static_run(ep, kind, thr)[1][0])
    oracle = f.BinOracle([ref(ep) for ep in orc], eps_ms)
    lam = f.tune_lambda([oracle.predict(ref(ep))[:2] for ep in cal], 0.0)
    rows, pdn_all, harm_all, contrib, head_terms = [], [], [], [], []
    for ep in test:
        act, cur = f.static_run(ep, kind, thr)
        o = f.orient(ep, cur[0])
        ibar, pdn, _ = oracle.predict(o)
        a_st, a_k2, a_inf = act[0], (ibar - lam * pdn) > 0, ibar > 0      # tĩnh | K2(α) | K2(∞): λ = 0
        I, harm = o["I"], o["I"] < -eps_ms
        rows.append(dict(gain_static=np.mean(a_st * I), gain_k2=np.mean(a_k2 * I), gain_k2_inf=np.mean(a_inf * I),
                         headroom=np.mean(np.maximum(I, 0)), harm_static=np.mean(a_st * harm),
                         harm_k2=np.mean(a_k2 * harm), bias=np.mean(I - ibar), frac_harm_possible=np.mean(harm)))
        pdn_all.append(pdn)
        harm_all.append(harm)
        contrib.append((a_k2.astype(float) - a_st) * I)                  # đóng góp từng epoch vào gap
        head_terms.append(np.maximum(I, 0))                              # tích phân của headroom
    cols = {k: np.array([r[k] for r in rows]) for k in rows[0]}
    cols["gap"] = cols["gain_k2"] - cols["gain_static"]
    return dict(kind=kind, lam=lam, sparse=oracle.frac_sparse, cols=cols, pdn=np.concatenate(pdn_all),
                harm=np.concatenate(harm_all), contrib=contrib, head_terms=head_terms)


def run_cell(name):
    cell, stream = CELLS[name]
    psa = f.PSA(cell.k)
    seeds = dict(cal=f.CAL_SEEDS, test=f.TEST_SEEDS, orc=f.ORACLE_SEEDS)
    pairs = {k: [simulate_pair(cell, psa, s, stream) for s in v] for k, v in seeds.items()}
    for ep_des, ep_psa in pairs["test"]:                 # kiểm thiết kế ghép cặp
        assert np.array_equal(ep_des["Ihat_A"], ep_psa["Ihat_A"])
    n_nan = sum(p[0]["n_nan"] for k in pairs for p in pairs[k])
    clip = max(p[0]["clip"] for k in pairs for p in pairs[k])
    return cell, n_nan, clip, {w: evaluate(pairs, i, cell) for i, w in enumerate(("des", "psa"))}


def bounds(x):
    """Cận dưới và cận trên CI95 (t theo seed) của trung bình x."""
    m, h = f.ci(x)
    return m - h, m + h


def lag1(x):
    x = x - x.mean()
    return float(np.dot(x[:-1], x[1:]) / np.dot(x, x)) if np.dot(x, x) > 0 else 0.0


def seeds_needed(sd, half_width):
    n = 3
    while n < 10_000 and stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n) > half_width:
        n += 1
    return n


def show_validity(name, cell, n_nan, clip, res):
    print(f"\n=== {name}  (K={cell.k}, ρ̄={cell.rho_bar}, σ={cell.sigma}, τ={cell.tau} s) | epoch đầy trọn khoảng giữ: "
          f"{n_nan} | tỉ lệ tải OU < 0: {clip:.1e} | Î giống hệt giữa hai thế giới: OK")
    for w, r in res.items():
        c = r["cols"]
        hs, hk, b, fh = (f.ci(c[k]) for k in ("harm_static", "harm_k2", "bias", "frac_harm_possible"))
        print(f"  [{w}] họ tĩnh '{r['kind']}' | harm tĩnh {hs[0]*100:.2f}±{hs[1]*100:.2f}% | harm K2 {hk[0]*100:.2f}"
              f"±{hk[1]*100:.2f}% | lệch oracle TB(I−Ī) {b[0]:+.2f}±{b[1]:.2f} ms | P(I<−ε) {fh[0]:.3f} | "
              f"ô thưa {r['sparse']:.3f}")
        edges = np.array([0, 0.02, 0.1, 0.3, 0.6, 1.0001])
        k = np.digitize(r["pdn"], edges) - 1
        cells_txt = []
        for i in range(len(edges) - 1):
            sel = k == i
            if sel.sum() >= 30:
                cells_txt.append(f"{r['pdn'][sel].mean():.3f}→{r['harm'][sel].mean():.3f}")
        print(f"       độ tin cậy p− (dự đoán→thực, gộp seed test): {'  '.join(cells_txt)}")


def show_power(name, res):
    for w, r in res.items():
        sd = r["cols"]["gap"].std(ddof=1)
        acf_c = np.mean([lag1(x) for x in r["contrib"]])
        acf_h = np.mean([lag1(x) for x in r["head_terms"]])
        print(f"  {name:18s} [{w}] sd_seed(gap) {sd:.3f} ms | seed cần cho ±{f.M_SESOI_MS/2:.2f} ms: "
              f"{seeds_needed(sd, f.M_SESOI_MS / 2):4d} | cho ±1 ms: {seeds_needed(sd, 1.0):4d} | "
              f"ACF lag-1: đóng góp gap {acf_c:+.3f}, (I)⁺ {acf_h:+.3f}")


def show_outcome(name, res, store):
    print(f"\n=== {name}")
    print(f"  {'thế giới':8s} {'tĩnh':>7s} {'K2(α)':>7s} {'K2(∞)':>7s} {'headroom':>8s} | {'thích nghi':>10s} "
          f"{'an toàn':>8s} {'thông tin':>9s} | {'gap ± CI':>15s} | phán quyết SESOI")
    terms = {}
    for w, r in res.items():
        c = r["cols"]
        t = dict(adapt=c["gap"], safety=c["gain_k2_inf"] - c["gain_k2"], info=c["headroom"] - c["gain_k2_inf"])
        terms[w] = t
        g = f.ci(c["gap"])
        lo_abs, hi_abs = bounds(c["gap"] - f.M_SESOI_MS)                  # D_abs = gap − m
        lo_rel, hi_rel = bounds(c["gap"] - f.R_SESOI * c["headroom"])     # D_rel = gap − r·headroom
        verdict = ("CÓ Ý NGHĨA" if lo_abs > 0 and lo_rel > 0 else
                   "KHÔNG ĐÁNG KỂ" if hi_abs < 0 or hi_rel < 0 else "CHƯA KẾT LUẬN")
        print(f"  {w:8s} {c['gain_static'].mean():7.3f} {c['gain_k2'].mean():7.3f} {c['gain_k2_inf'].mean():7.3f} "
              f"{c['headroom'].mean():8.3f} | {t['adapt'].mean():10.3f} {t['safety'].mean():8.3f} "
              f"{t['info'].mean():9.3f} | {g[0]:+7.3f} ± {g[1]:.3f} | {verdict}")
        store[f"{name}/{w}"] = {k: f.ci(v) for k, v in {**c, **t}.items()} | dict(verdict=verdict, lam=r["lam"],
                                                                                 kind=r["kind"])
    for k in ("adapt", "safety", "info"):
        d = f.ci(terms["des"][k] - terms["psa"][k])
        print(f"    DES − PSA ({k:6s}, ghép cặp theo seed): {d[0]:+.3f} ± {d[1]:.3f} ms")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("validity", "power", "outcome"), required=True)
    mode, t0, store = ap.parse_args().mode, time.time(), {}
    print(f"f04b | engine {ENGINE} | mode {mode} | {f.N_EPOCH} epoch/seed | "
          f"seed cal {len(f.CAL_SEEDS)}, test {len(f.TEST_SEEDS)}, oracle {len(f.ORACLE_SEEDS)}")
    for name in CELLS:
        cell, n_nan, clip, res = run_cell(name)
        if mode == "validity":
            show_validity(name, cell, n_nan, clip, res)
        elif mode == "power":
            show_power(name, res)
        else:
            show_outcome(name, res, store)
    if mode == "outcome":
        out = Path(__file__).resolve().parent / "results" / "f04b"
        out.mkdir(parents=True, exist_ok=True)
        (out / "f04b_results.json").write_text(json.dumps(store, indent=1, ensure_ascii=False, default=float),
                                               encoding="utf-8")
    print(f"Thời gian {time.time() - t0:.0f} s", file=sys.stderr)   # stderr: stdout phải trùng byte khi chạy lại
