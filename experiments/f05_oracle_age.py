"""f05 (L1.8: F5 + tuổi dao động) — Phán quyết "không đáng kể" của f04b có phải do oracle yếu, và có sống sót
khi tuổi dao động không?

Chỉ thế giới DES. Hai ô có trần chặt DES (headroom − gain tĩnh) > m trong f04b: P2 và K100_r0.95_s03t10 —
chỉ ở đó kết luận mới CÓ THỂ đổi; ở các ô khác trần < m nên kết luận đã định sẵn.
  A0 = tuổi cố định (đúng thế giới f04b, cùng seed, cùng khoá luồng 711/713).
  A1 = tuổi dao động: lag mỗi epoch ~ U[lag − T/2, lag + T/2), T = T_poll = 0,5 s (cùng tuổi TB với A0);
       dùng CHUNG tải và gói đến với A0 (CRN), chỉ vị trí cửa sổ đo đổi.
Oracle (bin dọc quỹ đạo tham chiếu tĩnh): F = số đếm (ρ̂_cur, ρ̂_alt); Q = workload V cuối cửa sổ (twin "thấy
hàng đợi", cùng tuổi); FZ = số đếm + tuổi. "x2" = gấp đôi dữ liệu oracle (thêm lô seed với khoá luồng +100).
Luật: S0 = tĩnh plug-in (tham chiếu) | K2 = Ī − λp− > 0 | SC = Ī > H ("tĩnh trên tâm tốt") | K2(∞) = Ī > 0.
  gap = K2 − S0 = (SC − S0: giá trị của TÂM tốt hơn) + (K2 − SC: giá trị THUẦN của bất định).
Chạy: --mode validity  →  (tác giả tự viết prereg, commit)  →  --mode outcome
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f02_existence_surrogate as f
import f04b_des_gap as g

CELLS = ("P2", "K100_r0.95_s03t10")
F04B_JSON = Path(__file__).resolve().parent / "results" / "f04b" / "f04b_results.json"
T_POLL, EXTRA, AGE_KEY = 0.5, 100, 99
SPECS = {                                       # tên: (đặc trưng, số bin mỗi chiều đếm/queue, số bin tuổi, gấp đôi dữ liệu)
    "A0": {"F10": ("F", 10, 0, False), "F20": ("F", 20, 0, False), "F20x2": ("F", 20, 0, True),
           "F40x2": ("F", 40, 0, True), "Q20x2": ("Q", 20, 0, True)},
    "A1": {"F20x2": ("F", 20, 0, True), "FZ10x5": ("FZ", 10, 5, True), "FZ20x3": ("FZ", 20, 3, True)},
}


def one_path_state(rng, cell, t_dec, lags):
    """Giống g.one_path (CÙNG thứ tự rút số ngẫu nhiên), nhưng cửa sổ đo lệch theo lags từng epoch và trả thêm
    workload V ở cuối cửa sổ (ms). Không tính PSA."""
    s = cell.s_ms * 1e-3
    n = int(np.ceil((t_dec[-1] + cell.act + cell.hold + 1.0) / f.DT))
    r = np.exp(-f.DT / cell.tau)
    x0 = cell.sigma * rng.standard_normal()
    e = cell.sigma * np.sqrt(1 - r * r) * rng.standard_normal(n - 1)
    rho = np.clip(cell.rho_bar + np.concatenate([[x0], lfilter([1.0], [1.0, -r], e, zi=[r * x0])[0]]), 0.0, None)
    t_grid = np.arange(n + 1) * f.DT
    cum_lam = np.concatenate([[0.0], np.cumsum(rho / s * f.DT)])
    u = np.cumsum(rng.exponential(1.0, int(cum_lam[-1] * 1.1) + 1000))
    arrivals = np.interp(u[u < cum_lam[-1]], cum_lam, t_grid)
    full = (cell.k - 1) * s
    v_after = g.workload_after(arrivals, s, full)

    def workload_at(ts):
        j = np.searchsorted(arrivals, ts, side="right") - 1
        jj = np.maximum(j, 0)
        return np.where(j >= 0, np.maximum(v_after[jj] - (ts - arrivals[jj]), 0.0), 0.0)

    t_m = t_dec - lags
    count = np.searchsorted(arrivals, t_m) - np.searchsorted(arrivals, t_m - cell.win)
    probes = (t_dec + cell.act)[:, None] + np.linspace(0.0, cell.hold, g.N_PROBE)[None, :]
    v = workload_at(probes)
    ok = v <= full
    n_ok = ok.sum(1)
    d_des = np.where(n_ok > 0, np.where(ok, v + s, 0.0).sum(1) / np.maximum(n_ok, 1), cell.k * s) * 1e3
    return count * s / cell.win, d_des, workload_at(t_m) * 1e3


def simulate(cell, psa, seed, stream, jitter):
    t_dec = g.BURN_IN + cell.lag + cell.win + cell.hold * np.arange(f.N_EPOCH)
    lags = np.full(f.N_EPOCH, cell.lag)
    if jitter:                                          # luồng riêng: không làm xê dịch tải/gói đến (CRN)
        u = np.random.default_rng(np.random.SeedSequence([seed, stream, AGE_KEY])).random(f.N_EPOCH)
        lags = cell.lag - T_POLL / 2 + T_POLL * u
    rng_a, rng_b = (np.random.default_rng(q) for q in np.random.SeedSequence([seed, stream]).spawn(2))
    rh_a, d_a, v_a = one_path_state(rng_a, cell, t_dec, lags)
    rh_b, d_b, v_b = one_path_state(rng_b, cell, t_dec, lags)
    dhat_a, dhat_b = psa.point(rh_a) * cell.s_ms, psa.point(rh_b) * cell.s_ms
    return dict(D_A=d_a, D_B=d_b, I_A=d_a - d_b, Ihat_A=dhat_a - dhat_b, Chat_A=dhat_a, Chat_B=dhat_b,
                rh_A=rh_a, rh_B=rh_b, v_A=v_a, v_B=v_b, age=lags)


def orient_ext(ep, cur_a):
    o = f.orient(ep, cur_a)
    o.update(v_cur=np.where(cur_a, ep["v_A"], ep["v_B"]), v_alt=np.where(cur_a, ep["v_B"], ep["v_A"]), age=ep["age"])
    return o


def features(kind, o):
    if kind == "Q":
        return [o["v_cur"], o["v_alt"]]
    return [o["rh_cur"], o["rh_alt"]] + ([o["age"]] if kind == "FZ" else [])


class GridOracle:
    """Oracle bin N chiều. Cặp (cur, alt) dùng CHUNG cạnh phân vị như f02.BinOracle; tuổi có cạnh riêng.
    Ô có < 30 mẫu dùng giá trị toàn cục (báo tỉ lệ, không giấu)."""

    def __init__(self, orients, kind, n_bin, n_age, eps_ms, min_count=30):
        feats = [np.concatenate(col) for col in zip(*[features(kind, o) for o in orients])]
        I = np.concatenate([o["I"] for o in orients])
        pair = np.unique(np.quantile(np.concatenate(feats[:2]), np.linspace(0, 1, n_bin + 1)))
        self.edges = [pair, pair] + ([np.unique(np.quantile(feats[2], np.linspace(0, 1, n_age + 1)))] if n_age else [])
        self.kind, self.shape = kind, [len(e) - 1 for e in self.edges]
        idx = self._flat(feats)
        n = int(np.prod(self.shape))
        cnt = np.bincount(idx, minlength=n).astype(float)
        ok = cnt >= min_count
        self.ibar = np.where(ok, np.bincount(idx, I, n) / np.maximum(cnt, 1), I.mean())
        self.pdn = np.where(ok, np.bincount(idx, (I < -eps_ms).astype(float), n) / np.maximum(cnt, 1),
                            (I < -eps_ms).mean())
        self.frac_sparse = float(np.mean(~ok[idx]))

    def _flat(self, feats):
        idx = np.zeros(len(feats[0]), dtype=np.int64)
        for x, e, nb in zip(feats, self.edges, self.shape):
            idx = idx * nb + np.clip(np.searchsorted(e, x, side="right") - 1, 0, nb - 1)
        return idx

    def predict(self, o):
        k = self._flat(features(self.kind, o))
        return self.ibar[k], self.pdn[k]


def tune_center(preds):
    """Ngưỡng H ≥ 0 nhỏ nhất để luật 'Ī > H' có harm DỰ ĐOÁN ≤ α (cùng tiêu chí với λ của K2)."""
    harm = lambda h: np.mean([np.mean((ib > h) * pd) for ib, pd in preds])
    if harm(0.0) <= f.ALPHA:
        return 0.0
    lo, hi = 0.0, 1.0
    while harm(hi) > f.ALPHA:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if harm(mid) <= f.ALPHA else (mid, hi)
    return hi


def evaluate(cell, regime, eps_ms, eps):
    cal, test, orc = eps["cal"], eps["test"], eps["orc"]
    tuned = {kd: f.tune_static(cal, kd, 0.0, eps_ms) for kd in ("abs", "rel")}
    kind = min(tuned, key=lambda kd: tuned[kd][1])
    thr = tuned[kind][0]
    ref = lambda ep: orient_ext(ep, f.static_run(ep, kind, thr)[1][0])
    r_orc, r_cal = [ref(ep) for ep in orc], [ref(ep) for ep in cal]
    r_test = []
    for ep in test:
        act, cur = f.static_run(ep, kind, thr)
        r_test.append((act[0], orient_ext(ep, cur[0])))
    res = dict(kind=kind, S0=np.array([np.mean(a * o["I"]) for a, o in r_test]),
               headroom=np.array([np.mean(np.maximum(o["I"], 0)) for _, o in r_test]), oracles={})
    for name, (fk, nb, na, x2) in SPECS[regime].items():
        oracle = GridOracle(r_orc if x2 else r_orc[:len(f.ORACLE_SEEDS)], fk, nb, na, eps_ms)
        pc = [oracle.predict(o) for o in r_cal]
        lam, h = f.tune_lambda(pc, 0.0), tune_center(pc)
        cols = {k: [] for k in ("K2", "SC", "INF", "harm_K2", "harm_SC", "bias")}
        for a_st, o in r_test:
            ib, pd = oracle.predict(o)
            I, harm = o["I"], o["I"] < -eps_ms
            k2, sc = (ib - lam * pd) > 0, ib > h
            for key, val in (("K2", k2 * I), ("SC", sc * I), ("INF", (ib > 0) * I), ("harm_K2", k2 * harm),
                             ("harm_SC", sc * harm), ("bias", I - ib)):
                cols[key].append(np.mean(val))
        res["oracles"][name] = dict(lam=lam, H=h, sparse=oracle.frac_sparse, n_cells=int(np.prod(oracle.shape)),
                                    **{k: np.array(v) for k, v in cols.items()})
    res["r_test"], res["r_orc_first"] = r_test, r_orc[:len(f.ORACLE_SEEDS)]
    return res


def run_cell(name):
    cell, stream = g.CELLS[name]
    psa = f.PSA(cell.k)
    eps_ms = f.EPS_OVER_S * cell.s_ms
    out = {}
    for regime, jitter in (("A0", False), ("A1", True)):
        sim = lambda seeds, st: [simulate(cell, psa, s, st, jitter) for s in seeds]
        eps = dict(cal=sim(f.CAL_SEEDS, stream), test=sim(f.TEST_SEEDS, stream),
                   orc=sim(f.ORACLE_SEEDS, stream) + sim(f.ORACLE_SEEDS, stream + EXTRA))
        out[regime] = evaluate(cell, regime, eps_ms, eps)
        if regime == "A0":                             # ba phép kiểm neo: cùng thế giới, cùng oracle, cùng gap
            ref_des = g.simulate_pair(cell, psa, f.TEST_SEEDS[0], stream)[0]
            out["world_same"] = all(np.array_equal(ref_des[k], eps["test"][0][k]) for k in ("rh_A", "D_A", "rh_B", "D_B"))
            r = out["A0"]
            old = f.BinOracle(r["r_orc_first"], eps_ms)
            new = GridOracle(r["r_orc_first"], "F", 20, 0, eps_ms)
            out["oracle_same"] = all(np.array_equal(a, b) for _, o in r["r_test"]
                                     for a, b in zip(old.predict(o)[:2], new.predict(o)))
            prev = json.loads(F04B_JSON.read_text(encoding="utf-8"))[f"{name}/des"]["gap"]
            now = f.ci(r["oracles"]["F20"]["K2"] - r["S0"])
            out["gap_same"] = bool(np.allclose(now, prev, rtol=0, atol=1e-9))
        lags = np.concatenate([ep["age"] for ep in eps["test"]])
        out[regime]["lag_range"] = (float(lags.min()), float(lags.mean()), float(lags.max()))
    return cell, out


def ci_txt(x, scale=1.0, digits=3):
    m, h = f.ci(np.asarray(x) * scale)
    return f"{m:+.{digits}f}±{h:.{digits}f}"


def show_validity(name, cell, out):
    print(f"\n=== {name} | A0 trùng f04b — thế giới: {out['world_same']}, oracle F20 (lớp mới vs f02.BinOracle): "
          f"{out['oracle_same']}, gap F20: {out['gap_same']}")
    for regime in ("A0", "A1"):
        r = out[regime]
        lo, mean, hi = r["lag_range"]
        print(f"  [{regime}] lag ∈ [{lo:.3f}; {hi:.3f}] s, TB {mean:.3f} s | họ tĩnh '{r['kind']}'")
        for oname, o in r["oracles"].items():
            print(f"     {oname:7s} ô {o['n_cells']:5d} | thưa {o['sparse']:.3f} | harm K2 {ci_txt(o['harm_K2'], 100, 2)}% "
                  f"| harm SC {ci_txt(o['harm_SC'], 100, 2)}% | lệch TB(I−Ī) {ci_txt(o['bias'], 1, 2)} ms")


def verdict(gap, head):
    lo_a, hi_a = g.bounds(gap - f.M_SESOI_MS)
    lo_r, hi_r = g.bounds(gap - f.R_SESOI * head)
    return "CÓ Ý NGHĨA" if lo_a > 0 and lo_r > 0 else "KHÔNG ĐÁNG KỂ" if hi_a < 0 or hi_r < 0 else "CHƯA KẾT LUẬN"


def show_outcome(name, out, store):
    for regime in ("A0", "A1"):
        r = out[regime]
        print(f"\n=== {name} [{regime}] headroom {ci_txt(r['headroom'])} ms | tĩnh plug-in S0 {ci_txt(r['S0'])} ms")
        print(f"  {'oracle':7s} {'gap = K2 − S0':>16s} {'tâm: SC − S0':>16s} {'thuần: K2 − SC':>16s} "
              f"{'K2(∞) − S0':>16s} | phán quyết SESOI")
        for oname, o in r["oracles"].items():
            gap = o["K2"] - r["S0"]
            v = verdict(gap, r["headroom"])
            print(f"  {oname:7s} {ci_txt(gap):>16s} {ci_txt(o['SC'] - r['S0']):>16s} {ci_txt(o['K2'] - o['SC']):>16s} "
                  f"{ci_txt(o['INF'] - r['S0']):>16s} | {v}")
            store[f"{name}/{regime}/{oname}"] = dict(gap=f.ci(gap), center=f.ci(o["SC"] - r["S0"]),
                                                     pure=f.ci(o["K2"] - o["SC"]), inf=f.ci(o["INF"] - r["S0"]),
                                                     verdict=v, lam=o["lam"], H=o["H"])
    a0, a1 = out["A0"], out["A1"]
    base = a0["oracles"]["F20"]["K2"] - a0["S0"]
    spread = max(abs(np.mean(a0["oracles"][k]["K2"] - a0["S0"]) - np.mean(base)) for k in ("F10", "F20x2", "F40x2"))
    print(f"  Ổn định oracle đếm (A0): max |gap − gap_F20| = {spread:.3f} ms  (tiêu chí DP0: < m/2 = "
          f"{f.M_SESOI_MS / 2:.2f} ms)")
    d_gap = (a1["oracles"]["F20x2"]["K2"] - a1["S0"]) - (a0["oracles"]["F20x2"]["K2"] - a0["S0"])
    print(f"  A1 − A0 (ghép cặp, CRN): gain tĩnh S0 {ci_txt(a1['S0'] - a0['S0'])} ms | gap F20x2 {ci_txt(d_gap)} ms")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("validity", "outcome"), required=True)
    mode, t0, store = ap.parse_args().mode, time.time(), {}
    print(f"f05 | engine {g.ENGINE} | mode {mode} | ô {', '.join(CELLS)} | T_poll {T_POLL} s | "
          f"oracle seed {len(f.ORACLE_SEEDS)} (×2 với khoá +{EXTRA})")
    for name in CELLS:
        cell, out = run_cell(name)
        if mode == "validity":
            show_validity(name, cell, out)
        else:
            show_outcome(name, out, store)
    if mode == "outcome":
        path = Path(__file__).resolve().parent / "results" / "f05"
        path.mkdir(parents=True, exist_ok=True)
        (path / "f05_results.json").write_text(json.dumps(store, indent=1, ensure_ascii=False, default=float),
                                               encoding="utf-8")
    print(f"Thời gian {time.time() - t0:.0f} s", file=sys.stderr)
