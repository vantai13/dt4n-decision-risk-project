"""f07 (P1v2/L1.8) — F7b: hai path cùng delay TB, khác rủi ro. Thực thi F7 §2 v2, khoá tại tag prereg-f7 (9a4ac69).

Chế độ, theo thứ tự đã khoá (Phần A → anchor → validity [commit] → outcome [commit]):
  anchor   — code f07 ở CẤU HÌNH f05c (quỹ đạo S0 một ngưỡng; oracle F20x2 KHÔNG chiều; seed f04b; khoá 712 và 712 + EXTRA)
             phải tái lập f05c K100_r0.85_s10t2/A0 đến chữ số in ra: λ 51,29; t₀ 11,56; K2 − SC +0,103 ± 0,119; κ̂ 0,271.
  validity — AA, BB, AB: CHỈ calibration + dữ liệu oracle. In cổng và tham số đã tune. KHÔNG mô phỏng seed test,
             KHÔNG tính κ̂, gap hay estimand nào của §2.4.
  outcome  — 90 seed test: estimand §2.4, phép kiểm §2.6, ô của bảng §2.7; ghi results/f07/f07_results.json.
  smoke    — episode NGẪU NHIÊN tổng hợp (không phải thế giới F7, không DES) để chạy thử mọi nhánh code; số liệu vô nghĩa.

Cài đặt các chỗ văn bản khoá để ngỏ (ghi vào F7 §3; không đổi estimand hay tiêu chí chính):
  (1) CI95 dùng t với bậc tự do n − 1 theo SỐ SEED THẬT. f02.ci cố định t cho 8 seed nên KHÔNG dùng cho 90 seed.
  (2) "harm ≤ α trên calibration cho mọi luật" = theo tiêu chí mà luật được tune: harm THỰC trên quỹ đạo riêng (S0, S0dir);
      harm DỰ ĐOÁN dọc quỹ đạo tham chiếu (SC, SCdir, K2). Harm thực của luật oracle được BÁO, không làm cổng.
  (3) SCdir "tune_center mỗi chiều một": mỗi chiều tự thoả harm dự đoán ≤ α trên các epoch calibration của chiều đó
      (gộp mọi seed) ⇒ tổng thể ≤ α. SCdir chỉ vào phân rã và L (mô tả), không vào M1, M2, V, D.
  (4) Ô thưa theo chiều: tỉ lệ mẫu dữ liệu oracle rơi vào ô < 30 mẫu, tính riêng từng chiều (định nghĩa như f05).
  (5) Sàn D6 = √(sàn bin² + sàn mẫu²) trên dữ liệu gộp, tính cho κ̂_chiều (trong từng chiều, trọng số theo số epoch);
      M2 so |hiệu| với tổng sàn κ̂_chiều của hai thế giới.
  (6) κ̂ theo seed: chiều có < 2·20 epoch trong seed bị bỏ khỏi trung bình của seed đó; báo số lần bỏ.
  (7) S0 "để đối chiếu" trong phân rã = luật một ngưỡng áp decision-level trên quỹ đạo tham chiếu S0dir; D dùng J của S0 và
      S0dir trên quỹ đạo RIÊNG của mỗi luật.
  (8) Epoch đầy buffer suốt khoảng giữ: giữ đúng f04b (thay bằng K·S, đếm n_nan) để anchor tái lập được; báo n_nan.
Provenance: Claude (AI) viết theo F7 §2 v2; tác giả kiểm từng hàm, chạy các chế độ và commit theo thứ tự đã khoá.
Chạy: python experiments/f07_asym_risk.py --mode {anchor|validity|outcome|smoke}
      | tee experiments/results/f07_<mode>_output.txt
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import f02_existence_surrogate as f
import f04b_des_gap as g
import f05_oracle_age as q

ALPHA, N_BIN, MIN_COUNT, STREAM = f.ALPHA, 20, 30, 720
SEEDS = dict(cal=tuple(range(11001, 11009)), test=tuple(range(11011, 11101)), orc=tuple(range(11101, 11698)))
PATH = {"A": f.Cell("A_K100_r0.85_s10t2", 4, 100, 0.85, 0.10, 2.0),
        "B": f.Cell("B_K100_r0.918_s03t10", 4, 100, 0.918, 0.03, 10.0)}
WORLDS = {"AA": ("A", "A"), "BB": ("B", "B"), "AB": ("A", "B")}
ANCHOR = dict(cell="K100_r0.85_s10t2", lam=51.29, t0=11.56, pure=(0.103, 0.119), k_pure=0.271)
F05C_JSON = HERE / "results" / "f05c" / "f05c_results.json"
OUT = HERE / "results" / "f07"
_PSA = {}


# ---------------------------------------------------------------- thống kê
def ci_n(x):
    """(trung bình, nửa độ rộng CI95) với t theo bậc tự do n − 1 của CHÍNH mẫu (bỏ NaN)."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(x.mean()), float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))


def txt(x, d=3):
    m, h = ci_n(x)
    return f"{m:+.{d}f} ± {h:.{d}f}"


