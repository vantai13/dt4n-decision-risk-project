"""f05c (P1v2/L1.6) — κ và luật bậc hai trên dữ liệu DES ĐÃ CÓ. KHÁM PHÁ / POST HOC, không phải bằng chứng xác nhận.

Định nghĩa khoá TRƯỚC khi tính (dòng log L1.6, D1–D11):
  D1 thế giới + seed = f05 (A0: 4 ô f04b; A1: P2, K100_r0.95_s03t10). Không seed mới.
  D2 oracle = F20x2 của f05 + sd trong ô (s). D3 luật S0/SC/K2 đúng f05; thêm S_Î* (ngưỡng trên Î, abs|rel, tune trên cal
     bằng harm DỰ ĐOÁN của oracle — cùng quy trình với SC; chọn họ theo gain dự đoán trên cal).
  D4 κ̂_pure: 20 bin phân vị của Ī, detrend tuyến tính log s trong bin, sd có trọng số, gộp epoch test.
  D5 sd_log_s_cond: 20 bin của Î, không detrend (chỉ số đã đăng ký, phụ).
  D6 sàn bin: cùng ước lượng trên log s đã làm trơn (TB 50 bin, nội suy tuyến tính); sàn lấy mẫu: TB 1/√(2(n_ô − 1)).
  D7 biên: t₀ = ngưỡng SC; λ vận hành của K2; f₀ = tỉ lệ |Ī − t₀| < h chia 2h (h = 1 ms; độ nhạy 0,5; 2);
     OLS chung trong |Ī − t₀| < 2 ms (độ nhạy 1; 4): u ~ c + a′(Ī − t₀) + β·r, r = phần dư D4; κ_b = sd(r trong dải);
     dự đoán = f₀β²κ_b²/(2a′) nếu a′ > 0, ngược lại đánh dấu đường (ii).
  D8 quan sát = K2 − SC theo seed test, TB ± CI t. D9 đường (ii): số lần TB u giảm qua 20 bin Ī trong Ī > 0.
  D10 đối chứng: tái lập f05 (F20x2: thuần, λ, H) cho P2 và K100_r0.95_s03t10; λ = 0 ⇒ thuần = 0 đúng.
Provenance: Claude (AI) soạn theo L1.6; tác giả chạy lại, kiểm.
Chạy: python experiments/f05c_kappa_des.py | tee experiments/results/f05c_kappa_des_output.txt  (≈ 2,5 phút)
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import f02_existence_surrogate as f
import f04b_des_gap as g
import f05_oracle_age as q

REGIMES = [("P1", "A0"), ("P2", "A0"), ("K100_r0.85_s10t2", "A0"), ("K100_r0.95_s03t10", "A0"),
           ("P2", "A1"), ("K100_r0.95_s03t10", "A1")]
F05_JSON = HERE / "results" / "f05" / "f05_results.json"
OUT = HERE / "results" / "f05c"


class SdGridOracle(q.GridOracle):
    """GridOracle F của f05 + độ lệch chuẩn của I trong ô và số mẫu mỗi ô (để tính sàn lấy mẫu)."""

    def __init__(self, orients, eps_ms, n_bin=20, min_count=30):
        super().__init__(orients, "F", n_bin, 0, eps_ms, min_count)
        feats = [np.concatenate(col) for col in zip(*[q.features("F", o) for o in orients])]
        I = np.concatenate([o["I"] for o in orients])
        idx = self._flat(feats)
        n = int(np.prod(self.shape))
        cnt = np.bincount(idx, minlength=n).astype(float)
        ok = cnt >= min_count
        mean = np.bincount(idx, I, n) / np.maximum(cnt, 1)
        var = np.bincount(idx, I * I, n) / np.maximum(cnt, 1) - mean**2
        self.sd = np.where(ok, np.sqrt(np.maximum(var, 1e-12)), I.std())
        self.count = np.where(ok, cnt, len(I))

    def predict_all(self, o):
        k = self._flat(q.features("F", o))
        return self.ibar[k], self.pdn[k], self.sd[k], self.count[k]


def edges_of(x, n_bin):
    e = np.unique(np.quantile(x, np.linspace(0, 1, n_bin + 1)))
    return e, np.clip(np.searchsorted(e, x, side="right") - 1, 0, len(e) - 2)


def kappa(key, log_s, n_bin=20, detrend=True):
    """(κ, phần dư r). detrend=True: D4; detrend=False: D5."""
    _, b = edges_of(key, n_bin)
    r, groups = np.zeros_like(log_s), []
    for k in np.unique(b):
        m = b == k
        y = log_s[m] - log_s[m].mean()
        if detrend and m.sum() >= 3 and np.ptp(key[m]) > 0:
            x = np.vstack([np.ones(m.sum()), key[m]]).T
            y = log_s[m] - x @ np.linalg.lstsq(x, log_s[m], rcond=None)[0]
        r[m] = y
        if m.sum() >= 2:
            groups.append((y.std(), m.sum()))
    return float(np.average([g_[0] for g_ in groups], weights=[g_[1] for g_ in groups])), r


def smooth_log_s(key, log_s, n_bin=50):
    """D6: log s làm trơn = nội suy tuyến tính giữa trung bình của 50 bin phân vị."""
    _, b = edges_of(key, n_bin)
    xs = np.array([key[b == k].mean() for k in np.unique(b)])
    ys = np.array([log_s[b == k].mean() for k in np.unique(b)])
    return np.interp(key, xs, ys)


def tune_threshold(keys, preds):
    """Ngưỡng H ≥ 0 nhỏ nhất trên `keys` để harm DỰ ĐOÁN ≤ α (đúng tiêu chí của q.tune_center)."""
    harm = lambda h: np.mean([np.mean((k > h) * pd) for k, (_, pd) in zip(keys, preds)])
    if harm(0.0) <= f.ALPHA:
        return 0.0
    lo, hi = 0.0, 1.0
    while harm(hi) > f.ALPHA:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if harm(mid) <= f.ALPHA else (mid, hi)
    return hi


def run(name, regime):
    cell, stream = g.CELLS[name]
    psa = f.PSA(cell.k)
    eps_ms = f.EPS_OVER_S * cell.s_ms
    jitter = regime == "A1"
    sim = lambda seeds, st: [q.simulate(cell, psa, s, st, jitter) for s in seeds]
    eps = dict(cal=sim(f.CAL_SEEDS, stream), test=sim(f.TEST_SEEDS, stream),
               orc=sim(f.ORACLE_SEEDS, stream) + sim(f.ORACLE_SEEDS, stream + q.EXTRA))
    if regime == "A0":                                      # thế giới trùng f04b (như phép kiểm của f05)
        ref = g.simulate_pair(cell, psa, f.TEST_SEEDS[0], stream)[0]
        assert all(np.array_equal(ref[k], eps["test"][0][k]) for k in ("rh_A", "D_A", "rh_B", "D_B"))

    tuned = {kd: f.tune_static(eps["cal"], kd, 0.0, eps_ms) for kd in ("abs", "rel")}
    kind = min(tuned, key=lambda kd: tuned[kd][1])
    thr = tuned[kind][0]
    orient = lambda ep: q.orient_ext(ep, f.static_run(ep, kind, thr)[1][0])
    r_orc, r_cal = [orient(ep) for ep in eps["orc"]], [orient(ep) for ep in eps["cal"]]
    oracle = SdGridOracle(r_orc, eps_ms)
    pc = [oracle.predict(o) for o in r_cal]
    lam, h_c = f.tune_lambda(pc, 0.0), q.tune_center(pc)

    chat = lambda o: psa.point(o["rh_cur"]) * cell.s_ms
    keys = {"abs": lambda o: o["Ihat"], "rel": lambda o: o["Ihat"] / chat(o)}
    star = {}
    for kd, key in keys.items():
        h = tune_threshold([key(o) for o in r_cal], pc)
        star[kd] = (h, np.mean([np.mean((key(o) > h) * ib) for o, (ib, _) in zip(r_cal, pc)]))
    kind_star = max(star, key=lambda kd: star[kd][1])

    per_seed = {k: [] for k in ("S0", "SC", "K2", "Sstar", "head", "disagree")}
    pool = {k: [] for k in ("ibar", "ihat", "s", "n", "u")}
    for ep in eps["test"]:
        act, cur = f.static_run(ep, kind, thr)
        o = q.orient_ext(ep, cur[0])
        ib, pd, sd, n = oracle.predict_all(o)
        I = o["I"]
        k2, sc = (ib - lam * pd) > 0, ib > h_c
        s_star = keys[kind_star](o) > star[kind_star][0]
        for key, a in (("S0", act[0]), ("SC", sc), ("K2", k2), ("Sstar", s_star)):
            per_seed[key].append(np.mean(a * I))
        per_seed["head"].append(np.mean(np.maximum(I, 0)))
        per_seed["disagree"].append(np.mean(k2 != sc))
        for key, v in (("ibar", ib), ("ihat", o["Ihat"]), ("s", sd), ("n", n), ("u", ib - lam * pd)):
            pool[key].append(v)
    per_seed = {k: np.array(v) for k, v in per_seed.items()}
    pool = {k: np.concatenate(v) for k, v in pool.items()}
    return dict(cell=cell, kind=kind, lam=lam, t0=h_c, sparse=oracle.frac_sparse, kind_star=kind_star,
                per_seed=per_seed, pool=pool)


def analyse(res):
    p, ps = res["pool"], res["per_seed"]
    ibar, log_s, u, t0 = p["ibar"], np.log(p["s"]), p["u"], res["t0"]
    k_pure, r = kappa(ibar, log_s)
    k_hat, _ = kappa(p["ihat"], log_s, detrend=False)
    floor_b, _ = kappa(ibar, smooth_log_s(ibar, log_s))
    floor_s = float(np.mean(1 / np.sqrt(2 * np.maximum(p["n"] - 1, 1))))
    out = dict(kind=res["kind"], lam=res["lam"], t0=t0, sparse=res["sparse"], k_pure=k_pure, k_hat=k_hat,
               floor_b=floor_b, floor_s=floor_s, k_excess=float(np.sqrt(max(k_pure**2 - floor_b**2 - floor_s**2, 0))),
               f0={h: float(np.mean(np.abs(ibar - t0) < h) / (2 * h)) for h in (0.5, 1.0, 2.0)})
    law = {}
    for h_r in (1.0, 2.0, 4.0):
        band = np.abs(ibar - t0) < h_r
        n_cells = len(np.unique(np.round(ibar[band], 9)))
        if band.sum() < 30 or n_cells < 3:
            law[h_r] = dict(n=int(band.sum()), cells=n_cells, a1=np.nan, beta=np.nan, k_b=np.nan, pred=np.nan)
            continue
        x = np.vstack([np.ones(band.sum()), ibar[band] - t0, r[band]]).T
        _, a1, beta = np.linalg.lstsq(x, u[band], rcond=None)[0]
        k_b = float(r[band].std())
        pred = out["f0"][1.0] * beta**2 * k_b**2 / (2 * a1) if a1 > 0 else np.nan
        law[h_r] = dict(n=int(band.sum()), cells=n_cells, a1=float(a1), beta=float(beta), k_b=k_b, pred=float(pred))
    out["law"] = law
    pos = ibar > 0
    _, b = edges_of(ibar[pos], 20)
    means = np.array([u[pos][b == k].mean() for k in np.unique(b)])
    out["u_decreases"] = int(np.sum(np.diff(means) < 0))
    ci = lambda x: f.ci(x)
    out["pure"] = ci(ps["K2"] - ps["SC"])
    out["center_f05"] = ci(ps["SC"] - ps["S0"])
    out["center_clean"] = ci(ps["SC"] - ps["Sstar"])
    out["procedure"] = ci(ps["Sstar"] - ps["S0"])
    out["head"] = float(ps["head"].mean())
    out["disagree"] = float(ps["disagree"].mean())
    out["kind_star"] = res["kind_star"]
    return out


def check_f05(name, regime, a):
    """D10: tái lập thuần, λ, H của f05 (F20x2) cho hai ô f05 đã chạy."""
    key = f"{name}/{regime}/F20x2"
    ref = json.loads(F05_JSON.read_text(encoding="utf-8")).get(key)
    if ref is None:
        return "—"
    ok = (np.allclose(a["pure"], ref["pure"], atol=1e-9) and np.isclose(a["lam"], ref["lam"])
          and np.isclose(a["t0"], ref["H"]))
    assert ok, f"{key}: không tái lập được f05"
    return "khớp f05"


if __name__ == "__main__":
    t_start, store = time.time(), {}
    print("f05c | KHÁM PHÁ post hoc | seed cũ của f05 | oracle F20x2 + sd trong ô")
    for name, regime in REGIMES:
        a = analyse(run(name, regime))
        a["check"] = check_f05(name, regime, a)
        if a["lam"] == 0:
            assert a["pure"][0] == 0 and a["pure"][1] == 0, "λ = 0 ⇒ K2 ≡ SC"
        store[f"{name}/{regime}"] = a
        print(f"{name}/{regime} xong ({a['check']})", file=sys.stderr)

    print("\nBẢNG 1 — κ và các sàn (gộp 8 seed test)")
    print(f"{'ô/chế độ':22s} {'họ':>4s} {'ô thưa':>7s} | {'κ̂_pure':>7s} {'sàn bin':>8s} {'sàn mẫu':>8s} {'κ vượt sàn':>10s}"
          f" | {'sd_log_s_cond (Î)':>17s}")
    for k, a in store.items():
        print(f"{k:22s} {a['kind']:>4s} {a['sparse']:7.3f} | {a['k_pure']:7.3f} {a['floor_b']:8.3f} {a['floor_s']:8.3f} "
              f"{a['k_excess']:10.3f} | {a['k_hat']:17.3f}")

    print("\nBẢNG 2 — luật bậc hai tại biên (dải OLS 2 ms; f₀ với h = 1 ms)")
    print(f"{'ô/chế độ':22s} {'λ':>7s} {'t₀':>7s} {'f₀':>6s} | {'n dải':>6s} {'ô':>4s} {'a′':>6s} {'β':>8s} {'κ_b':>6s} | "
          f"{'dự đoán':>8s} {'quan sát K2 − SC':>17s} {'tỉ lệ':>6s} {'K2≠SC':>6s} {'u giảm':>6s}")
    for k, a in store.items():
        L = a["law"][2.0]
        pred = "  λ = 0 " if a["lam"] == 0 else ("đường ii" if np.isnan(L["pred"]) else f"{L['pred']:8.3f}")
        print(f"{k:22s} {a['lam']:7.2f} {a['t0']:7.2f} {a['f0'][1.0]:6.3f} | {L['n']:6d} {L['cells']:4d} "
              f"{L['a1']:6.2f} {L['beta']:8.2f} {L['k_b']:6.3f} | {pred:>8s} {a['pure'][0]:+8.3f} ± {a['pure'][1]:.3f} "
              f"{a['pure'][0] / a['head']:6.2%} {a['disagree']:6.2%} {a['u_decreases']:6d}")
    print("  Độ nhạy dự đoán (ms) theo dải OLS 1 / 2 / 4 ms và f₀ theo h = 0,5 / 1 / 2 ms:")
    for k, a in store.items():
        preds = " / ".join("—" if np.isnan(a["law"][h]["pred"]) else f"{a['law'][h]['pred']:.3f}" for h in (1.0, 2.0, 4.0))
        f0s = " / ".join(f"{a['f0'][h]:.3f}" for h in (0.5, 1.0, 2.0))
        print(f"    {k:22s} dự đoán {preds} | f₀ {f0s}")

    print("\nBẢNG 3 — tách tâm khỏi quy trình tune (L1.3 §10.6)")
    print(f"{'ô/chế độ':22s} | {'SC − S0 (f05)':>16s} = {'tâm sạch SC − S_Î*':>18s} + {'quy trình S_Î* − S0':>19s} | họ S_Î*")
    for k, a in store.items():
        c, cc, pr = a["center_f05"], a["center_clean"], a["procedure"]
        print(f"{k:22s} | {c[0]:+7.3f} ± {c[1]:.3f} = {cc[0]:+9.3f} ± {cc[1]:.3f} + {pr[0]:+10.3f} ± {pr[1]:.3f} | "
              f"{a['kind_star']}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "f05c_results.json").write_text(json.dumps(store, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        for k, a in store.items():
            L = a["law"][2.0]
            x = 0.0 if a["lam"] == 0 else L["pred"]
            ax[0].errorbar(x, a["pure"][0], yerr=a["pure"][1], fmt="o", capsize=3, label=k)
            ax[1].plot(a["k_excess"], a["pure"][0] / a["head"] * 100, "o", label=k)
        lim = max(0.5, max(abs(a["pure"][0]) + a["pure"][1] for a in store.values()))
        ax[0].plot([-lim, lim], [-lim, lim], "k--", lw=0.8)
        ax[0].axhline(0, color="grey", lw=0.5)
        ax[0].set(xlabel="gap thuần dự đoán f₀β²κ_b²/(2a′) (ms)", ylabel="K2 − SC quan sát ± CI95 (ms)",
                  title="Luật bậc hai trên DES cũ (post hoc)")
        kk = np.linspace(0, 1, 50)
        toy = np.interp(kk, [0, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0], [0, 0.09, 0.39, 1.44, 3.49, 7.61, 13.85])
        ax[1].plot(kk, toy, "k:", label="toy t05 (không chuyển hằng số)")
        ax[1].set(xlabel="κ vượt sàn", ylabel="share_pure (%)", title="Tỉ lệ thuần theo κ")
        ax[1].legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(OUT / "f05c_law.png", dpi=150)
    except ImportError:
        print("matplotlib không có: bỏ qua hình", file=sys.stderr)
    print(f"Thời gian {time.time() - t_start:.0f} s", file=sys.stderr)
