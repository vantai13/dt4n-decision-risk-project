"""f08b (P1v2/L1.9) — KHÁM PHÁ POST HOC sau outcome F8 (423546f). KHÔNG đổi phán quyết F8.

Câu hỏi: vì sao oracle bin thua S0 ở T10/FH (cổng K2 − S0 ≥ −2SE hỏng, −3,1 SE)? Giả thuyết: biên quyết định của S0 là một
đường mức của Î_twin nằm sát đường chéo tâm_cur ≈ tâm_alt; ô vuông trên (tâm_cur, tâm_alt) trộn epoch Î âm và dương nên
oracle không phân giải được biên, thua luật dùng Î liên tục. F1 không lộ vì S0_F1 quá yếu (ngưỡng 256 ms).

Định nghĩa ghi TRƯỚC khi chạy (kế hoạch 2026-09-30T10:42:59Z; dòng log tương ứng):
  E0 tái lập oracle gốc: 20×20 vuông, cạnh phân vị GỘP trên (tâm_cur, tâm_alt) — phải trùng từng bit outcome F8.
  E1 cùng toạ độ, mịn hơn: 40×40 vuông, cạnh gộp.
  E2 toạ độ khớp biên: cạnh phân vị RIÊNG từng chiều trên (Î_twin, L = tâm_cur + tâm_alt); 20×20 và 40×40.
  E3 validity có bắt được không: K2 − S0 decision-level trên 8 seed calibration, oracle gốc.
  E4 quỹ đạo chung (T10): F1 và FH cùng dựng + đánh giá oracle dọc quỹ đạo S0 của F1 (headroom giống hệt).
Phụ lục ghi SAU khi thấy E0–E4, TRƯỚC khi chạy (2026-09-30T10:50:21Z), báo riêng, không phải kế hoạch gốc:
  F  trần thông tin (chỉ seed calibration): G = tải thật TB khoảng giữ; tỉ lệ nội tại E[Var(D | G)]/Var(D) (50 bin phân vị
     của G) và trần ρ_s²(G, D). Dự đoán AI: nội tại T10 > 0,5, P2 < 0,3; trần T10 < 0,5, P2 > 0,7.
  G  cận không dùng oracle cho phán quyết VoIP tuyệt đối: headroom − S0 (luật thấu thị trên quỹ đạo S0) so với m = 8,1 ms,
     tính từ JSON outcome.
Danh sách phân tích đã chạy là ĐỦ: E0–E4, F, G. Không có phân tích nào bị bỏ khỏi output.
Mọi thứ khác y hệt f08: seed, khoá 730, S0 tune theo J, λ và ngưỡng SC tune bằng harm dự đoán trên cal, κ̂ = D4.
Provenance: Claude (AI) ghi kế hoạch, viết script, chạy trước trong sandbox; tác giả chạy lại, kiểm, commit.
Chạy: python experiments/f08b_oracle_resolution.py | tee experiments/results/f08b_oracle_resolution_output.txt
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.signal import lfilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import f02_existence_surrogate as f
import f04b_des_gap as g
import f05_oracle_age as q
import f07_asym_risk as r7
import f08_history_twin as h

OUTCOME_JSON = HERE / "results" / "f08" / "f08_outcome.json"
FEATS = {"vuông": lambda o: (o["rh_cur"], o["rh_alt"]),
         "khớp biên": lambda o: (o["Ihat"], o["rh_cur"] + o["rh_alt"])}
VARIANTS = {"E0 vuông 20": ("vuông", 20, True), "E1 vuông 40": ("vuông", 40, True),
            "E2 khớp biên 20": ("khớp biên", 20, False), "E2 khớp biên 40": ("khớp biên", 40, False)}


class Oracle2D:
    """Oracle bin 2 chiều tổng quát. pooled=True + toạ độ vuông ⇒ trùng từng bit f07.DirOracle(use_dir=False)."""

    def __init__(self, orients, eps_ms, feat, n_bin, pooled, min_count=r7.MIN_COUNT):
        self.feat = FEATS[feat]
        x1, x2 = (np.concatenate([self.feat(o)[i] for o in orients]) for i in (0, 1))
        I = np.concatenate([o["I"] for o in orients])
        q_ = np.linspace(0, 1, n_bin + 1)
        if pooled:
            e = np.unique(np.quantile(np.concatenate([x1, x2]), q_))
            self.edges = [e, e]
        else:
            self.edges = [np.unique(np.quantile(x, q_)) for x in (x1, x2)]
        self.shape = [len(e) - 1 for e in self.edges]
        idx = self._idx(x1, x2)
        n = self.shape[0] * self.shape[1]
        cnt = np.bincount(idx, minlength=n).astype(float)
        ok = cnt >= min_count
        mean = np.bincount(idx, I, n) / np.maximum(cnt, 1)
        var = np.bincount(idx, I * I, n) / np.maximum(cnt, 1) - mean**2
        self.ibar = np.where(ok, mean, I.mean())
        self.pdn = np.where(ok, np.bincount(idx, (I < -eps_ms).astype(float), n) / np.maximum(cnt, 1),
                            (I < -eps_ms).mean())
        self.sd = np.where(ok, np.sqrt(np.maximum(var, 1e-12)), I.std())
        self.count = np.where(ok, cnt, len(I))
        self.frac_sparse = float(np.mean(~ok[idx]))

    def _idx(self, x1, x2):
        b = [np.clip(np.searchsorted(e, x, side="right") - 1, 0, nb - 1) for e, x, nb in zip(self.edges, (x1, x2),
                                                                                           self.shape)]
        return b[0] * self.shape[1] + b[1]

    def predict(self, o):
        k = self._idx(*self.feat(o))
        return self.ibar[k], self.pdn[k], self.sd[k], self.count[k]


def orient_along(eps, curs):
    return [r7.orient_dir(ep, cur) for ep, cur in zip(eps, curs)]


def run_variant(r_cal, r_test, r_orc, s0_test, s0_cal, eps_ms, spec):
    feat, nb, pooled = spec
    orc = Oracle2D(r_orc, eps_ms, feat, nb, pooled)
    pc = [orc.predict(o)[:2] for o in r_cal]
    lam, hc = f.tune_lambda(pc, 0.0), q.tune_center(pc)
    per, ib_all, ls_all, cnt_all = defaultdict(list), [], [], []
    for o, g0 in zip(r_test, s0_test):
        ib, pd, sd, cnt = orc.predict(o)
        I = o["I"]
        per["S0"].append(g0)
        for name, a in (("SC", ib > hc), ("K2", (ib - lam * pd) > 0), ("K2inf", ib > 0)):
            per[name].append(np.mean(a * I))
        per["head"].append(np.mean(np.maximum(I, 0)))
        ls = np.log(sd)
        per["kappa"].append(r7.kappa(ib, ls)[0])
        ib_all.append(ib), ls_all.append(ls), cnt_all.append(cnt)
    cal_gap = [np.mean(((ib - lam * pd) > 0) * o["I"]) - g0 for (ib, pd), o, g0 in zip(pc, r_cal, s0_cal)]
    per = {k: np.array(v) for k, v in per.items()}
    ib, ls, cnt = (np.concatenate(x) for x in (ib_all, ls_all, cnt_all))
    fb, fs, ft = r7.floors_by_dir(ib, ls, cnt, np.zeros(len(ib), np.int64))
    return dict(per=per, lam=lam, hc=hc, sparse=orc.frac_sparse, k_pool=r7.kappa(ib, ls)[0], floor=ft,
                cal_gap=np.array(cal_gap))


def s0_setup(eps, eps_ms):
    """S0 tune trên cal như f08; trả quỹ đạo (cur) và gain riêng theo seed cho cal/test/orc."""
    rule0, _ = r7.tune_rules(eps["cal"], eps_ms, directional=False)
    out = {}
    for k in ("cal", "test", "orc"):
        acts_curs = [r7.run_rule(ep, rule0) for ep in eps[k]]
        out[k] = dict(cur=[c for _, c in acts_curs],
                      gain=[float(np.mean(a * r7.orient_dir(ep, c)["I"])) for (a, c), ep in zip(acts_curs, eps[k])])
    return rule0, out


def path_with_G(rng, cell, psa):
    """Bản sao g.one_path (CÙNG thứ tự rút số — kiểm bằng assert) + G = tải thật TB khoảng giữ (lưới DT, hình thang)."""
    t_dec = g.BURN_IN + cell.lag + cell.win + cell.hold * np.arange(f.N_EPOCH)
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
    probes = (t_dec + cell.act)[:, None] + np.linspace(0.0, cell.hold, g.N_PROBE)[None, :]
    j = np.searchsorted(arrivals, probes, side="right") - 1
    jj = np.maximum(j, 0)
    v = np.where(j >= 0, np.maximum(v_after[jj] - (probes - arrivals[jj]), 0.0), 0.0)
    ok = v <= full
    n_ok = ok.sum(1)
    d = np.where(n_ok > 0, np.where(ok, v + s, 0.0).sum(1) / np.maximum(n_ok, 1), cell.k * s) * 1e3
    i0, hn = np.rint((t_dec + cell.act) / f.DT).astype(int), int(round(cell.hold / f.DT))
    G = np.array([rho[a:a + hn + 1] @ f.trap_w(hn + 1) for a in i0])
    return d, G, t_dec


def ceiling(cell):
    """F: trần thông tin trên seed calibration, hai path gộp."""
    psa, D, G = r7.psa_for(cell.k), [], []
    for sd in h.SEEDS["cal"]:
        for ch in np.random.SeedSequence([sd, h.STREAM]).spawn(2):
            d, gg, t_dec = path_with_G(np.random.default_rng(ch), cell, psa)
            assert np.array_equal(d, g.one_path(np.random.default_rng(ch), cell, psa, t_dec)[1]), "bản sao lệch f04b"
            D.append(d), G.append(gg)
    D, G = np.concatenate(D), np.concatenate(G)
    e = np.unique(np.quantile(G, np.linspace(0, 1, 51)))
    b = np.clip(np.searchsorted(e, G, side="right") - 1, 0, len(e) - 2)
    within = sum(np.var(D[b == k]) * np.sum(b == k) for k in np.unique(b)) / len(D)
    return float(within / np.var(D)), float(stats.spearmanr(G, D)[0] ** 2)


def se(x):
    return float(np.std(x, ddof=1) / np.sqrt(len(x)))


def main():
    t0 = time.time()
    ref = json.loads(OUTCOME_JSON.read_text(encoding="utf-8"))
    print("f08b — KHÁM PHÁ POST HOC (không đổi phán quyết F8) | seed và khoá như f08 outcome")
    res, store = {}, {}
    for w, name in h.WORLDS.items():
        cell = g.CELLS[name][0]
        eps_ms = f.EPS_OVER_S * cell.s_ms
        sims = {k: h.simulate(cell, h.SEEDS[k], h.STREAM) for k in ("cal", "test", "orc")}
        setup = {}
        for c in h.CONDS:
            eps = {k: sims[k][c] for k in sims}
            rule0, tr = s0_setup(eps, eps_ms)
            setup[c] = (eps, tr)
            r = {k: orient_along(eps[k], tr[k]["cur"]) for k in eps}
            for vname, spec in VARIANTS.items():
                res[(w, c, vname)] = run_variant(r["cal"], r["test"], r["orc"], tr["test"]["gain"], tr["cal"]["gain"],
                                                 eps_ms, spec)
            p0, j = res[(w, c, "E0 vuông 20")]["per"], ref[f"{w}/{c}"]["per"]
            same = all(np.array_equal(p0[a], np.array(j[b_])) for a, b_ in
                       (("S0", "gain_ref"), ("K2", "gain_K2"), ("SC", "gain_SC"), ("K2inf", "gain_K2inf"),
                        ("head", "headroom")))
            dk = float(np.max(np.abs(p0["kappa"] - np.array(j["k_chung"]))))
            same = same and dk < 1e-12                      # κ̂ qua lstsq/std: khác máy lệch ~1e−16 (như F7 §2.9)
            print(f"[{w}/{c}] S0 {rule0[1]} {rule0[2]:.4g} | E0 tái lập outcome F8: gain trùng từng bit, "
                  f"κ̂ lệch tối đa {dk:.1e} → {same}")
            assert same, "E0 KHÔNG tái lập outcome — dừng"
        if w == "T10":                                       # E4: quỹ đạo chung = quỹ đạo S0 của F1
            tr1 = setup["F1"][1]
            for c in h.CONDS:
                eps = setup[c][0]
                r = {k: orient_along(eps[k], tr1[k]["cur"]) for k in eps}
                res[(w, c, "E4 quỹ đạo F1")] = run_variant(r["cal"], r["test"], r["orc"], tr1["test"]["gain"],
                                                           tr1["cal"]["gain"], eps_ms, VARIANTS["E0 vuông 20"])

    print("\nBẢNG A — cổng oracle và phân rã (ms/epoch; CI95 t theo 90 seed; 'cal' = E3: K2 − S0 trên 8 seed cal)")
    for (w, c, v), r in res.items():
        p = r["per"]
        d = p["K2"] - p["S0"]
        m, hw = r7.ci_n(d)
        sh = (p["head"] - p["K2inf"]) / p["head"]
        print(f"[{w}/{c}] {v:16s} K2 − S0 {m:+.3f} ± {hw:.3f} ({m / se(d):+5.1f} SE, cổng {'✓' if m >= -2 * se(d) else '✗'})"
              f" | SC − S0 {np.mean(p['SC'] - p['S0']):+.3f} | cal {np.mean(r['cal_gap']):+.3f} ± "
              f"{r7.ci_n(r['cal_gap'])[1]:.3f} | share_info {100 * sh.mean():.1f}% | headroom {p['head'].mean():.2f} | "
              f"κ̂ {p['kappa'].mean():.3f} (gộp {r['k_pool']:.3f}, sàn {r['floor']:.3f}) | λ {r['lam']:.1f} | "
              f"thưa {100 * r['sparse']:.2f}%")
        store[f"{w}/{c}/{v}"] = dict(K2_S0=(m, hw), cal_gap=r7.ci_n(r["cal_gap"]), share_info=float(sh.mean()),
                                     kappa=r7.ci_n(p["kappa"]), k_pool=r["k_pool"], floor=r["floor"], lam=r["lam"],
                                     sparse=r["sparse"], headroom=float(p["head"].mean()))

    print("\nBẢNG B — Δκ̂ và share_info theo biến thể oracle (theo seed, ghép cặp)")
    for v in list(VARIANTS) + ["E4 quỹ đạo F1"]:
        k = lambda w, c: res[(w, c, v)]["per"]["kappa"]
        sh = lambda w, c: (res[(w, c, v)]["per"]["head"] - res[(w, c, v)]["per"]["K2inf"]) / res[(w, c, v)]["per"]["head"]
        d10 = k("T10", "FH") - k("T10", "F1")
        line = f"{v:16s} Δ₁₀ {r7.txt(d10)} | share_info FH − F1 (T10) {r7.txt(100 * (sh('T10', 'FH') - sh('T10', 'F1')), 2)} đ%"
        if v != "E4 quỹ đạo F1":
            dp2 = k("P2", "FH") - k("P2", "F1")
            line += f" | Δ_P2 {r7.txt(dp2)} | Δ₁₀ − Δ_P2 {r7.txt(d10 - dp2)}"
        print("  " + line)
    print("\nBẢNG C — F: trần thông tin (seed calibration; so với ρ_s²(tâm, D) của f08 validity: T10 0,132 → 0,293; "
          "P2 0,430 → 0,573)")
    for w, name in h.WORLDS.items():
        frac, cap = ceiling(g.CELLS[name][0])
        print(f"  [{w}] tỉ lệ nội tại E[Var(D | G)]/Var(D) {frac:.3f} | trần ρ_s²(G, D) khi biết HOÀN HẢO tải khoảng giữ {cap:.3f}")
        store[f"{w}/ceiling"] = dict(intrinsic=frac, rho_s2_G=cap)
    print("\nBẢNG D — G: cận không dùng oracle cho VoIP tuyệt đối: headroom − S0 (luật thấu thị trên quỹ đạo S0) so với m")
    for k in ("T10/F1", "T10/FH", "P2/F1", "P2/FH"):
        p = ref[k]["per"]
        m, hw = r7.ci_n(np.array(p["headroom"]) - np.array(p["gain_ref"]))
        print(f"  [{k}] {m:.2f} ± {hw:.2f} ms | cận trên {m + hw:.2f} {'< m ⇒ KHÔNG ĐÁNG KỂ không cần oracle' if m + hw < f.M_SESOI_MS else '≥ m ⇒ cần oracle'}")
        store[f"{k}/clairvoyant"] = (m, hw)
    out = HERE / "results" / "f08b"
    out.mkdir(parents=True, exist_ok=True)
    (out / "f08b_results.json").write_text(json.dumps(store, indent=1, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"Thời gian {time.time() - t0:.0f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