def edges_of(x, n_bin):
    e = np.unique(np.quantile(x, np.linspace(0, 1, n_bin + 1)))
    return e, np.clip(np.searchsorted(e, x, side="right") - 1, 0, len(e) - 2)


def kappa(key, log_s, n_bin=N_BIN, detrend=True):
    """D4 của L1.6 (giống f05c từng dòng): (κ, phần dư r)."""
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
    _, b = edges_of(key, n_bin)
    xs = np.array([key[b == k].mean() for k in np.unique(b)])
    ys = np.array([log_s[b == k].mean() for k in np.unique(b)])
    return np.interp(key, xs, ys)


def kappa_by_dir(ibar, log_s, dirs, min_n=2 * N_BIN):
    """κ̂_chiều: D4 trong từng chiều, trung bình trọng số theo số epoch; chiều quá ít epoch bị bỏ (cài đặt 6)."""
    vals, wts, dropped = [], [], 0
    for d in np.unique(dirs):
        m = dirs == d
        if m.sum() < min_n:
            dropped += 1
            continue
        vals.append(kappa(ibar[m], log_s[m])[0])
        wts.append(m.sum())
    return (float(np.average(vals, weights=wts)) if vals else np.nan), dropped


def floors_by_dir(ibar, log_s, count, dirs):
    """Sàn D6 (cài đặt 5): √(sàn bin² + sàn mẫu²), sàn bin tính trong từng chiều rồi lấy trọng số."""
    fb, w = [], []
    for d in np.unique(dirs):
        m = dirs == d
        if m.sum() >= 2 * N_BIN:
            fb.append(kappa(ibar[m], smooth_log_s(ibar[m], log_s[m]))[0])
            w.append(m.sum())
    f_bin = float(np.average(fb, weights=w))
    f_smp = float(np.mean(1 / np.sqrt(2 * np.maximum(count - 1, 1))))
    return f_bin, f_smp, float(np.hypot(f_bin, f_smp))


# ---------------------------------------------------------------- mô phỏng
def psa_for(k):
    if k not in _PSA:
        _PSA[k] = f.PSA(k)
    return _PSA[k]


def slot_path(seed, stream, slot, cell):
    """Một khe path của một seed. Khe = con thứ `slot` của SeedSequence([seed, stream]).spawn(2), đúng như f04b."""
    child = np.random.SeedSequence([seed, stream]).spawn(2)[slot]
    t_dec = g.BURN_IN + cell.lag + cell.win + cell.hold * np.arange(f.N_EPOCH)
    rh, des, _, n_nan, clip = g.one_path(np.random.default_rng(child), cell, psa_for(cell.k), t_dec)
    return rh, des, n_nan, clip


def episode(p1, p2, s_ms, k=100):
    """Ghép hai khe thành episode có đúng các khoá mà f02.static_run / tune_static / orient cần (như f04b)."""
    (rh1, des1, nan1, clip1), (rh2, des2, nan2, clip2) = p1, p2
    psa = psa_for(k)
    d1, d2 = psa.point(rh1) * s_ms, psa.point(rh2) * s_ms
    return dict(D_A=des1, D_B=des2, I_A=des1 - des2, Ihat_A=d1 - d2, Chat_A=d1, Chat_B=d2, rh_A=rh1, rh_B=rh2,
                n_nan=nan1 + nan2, clip=max(clip1, clip2))


def simulate_world(world, seeds, cache, stream=STREAM):
    """CRN: khe 1 của AA và AB là CÙNG một path A; khe 2 của BB và AB là CÙNG một path B (dùng chung cache)."""
    types = WORLDS[world]
    for cell in (PATH[t] for t in types):
        assert (cell.lag, cell.act, cell.win, cell.hold, cell.mbps, cell.k) == \
               (PATH["A"].lag, PATH["A"].act, PATH["A"].win, PATH["A"].hold, PATH["A"].mbps, PATH["A"].k)
    out = []
    for s in seeds:
        p = []
        for slot, t in enumerate(types):
            key = (s, stream, slot, t)
            if key not in cache:
                cache[key] = slot_path(s, stream, slot, PATH[t])
            p.append(cache[key])
        out.append(episode(*p, PATH["A"].s_ms))
    return out


# ---------------------------------------------------------------- luật tĩnh
def dir_scores(ep, kind):
    """Điểm theo chiều: khe1→khe2 (đang ở khe 1) và khe2→khe1. Họ rel chia cho Ĉ của path hiện tại (như static_run)."""
    if kind == "abs":
        return ep["Ihat_A"], -ep["Ihat_A"]
    return ep["Ihat_A"] / ep["Chat_A"], -ep["Ihat_A"] / ep["Chat_B"]


def static_run_dir(ep, kind, t12, t21):
    """Luật hai ngưỡng TUẦN TỰ cho nhiều cặp ngưỡng cùng lúc → (đổi, cur_is_khe1), dạng (n_cặp, N).
    Khi t12 = t21 thì trùng từng bit với f02.static_run (kiểm trong tests/test_f07_units.py)."""
    t12, t21 = np.atleast_1d(np.asarray(t12, float)), np.atleast_1d(np.asarray(t21, float))
    s12, s21 = dir_scores(ep, kind)
    cur = np.ones(len(t12), bool)
    act, hist = np.zeros((len(t12), f.N_EPOCH), bool), np.zeros((len(t12), f.N_EPOCH), bool)
    for e in range(f.N_EPOCH):
        hist[:, e] = cur
        act[:, e] = sw = np.where(cur, s12[e] > t12, s21[e] > t21)        # hoà thì GIỮ
        cur = cur ^ sw
    return act, hist


def _evaluate_pairs(cal, kind, t12, t21, eps_ms, chunk=1024):
    J, H = np.zeros(len(t12)), np.zeros(len(t12))
    for lo in range(0, len(t12), chunk):
        sl = slice(lo, lo + chunk)
        for ep in cal:
            act, cur = static_run_dir(ep, kind, t12[sl], t21[sl])
            I = np.where(cur, 1.0, -1.0) * ep["I_A"][None, :]
            J[sl] += (np.where(cur, ep["D_A"], ep["D_B"]) - act * I).mean(1) / len(cal)
            H[sl] += (act * (I < -eps_ms)).mean(1) / len(cal)
    return J, H


def tune_static_dir(cal, kind, eps_ms, n_grid=80, n_fine=21):
    """Khuôn f02.tune_static mở rộng hai chiều (F7 §2.3): lưới tích 81 × 81 ({0} ∪ 80 phân vị [0,3; 0,9995] của điểm
    theo từng chiều trên cal), tối thiểu J với harm thực ≤ α; tinh chỉnh 21 × 21 giữa hai điểm lưới kề; chỉ thay khi J tốt hơn."""
    sc = [np.concatenate(x) for x in zip(*[dir_scores(ep, kind) for ep in cal])]
    grids = [np.unique(np.concatenate([[0.0], np.quantile(s, np.linspace(0.3, 0.9995, n_grid))])) for s in sc]
    G12, G21 = (a.ravel() for a in np.meshgrid(grids[0], grids[1], indexing="ij"))
    J, H = _evaluate_pairs(cal, kind, G12, G21, eps_ms)
    if not (H <= ALPHA).any():
        return None
    i = int(np.argmin(np.where(H <= ALPHA, J, np.inf)))
    i12, i21 = np.unravel_index(i, (len(grids[0]), len(grids[1])))
    fine = [np.linspace(gr[max(k - 1, 0)], gr[min(k + 1, len(gr) - 1)], n_fine) for gr, k in zip(grids, (i12, i21))]
    F12, F21 = (a.ravel() for a in np.meshgrid(*fine, indexing="ij"))
    J2, H2 = _evaluate_pairs(cal, kind, F12, F21, eps_ms)
    j = int(np.argmin(np.where(H2 <= ALPHA, J2, np.inf)))
    if J2[j] < J[i]:
        return (float(F12[j]), float(F21[j])), float(J2[j])
    return (float(G12[i]), float(G21[i])), float(J[i])


def run_rule(ep, rule):
    """rule = (kiểu, họ, ngưỡng, J_cal). Trả (đổi, cur_is_khe1) trên quỹ đạo RIÊNG của luật."""
    typ, kind, thr, _ = rule
    act, hist = f.static_run(ep, kind, thr) if typ == "single" else static_run_dir(ep, kind, thr[0], thr[1])
    return act[0], hist[0]


def own_J_H(ep, rule, eps_ms):
    act, cur = run_rule(ep, rule)
    I = np.where(cur, 1.0, -1.0) * ep["I_A"]
    return float(np.mean(np.where(cur, ep["D_A"], ep["D_B"]) - act * I)), float(np.mean(act * (I < -eps_ms))), act, cur


def tune_rules(cal, eps_ms, directional):
    s0 = {kd: f.tune_static(cal, kd, 0.0, eps_ms) for kd in ("abs", "rel")}
    k0 = min(s0, key=lambda kd: s0[kd][1])
    rule0 = ("single", k0, s0[k0][0], s0[k0][1])
    if not directional:
        return rule0, None
    sd = {kd: tune_static_dir(cal, kd, eps_ms) for kd in ("abs", "rel")}
    sd = {k: v for k, v in sd.items() if v is not None}
    kd = min(sd, key=lambda k: sd[k][1])
    return rule0, ("dir", kd, sd[kd][0], sd[kd][1])


# ---------------------------------------------------------------- oracle
def orient_dir(ep, cur_a):
    o = f.orient(ep, cur_a)
    o["dir"] = np.asarray(cur_a, bool).astype(np.int64)              # 1: đang ở khe 1; 0: đang ở khe 2
    o["Chat_cur"] = np.where(cur_a, ep["Chat_A"], ep["Chat_B"])
    return o


class DirOracle:
    """Oracle bin (ρ̂_cur, ρ̂_alt[, chiều]) + sd của I trong ô + số mẫu mỗi ô. Cạnh phân vị gộp ρ̂_cur và ρ̂_alt dọc
    quỹ đạo tham chiếu. use_dir=False ⇒ trùng từng bit q.GridOracle('F', 20) và SdGridOracle của f05c."""

    def __init__(self, orients, eps_ms, use_dir, n_bin=N_BIN, min_count=MIN_COUNT):
        rc, ra, I = (np.concatenate([o[k] for o in orients]) for k in ("rh_cur", "rh_alt", "I"))
        d = np.concatenate([o["dir"] for o in orients]) if use_dir else np.zeros(len(I), np.int64)
        self.use_dir = use_dir
        self.edges = np.unique(np.quantile(np.concatenate([rc, ra]), np.linspace(0, 1, n_bin + 1)))
        self.nb, self.nd = len(self.edges) - 1, 2 if use_dir else 1
        idx = self._idx(rc, ra, d)
        n = self.nd * self.nb * self.nb
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
        self.sparse_by_dir = {int(k): float(np.mean(~ok[idx][d == k])) for k in range(self.nd) if (d == k).any()}

    def _bin(self, x):
        return np.clip(np.searchsorted(self.edges, x, side="right") - 1, 0, self.nb - 1)

    def _idx(self, rc, ra, d):
        return (d * self.nb + self._bin(rc)) * self.nb + self._bin(ra)

    def predict(self, o):
        d = o["dir"] if self.use_dir else np.zeros(len(o["I"]), np.int64)
        k = self._idx(o["rh_cur"], o["rh_alt"], d)
        return self.ibar[k], self.pdn[k], self.sd[k], self.count[k]


def tune_center_pooled(ibar, pdn):
    """Ngưỡng H ≥ 0 nhỏ nhất để TB (Ī > H)·p− ≤ α trên tập epoch cho trước (cài đặt 3, dùng cho từng chiều)."""
    harm = lambda h: float(np.mean((ibar > h) * pdn))
    if harm(0.0) <= ALPHA:
        return 0.0
    lo, hi = 0.0, 1.0
    while harm(hi) > ALPHA:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if harm(mid) <= ALPHA else (mid, hi)
    return hi


# ---------------------------------------------------------------- pipeline chung
def build(eps, eps_ms, directional):
    """Tune trên calibration, dựng oracle trên dữ liệu oracle. KHÔNG đụng seed test."""
    cal, orc = eps["cal"], eps["orc"]
    rule0, ruled = tune_rules(cal, eps_ms, directional)
    ref = ruled if directional else rule0
    orient = lambda ep: orient_dir(ep, run_rule(ep, ref)[1])
    r_orc, r_cal = [orient(ep) for ep in orc], [orient(ep) for ep in cal]
    oracle = DirOracle(r_orc, eps_ms, directional)
    pc = [oracle.predict(o)[:2] for o in r_cal]
    lam, h_c = f.tune_lambda(pc, 0.0), q.tune_center(pc)
    h_dir = None
    if directional:
        ib = np.concatenate([p[0] for p in pc])
        pd = np.concatenate([p[1] for p in pc])
        dd = np.concatenate([o["dir"] for o in r_cal])
        h_dir = {d: tune_center_pooled(ib[dd == d], pd[dd == d]) if (dd == d).any() else 0.0 for d in (0, 1)}
    # Cổng calibration (cài đặt 2)
    gates = {"S0 harm thực": np.mean([own_J_H(ep, rule0, eps_ms)[1] for ep in cal])}
    if directional:
        gates["S0dir harm thực"] = np.mean([own_J_H(ep, ruled, eps_ms)[1] for ep in cal])
    pred_harm = defaultdict(list)
    real_harm = defaultdict(list)
    for (ibar, pdn), o in zip(pc, r_cal):
        harm = o["I"] < -eps_ms
        rules = {"K2": (ibar - lam * pdn) > 0, "SC": ibar > h_c}
        if directional:
            rules["SCdir"] = ibar > np.where(o["dir"] == 1, h_dir[1], h_dir[0])
        for name, a in rules.items():
            pred_harm[name].append(np.mean(a * pdn))
            real_harm[name].append(np.mean(a * harm))
    for name in pred_harm:
        gates[f"{name} harm dự đoán"] = float(np.mean(pred_harm[name]))
    reported = {f"{name} harm thực (báo)": float(np.mean(v)) for name, v in real_harm.items()}
    return dict(rule0=rule0, ruled=ruled, ref=ref, oracle=oracle, lam=lam, h_c=h_c, h_dir=h_dir, gates=gates,
                reported=reported, dir_frac_cal=float(np.mean(np.concatenate([o["dir"] for o in r_cal]))))


def evaluate_test(test, b, eps_ms, directional):
    """Mọi estimand của §2.4 trên seed test, theo seed và gộp."""
    per, pool = defaultdict(list), defaultdict(list)
    kind0, thr0 = b["rule0"][1], b["rule0"][2]
    for ep in test:
        J0, _, _, _ = own_J_H(ep, b["rule0"], eps_ms)
        if directional:
            Jd, _, a_ref, cur = own_J_H(ep, b["ruled"], eps_ms)
        else:
            Jd, a_ref, cur = J0, *own_J_H(ep, b["rule0"], eps_ms)[2:]
        o = orient_dir(ep, cur)
        ib, pd, sd, cnt = b["oracle"].predict(o)
        I, harm = o["I"], o["I"] < -eps_ms
        score0 = o["Ihat"] if kind0 == "abs" else o["Ihat"] / o["Chat_cur"]
        acts = {"ref": a_ref, "S0dl": score0 > thr0, "SC": ib > b["h_c"], "K2": (ib - b["lam"] * pd) > 0,
                "K2inf": ib > 0}
        acts["SCdir"] = ib > np.where(o["dir"] == 1, b["h_dir"][1], b["h_dir"][0]) if directional else acts["SC"]
        for name, a in acts.items():
            per[f"gain_{name}"].append(np.mean(a * I))
            per[f"harm_{name}"].append(np.mean(a * harm))
        per["headroom"].append(np.mean(np.maximum(I, 0)))
        per["J_S0"].append(J0)
        per["J_S0dir"].append(Jd)
        per["ED1_minus_ED2"].append(np.mean(ep["D_A"]) - np.mean(ep["D_B"]))
        per["dir_frac"].append(np.mean(o["dir"]))
        per["n_nan"].append(ep["n_nan"])
        ls = np.log(sd)
        per["k_chung"].append(kappa(ib, ls)[0])
        kd, dropped = kappa_by_dir(ib, ls, o["dir"]) if directional else (per["k_chung"][-1], 0)
        per["k_chieu"].append(kd)
        per["k_dropped"].append(dropped)
        for key, val in (("ibar", ib), ("pdn", pd), ("log_s", ls), ("count", cnt), ("dir", o["dir"]),
                         ("u", ib - b["lam"] * pd), ("D1", ep["D_A"]), ("D2", ep["D_B"])):
            pool[key].append(val)
    per = {k: np.array(v, float) for k, v in per.items()}
    pool = {k: np.concatenate(v) for k, v in pool.items()}
    return per, pool


def pooled_summary(pool, b, directional):
    ib, ls, cnt, dd = pool["ibar"], pool["log_s"], pool["count"], pool["dir"]
    k_chung = kappa(ib, ls)[0]
    k_chieu = kappa_by_dir(ib, ls, dd)[0] if directional else k_chung
    f_bin, f_smp, f_tot = floors_by_dir(ib, ls, cnt, dd if directional else np.zeros_like(dd))
    law = {}
    for d in (np.unique(dd) if directional else [0]):
        m = (dd == d) if directional else np.ones(len(ib), bool)
        t0 = b["h_dir"][int(d)] if directional else b["h_c"]
        f0 = float(np.mean(np.abs(ib[m] - t0) < 1.0) / 2.0)
        _, r = kappa(ib[m], ls[m])
        band = np.abs(ib[m] - t0) < 2.0
        n_cells = len(np.unique(np.round(ib[m][band], 9)))
        a1 = beta = k_b = pred = np.nan
        if band.sum() >= 30 and n_cells >= 3:
            x = np.vstack([np.ones(band.sum()), ib[m][band] - t0, r[band]]).T
            _, a1, beta = np.linalg.lstsq(x, pool["u"][m][band], rcond=None)[0]
            k_b = float(r[band].std())
            pred = f0 * beta**2 * k_b**2 / (2 * a1) if a1 > 0 else np.nan
        law[int(d)] = dict(weight=float(m.mean()), t0=t0, f0=f0, n=int(band.sum()), cells=n_cells, a1=float(a1),
                           beta=float(beta), k_b=float(k_b), pred=float(pred))
    pred_total = sum(v["weight"] * v["pred"] for v in law.values() if np.isfinite(v["pred"]))
    return dict(k_chung=k_chung, k_chieu=k_chieu, floor_bin=f_bin, floor_smp=f_smp, floor=f_tot, law=law,
                pred_pure=float(pred_total), p95_1=float(np.percentile(pool["D1"], 95)),
                p95_2=float(np.percentile(pool["D2"], 95)))


def verdict(gap, head):
    lo_a = ci_n(gap - f.M_SESOI_MS)
    lo_r = ci_n(gap - f.R_SESOI * head)
    if lo_a[0] - lo_a[1] > 0 and lo_r[0] - lo_r[1] > 0:
        return "CÓ Ý NGHĨA"
    if lo_a[0] + lo_a[1] < 0 or lo_r[0] + lo_r[1] < 0:
        return "KHÔNG ĐÁNG KỂ"
    return "CHƯA KẾT LUẬN"


# ---------------------------------------------------------------- các chế độ
def mode_anchor():
    name = ANCHOR["cell"]
    cell, stream = g.CELLS[name]
    eps_ms = f.EPS_OVER_S * cell.s_ms
    sim = lambda seeds, st: [episode(slot_path(s, st, 0, cell), slot_path(s, st, 1, cell), cell.s_ms, cell.k)
                             for s in seeds]
    eps = dict(cal=sim(f.CAL_SEEDS, stream), test=sim(f.TEST_SEEDS, stream),
               orc=sim(f.ORACLE_SEEDS, stream) + sim(f.ORACLE_SEEDS, stream + q.EXTRA))
    ref = g.simulate_pair(cell, psa_for(cell.k), f.TEST_SEEDS[0], stream)[0]
    same = all(np.array_equal(ref[k], eps["test"][0][k]) for k in ("rh_A", "D_A", "rh_B", "D_B", "Ihat_A"))
    b = build(eps, eps_ms, directional=False)
    per, pool = evaluate_test(eps["test"], b, eps_ms, directional=False)
    k_pool = kappa(pool["ibar"], pool["log_s"])[0]
    pure = ci_n(per["gain_K2"] - per["gain_SC"])
    print(f"ANCHOR — code f07 ở cấu hình f05c | ô {name} | khoá {stream} (+{q.EXTRA}) | thế giới trùng f04b: {same}")
    print(f"  λ = {b['lam']:.2f} | t₀ = {b['h_c']:.2f} | K2 − SC = {pure[0]:+.3f} ± {pure[1]:.3f} | κ̂ gộp = {k_pool:.3f}")
    printed = (round(b["lam"], 2) == ANCHOR["lam"] and round(b["h_c"], 2) == ANCHOR["t0"]
               and (round(pure[0], 3), round(pure[1], 3)) == ANCHOR["pure"] and round(k_pool, 3) == ANCHOR["k_pure"])
    ref_json = json.loads(F05C_JSON.read_text(encoding="utf-8"))[f"{name}/A0"]
    dev = max(abs(b["lam"] - ref_json["lam"]), abs(b["h_c"] - ref_json["t0"]), abs(pure[0] - ref_json["pure"][0]),
              abs(pure[1] - ref_json["pure"][1]), abs(k_pool - ref_json["k_pure"]))
    print(f"  Khớp chữ số in ra: {printed} | lệch tối đa so với f05c_results.json: {dev:.1e}")
    assert same and printed, "ANCHOR KHÔNG KHỚP — dừng, tìm lỗi trong phần code chung trước mọi chế độ khác"
    return dict(world_same=same, lam=b["lam"], t0=b["h_c"], pure=pure, k_pure=k_pool, max_dev_json=dev)


def mode_validity(cache):
    print(f"VALIDITY — chỉ calibration {SEEDS['cal'][0]}–{SEEDS['cal'][-1]} + oracle {SEEDS['orc'][0]}–"
          f"{SEEDS['orc'][-1]}; KHÔNG seed test, KHÔNG κ̂/gap | khoá {STREAM}")
    out, ok_all = {}, True
    eps_ms = f.EPS_OVER_S * PATH["A"].s_ms
    for w in WORLDS:
        eps = dict(cal=simulate_world(w, SEEDS["cal"], cache), orc=simulate_world(w, SEEDS["orc"], cache))
        b = build(eps, eps_ms, directional=True)
        sparse = b["oracle"].sparse_by_dir
        gates_ok = all(v <= ALPHA + 1e-9 for v in b["gates"].values()) and all(v < 0.01 for v in sparse.values())
        ok_all &= gates_ok
        r0, rd = b["rule0"], b["ruled"]
        print(f"\n[{w}] S0: {r0[1]} ngưỡng {r0[2]:.4g} (J cal {r0[3]:.3f}) | S0dir: {rd[1]} ngưỡng "
              f"({rd[2][0]:.4g}; {rd[2][1]:.4g}) (J cal {rd[3]:.3f}) | λ {b['lam']:.2f} | H_c {b['h_c']:.2f} | "
              f"H_dir ({b['h_dir'][1]:.2f} khe1→2; {b['h_dir'][0]:.2f} khe2→1)")
        print("   cổng harm (≤ α = 1%): " + " | ".join(f"{k} {100 * v:.3f}%" for k, v in b["gates"].items()))
        print("   báo, không cổng: " + " | ".join(f"{k} {100 * v:.3f}%" for k, v in b["reported"].items()))
        print(f"   ô thưa theo chiều (< 1%): " + " | ".join(f"chiều {k}: {100 * v:.2f}%" for k, v in sparse.items())
              + f" | tỉ lệ epoch cal ở khe 1: {b['dir_frac_cal']:.3f} | CỔNG {'ĐẠT' if gates_ok else 'KHÔNG ĐẠT'}")
        out[w] = dict(gates=b["gates"], reported=b["reported"], sparse=sparse, lam=b["lam"], h_c=b["h_c"],
                      h_dir=b["h_dir"], rule0=list(r0), ruled=list(rd), ok=gates_ok)
    print(f"\nVALIDITY TỔNG: {'ĐẠT' if ok_all else 'KHÔNG ĐẠT — dừng, không chạy outcome'}")
    return out


def run_outcome(worlds_eps, eps_ms):
    """Chung cho outcome và smoke: estimand, cổng, phép kiểm, ô 2×2."""
    res = {}
    for w, eps in worlds_eps.items():
        b = build(eps, eps_ms, directional=True)
        per, pool = evaluate_test(eps["test"], b, eps_ms, directional=True)
        res[w] = dict(b=b, per=per, summ=pooled_summary(pool, b, True))
    P = {w: r["per"] for w, r in res.items()}
    S = {w: r["summ"] for w, r in res.items()}

    print(f"\nBẢNG 1 — phân rã decision-level trên quỹ đạo S0dir (ms/epoch, CI95 t theo {len(P['AB']['headroom'])} seed)")
    for w in res:
        p = P[w]
        print(f"[{w}] headroom {txt(p['headroom'])} | S0dir {txt(p['gain_ref'])} | tâm SCdir − S0dir "
              f"{txt(p['gain_SCdir'] - p['gain_ref'])} | thuần K2 − SCdir {txt(p['gain_K2'] - p['gain_SCdir'])} | "
              f"an toàn {txt(p['gain_K2inf'] - p['gain_K2'])} | thông tin {txt(p['headroom'] - p['gain_K2inf'])}")
        print(f"      đối chiếu: S0 (decision-level) {txt(p['gain_S0dl'])} | SC {txt(p['gain_SC'])} | "
              f"harm test K2 {100 * p['harm_K2'].mean():.2f}% · S0dir {100 * p['harm_ref'].mean():.2f}% | "
              f"n_nan TB {p['n_nan'].mean():.1f}")

    print("\nBẢNG 2 — κ̂ (theo seed, CI) và gộp; sàn D6 của κ̂_chiều")
    for w in res:
        p, s = P[w], S[w]
        print(f"[{w}] κ̂_chung {txt(p['k_chung'])} (gộp {s['k_chung']:.3f}) | κ̂_chiều {txt(p['k_chieu'])} "
              f"(gộp {s['k_chieu']:.3f}; bỏ chiều {int(p['k_dropped'].sum())} lần) | sàn bin {s['floor_bin']:.3f}, "
              f"mẫu {s['floor_smp']:.3f}, tổng {s['floor']:.3f}")

    print("\nBẢNG 3 — kiểm thao tác và quỹ đạo")
    for w in res:
        p, s = P[w], S[w]
        print(f"[{w}] E[D₁] − E[D₂] {txt(p['ED1_minus_ED2'], 2)} ms | p95 {s['p95_1']:.1f}/{s['p95_2']:.1f} ms | "
              f"tỉ lệ epoch ở khe 1 {p['dir_frac'].mean():.3f} | D = J(S0) − J(S0dir) {txt(p['J_S0'] - p['J_S0dir'])} ms | "
              f"ô thưa theo chiều " + ", ".join(f"{100 * v:.2f}%" for v in res[w]["b"]["oracle"].sparse_by_dir.values()))

    gates = {}
    for w in res:
        p, b = P[w], res[w]["b"]
        diff = p["gain_K2"] - p["gain_ref"]
        se = diff.std(ddof=1) / np.sqrt(len(diff))
        gates[w] = {"harm cal": all(v <= ALPHA + 1e-9 for v in b["gates"].values()),
                    "ô thưa < 1% mỗi chiều": all(v < 0.01 for v in b["oracle"].sparse_by_dir.values()),
                    "K2 − S0dir ≥ −2SE": bool(diff.mean() >= -2 * se)}
    sym = P["AA"]["k_chung"] - P["AA"]["k_chieu"]
    m, h = ci_n(sym)
    gates["AA"]["đối xứng AA"] = bool((m - h <= 0 <= m + h) or abs(S["AA"]["k_chung"] - S["AA"]["k_chieu"]) < 0.02)
    print("\nCỔNG HỢP LỆ: " + " | ".join(f"{w}: " + ", ".join(f"{k} {'✓' if v else '✗'}" for k, v in gw.items())
                                     for w, gw in gates.items()))

    m1 = ci_n(P["AB"]["k_chung"] - P["AB"]["k_chieu"])
    m2 = ci_n(P["AB"]["k_chieu"] - P["AA"]["k_chieu"])
    v = ci_n(P["AB"]["gain_K2"] - P["AB"]["gain_ref"] - f.R_SESOI * P["AB"]["headroom"])
    d_ab, d_aa = ci_n(P["AB"]["J_S0"] - P["AB"]["J_S0dir"]), ci_n(P["AA"]["J_S0"] - P["AA"]["J_S0dir"])
    floor_sum = S["AB"]["floor"] + S["AA"]["floor"]
    tests = {
        "M1": m1[0] - m1[1] > 0,
        "M2": (m2[0] + m2[1] < 0) and abs(m2[0]) > floor_sum,
        "V": v[0] - v[1] > 0,
        "D": (d_ab[0] - d_ab[1] > 0) and (d_aa[0] - d_aa[1] <= 0 <= d_aa[0] + d_aa[1]),
    }
    print("\nPHÉP KIỂM (§2.6)")
    print(f"  M1 κ̂_chung(AB) − κ̂_chiều(AB)       = {m1[0]:+.3f} ± {m1[1]:.3f}  → {'ĐẠT' if tests['M1'] else 'KHÔNG ĐẠT'}")
    print(f"  M2 κ̂_chiều(AB) − κ̂_chiều(AA)       = {m2[0]:+.3f} ± {m2[1]:.3f}; tổng sàn {floor_sum:.3f} "
          f"→ {'ĐẠT' if tests['M2'] else 'KHÔNG ĐẠT'}")
    print(f"  V  (K2 − S0dir) − 0,10·headroom (AB) = {v[0]:+.3f} ± {v[1]:.3f} ms → {'ĐẠT' if tests['V'] else 'KHÔNG ĐẠT'}")
    print(f"  D  J(S0) − J(S0dir): AB {d_ab[0]:+.3f} ± {d_ab[1]:.3f}; AA {d_aa[0]:+.3f} ± {d_aa[1]:.3f} ms "
          f"→ {'ĐẠT' if tests['D'] else 'KHÔNG ĐẠT'}")
    for w in res:
        s, p = S[w], P[w]
        print(f"  L  [{w}] thuần dự đoán (D7 theo chiều) {s['pred_pure']:.3f} ms | quan sát K2 − SCdir "
              f"{txt(p['gain_K2'] - p['gain_SCdir'])} | VoIP (m, r) trên K2 − S0dir: "
              f"{verdict(p['gain_K2'] - p['gain_ref'], p['headroom'])}")
    cell = {(True, True): "(i)", (True, False): "(ii)", (False, True): "(iv)", (False, False): "(iii)"}[
        (tests["M2"], tests["V"])]
    valid = all(all(gw.values()) for gw in gates.values())
    print(f"\nÔ BẢNG 2×2: {cell} | cổng hợp lệ {'ĐẠT' if valid else 'KHÔNG ĐẠT — không diễn giải estimand oracle'} | "
          f"dự đoán tham chiếu và của tác giả: (ii)")
    store = {w: dict(per={k: v.tolist() for k, v in P[w].items()}, summary=S[w], lam=res[w]["b"]["lam"],
                     h_c=res[w]["b"]["h_c"], h_dir=res[w]["b"]["h_dir"], rule0=list(res[w]["b"]["rule0"]),
                     ruled=list(res[w]["b"]["ruled"]), gates_cal=res[w]["b"]["gates"],
                     sparse=res[w]["b"]["oracle"].sparse_by_dir) for w in res}
    store.update(tests=dict(M1=m1, M2=m2, V=v, D_AB=d_ab, D_AA=d_aa, floor_sum=floor_sum, passed=tests),
                 gates=gates, cell=cell, valid=valid)
    return store


def mode_outcome(cache):
    print(f"OUTCOME — {len(SEEDS['test'])} seed test {SEEDS['test'][0]}–{SEEDS['test'][-1]} | khoá {STREAM}")
    eps_ms = f.EPS_OVER_S * PATH["A"].s_ms
    worlds = {w: {k: simulate_world(w, SEEDS[k], cache) for k in ("cal", "test", "orc")} for w in WORLDS}
    return run_outcome(worlds, eps_ms)


def synthetic_ep(rng, scale):
    """Episode ngẫu nhiên đúng định dạng — KHÔNG phải thế giới F7; chỉ để chạy thử code."""
    rh1, rh2 = rng.uniform(0.6, 1.1, f.N_EPOCH), rng.uniform(0.6, 1.1, f.N_EPOCH)
    d1, d2 = rng.gamma(2.0, 10 * scale[0], f.N_EPOCH), rng.gamma(2.0, 10 * scale[1], f.N_EPOCH)
    c1, c2 = d1 * rng.uniform(0.7, 1.3, f.N_EPOCH), d2 * rng.uniform(0.7, 1.3, f.N_EPOCH)
    return dict(D_A=d1, D_B=d2, I_A=d1 - d2, Ihat_A=c1 - c2, Chat_A=c1, Chat_B=c2, rh_A=rh1, rh_B=rh2, n_nan=0, clip=0.0)


def mode_smoke():
    print("SMOKE — dữ liệu NGẪU NHIÊN tổng hợp, không DES, không thế giới F7; mọi con số VÔ NGHĨA")
    rng = np.random.default_rng(12345)
    scales = {"AA": (1.0, 1.0), "BB": (0.7, 0.7), "AB": (1.0, 0.7)}
    worlds = {w: {k: [synthetic_ep(rng, s) for _ in range(n)] for k, n in (("cal", 2), ("test", 4), ("orc", 8))}
              for w, s in scales.items()}
    return run_outcome(worlds, f.EPS_OVER_S * PATH["A"].s_ms)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("anchor", "validity", "outcome", "smoke"), required=True)
    mode, t0, cache = ap.parse_args().mode, time.time(), {}
    print(f"f07 | engine {g.ENGINE} | mode {mode} | tiền đăng ký: tag prereg-f7 (F7 §2 v2)")
    result = {"anchor": mode_anchor, "smoke": mode_smoke}[mode]() if mode in ("anchor", "smoke") \
        else {"validity": mode_validity, "outcome": mode_outcome}[mode](cache)
    if mode in ("anchor", "validity", "outcome"):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"f07_{mode}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False, default=float),
                                             encoding="utf-8")
    print(f"Thời gian {time.time() - t0:.0f} s", file=sys.stderr)
