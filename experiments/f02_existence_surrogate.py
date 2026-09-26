"""f02 — F2: bài toán có tồn tại không? Surrogate PSA; oracle K2 cùng thông tin F chính; decision-level (K16).

Câu hỏi: gần điểm neo, ngưỡng tĩnh tốt nhất (K22) thua oracle K2 bao nhiêu ms so với headroom; ràng buộc harm có cắn?
SESOI đã khoá (log 2026-09-26, commit 504677e): m = 8,1 ms, r = 10%, quy tắc CI ba kết luận, ô chính P1, P2.

Thế giới surrogate (ĐỊNH HƯỚNG, không phải DES):
  - Hai path độc lập, mỗi path một link M/D/1/K; tải OU(ρ̄, σ, τ) rời rạc CHÍNH XÁC trên lưới DT.
  - Delay thật trên khoảng giữ = PSA: TB thời gian ở lại dừng T(ρ(s)) theo probe ĐƯỢC NHẬN (trọng số 1 − P_K).
    prop = 0 (triệt tiêu trong I_D; có ảnh hưởng tới ngưỡng tương đối — giới hạn đã biết).
  - F chính (K6): ρ̂ cửa sổ mới nhất của cur và alt (đếm Poisson), tuổi cố định, path hiện tại.
  - Luật tĩnh "hiện trạng vận hành" (K16, K22): tune trên seed calibration để tối thiểu TRỄ NGƯỜI DÙNG TRẢI QUA
    dọc quỹ đạo của chính nó, harm thực ≤ α. Quỹ đạo của nó là quỹ đạo tham chiếu.
  - Oracle chính = BIN (K10): E[I | ρ̂_cur, ρ̂_alt] và P(I < −ε | ·) ước lượng trên seed oracle DỌC quỹ đạo tham chiếu.
    Lý do: path hiện tại do luật tĩnh chọn từ số đo cũ nên MANG THÔNG TIN; oracle mô hình chỉ dùng cửa sổ mới nhất
    (nested MC, L1.2) bỏ sót thông tin đó (xem --mode check). Nested MC chỉ dùng cho đối chứng và kiểm tra.
Chạy: python experiments/f02_existence_surrogate.py --mode control|check|grid
Seed pilot (K13): calibration 9701–9708, test 9711–9718, oracle 9801–9999; luồng con: SeedSequence(seed, ô, biến thể).
"""
import argparse
import json
import time
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.signal import lfilter

from ndtrisk.theory.mdk import mdk

M_SESOI_MS, R_SESOI = 8.1, 0.10
ALPHA, EPS_OVER_S = 0.01, 0.5
PKT_BITS = 1512 * 8
DT, HOLD_STRIDE = 0.01, 5            # lưới thật 0,01 s; điểm khoảng giữ mỗi 0,05 s (cùng cho thật và oracle)
N_EPOCH, M_MC, N_BIN = 1500, 128, 20
CAL_SEEDS, TEST_SEEDS = tuple(range(9701, 9709)), tuple(range(9711, 9719))
ORACLE_SEEDS = tuple(range(9801, 10000))
C_FACTORS = (0.0, 0.25, 1.0)
T975 = stats.t.ppf(0.975, len(TEST_SEEDS) - 1)


@dataclass(frozen=True)
class Cell:
    name: str
    mbps: float
    k: int
    rho_bar: float
    sigma: float
    tau: float
    lag: float = 0.37            # t − t_m: TB CLEAN 0,369 s làm tròn lên lưới
    act: float = 0.05            # a: giả định
    win: float = 0.50
    hold: float = 0.50
    noise: bool = True

    @property
    def s_ms(self):
        return PKT_BITS / (self.mbps * 1e6) * 1e3


class PSA:
    """Đường cong dừng M/D/1/K từ mdk.py (L1.1), nội suy trên lưới ρ."""

    def __init__(self, k, rho_max=2.0, step=1e-3):
        self.grid = np.arange(0.0, rho_max + step / 2, step)
        res = [mdk(float(r), k) for r in self.grid]
        self.soj, self.loss = np.array([x.sojourn for x in res]), np.array([x.loss for x in res])

    def point(self, rho):
        return np.interp(np.clip(rho, 0, self.grid[-1]), self.grid, self.soj)

    def hold(self, rho_pts, w):
        r = np.clip(rho_pts, 0, self.grid[-1])
        acc = 1.0 - np.interp(r, self.grid, self.loss)
        return (w * acc * np.interp(r, self.grid, self.soj)).sum(-1) / (w * acc).sum(-1)


def trap_w(n):
    w = np.ones(n)
    if n > 1:
        w[0] = w[-1] = 0.5
    return w / w.sum()


def v_avg(L, sigma, tau):
    return sigma**2 if L == 0 else 2 * sigma**2 * (L / tau - 1 + np.exp(-L / tau)) / (L / tau) ** 2


def a_avg(L, tau):
    return 1.0 if L == 0 else (1 - np.exp(-L / tau)) / (L / tau)


def simulate(cell, psa, seed, cell_id, variant_id, with_mc=False):
    """Một seed: bảng theo epoch, hướng 'cur = A'. with_mc: thêm oracle mô hình (nested MC, chỉ cửa sổ mới nhất)."""
    rng_t, rng_n, rng_m = [np.random.default_rng(s)
                           for s in np.random.SeedSequence([seed, cell_id, variant_id]).spawn(3)]
    lag_n, act_n, win_n, hold_n = (round(v / DT) for v in (cell.lag, cell.act, cell.win, cell.hold))
    step_n, offset = max(hold_n, 1), lag_n + win_n
    n_steps = offset + N_EPOCH * step_n + act_n + hold_n + 1
    i_dec = offset + step_n * np.arange(N_EPOCH)
    win_idx = (i_dec - lag_n)[:, None] - np.arange(win_n, -1, -1)[None, :]
    hold_off = np.arange(0, hold_n + 1, HOLD_STRIDE) if hold_n > 0 else np.array([0])
    hold_idx = (i_dec + act_n)[:, None] + hold_off[None, :]
    w_win, w_hold = trap_w(win_idx.shape[1]), trap_w(len(hold_off))
    r_dt, S = np.exp(-DT / cell.tau), cell.s_ms * 1e-3
    out = {}
    for p in ("A", "B"):
        dev0 = cell.sigma * rng_t.standard_normal()
        e = cell.sigma * np.sqrt(1 - r_dt**2) * rng_t.standard_normal(n_steps - 1)
        rho = cell.rho_bar + np.concatenate([[dev0], lfilter([1.0], [1.0, -r_dt], e, zi=[r_dt * dev0])[0]])
        m_win = rho[win_idx] @ w_win
        noisy = cell.noise and cell.win > 0
        rho_hat = rng_n.poisson(cell.win * np.maximum(m_win, 0) / S) * S / cell.win if noisy else m_win
        rec = dict(d=psa.hold(rho[hold_idx], w_hold) * cell.s_ms, d_hat=psa.point(rho_hat) * cell.s_ms,
                   rho_hat=rho_hat, clip=float(np.mean((rho < 0) | (rho > psa.grid[-1]))))
        if with_mc:                                     # cập nhật tại t_m rồi dự báo (L1.2)
            R = cell.rho_bar * S / cell.win if noisy else 0.0
            cxy, vy = cell.sigma**2 * a_avg(cell.win, cell.tau), v_avg(cell.win, cell.sigma, cell.tau) + R
            x = cxy / vy * (rho_hat - cell.rho_bar)[:, None] + \
                np.sqrt(max(cell.sigma**2 - cxy**2 / vy, 0)) * rng_m.standard_normal((N_EPOCH, M_MC))
            r_g, r_h = np.exp(-(lag_n + act_n) * DT / cell.tau), np.exp(-HOLD_STRIDE * DT / cell.tau)
            pts = np.empty((N_EPOCH, M_MC, len(hold_off)))
            pts[..., 0] = r_g * x + cell.sigma * np.sqrt(1 - r_g**2) * rng_m.standard_normal(x.shape)
            for j in range(1, len(hold_off)):
                pts[..., j] = r_h * pts[..., j - 1] + cell.sigma * np.sqrt(1 - r_h**2) * rng_m.standard_normal(x.shape)
            rec["d_mc"] = psa.hold(cell.rho_bar + pts, w_hold) * cell.s_ms
        out[p] = rec
    ep = dict(D_A=out["A"]["d"], D_B=out["B"]["d"], I_A=out["A"]["d"] - out["B"]["d"],
              Ihat_A=out["A"]["d_hat"] - out["B"]["d_hat"], Chat_A=out["A"]["d_hat"], Chat_B=out["B"]["d_hat"],
              rh_A=out["A"]["rho_hat"], rh_B=out["B"]["rho_hat"], clip=max(out[p]["clip"] for p in "AB"))
    if with_mc:
        delta, eps_ms = out["A"]["d_mc"] - out["B"]["d_mc"], EPS_OVER_S * cell.s_ms
        ep.update(mcIbar_A=delta.mean(1), mcSd=delta.std(1),
                  mcPdn_A=(delta < -eps_ms).mean(1), mcPup_A=(delta > eps_ms).mean(1))
    return ep


def static_run(ep, kind, thr):
    """Chạy luật tĩnh TUẦN TỰ cho nhiều ngưỡng cùng lúc → (đổi, cur_is_A), dạng (n_thr, N)."""
    thr = np.atleast_1d(thr)
    cur = np.ones(len(thr), bool)
    act, hist = np.zeros((len(thr), N_EPOCH), bool), np.zeros((len(thr), N_EPOCH), bool)
    for e in range(N_EPOCH):
        hist[:, e] = cur
        ihat = np.where(cur, ep["Ihat_A"][e], -ep["Ihat_A"][e])
        score = ihat if kind == "abs" else ihat / np.where(cur, ep["Chat_A"][e], ep["Chat_B"][e])
        act[:, e] = sw = score > thr                       # hoà thì GIỮ
        cur = cur ^ sw
    return act, hist


def orient(ep, cur_a):
    sg = np.where(cur_a, 1.0, -1.0)
    o = dict(I=sg * ep["I_A"], Ihat=sg * ep["Ihat_A"], D_cur=np.where(cur_a, ep["D_A"], ep["D_B"]),
             rh_cur=np.where(cur_a, ep["rh_A"], ep["rh_B"]), rh_alt=np.where(cur_a, ep["rh_B"], ep["rh_A"]))
    if "mcIbar_A" in ep:
        o.update(mcIbar=sg * ep["mcIbar_A"], mcSd=ep["mcSd"], mcPdn=np.where(cur_a, ep["mcPdn_A"], ep["mcPup_A"]))
    return o


def tune_static(cal, kind, c, eps_ms):
    """Tối thiểu J = TB(D_cur − a·(I − c)) (trễ đã trải qua + c·tỉ lệ đổi) dọc quỹ đạo CỦA CHÍNH luật, harm thực ≤ α.
    KHÔNG tune bằng gain decision-level trên quỹ đạo riêng: gain đó thưởng cho việc nấn ná trên path tệ."""
    key = (lambda ep: ep["Ihat_A"]) if kind == "abs" else (lambda ep: ep["Ihat_A"] / ep["Chat_A"])

    def evaluate(grid):
        J, H = np.zeros(len(grid)), np.zeros(len(grid))
        for ep in cal:
            act, cur = static_run(ep, kind, grid)
            I = np.where(cur, 1.0, -1.0) * ep["I_A"][None, :]
            J += (np.where(cur, ep["D_A"], ep["D_B"]) - act * (I - c)).mean(1) / len(cal)
            H += (act * (I < -eps_ms)).mean(1) / len(cal)
        return J, H

    grid = np.unique(np.concatenate([[0.0], np.quantile(np.concatenate([key(ep) for ep in cal]),
                                                        np.linspace(0.3, 0.9995, 200))]))
    J, H = evaluate(grid)
    if not (H <= ALPHA).any():
        return np.inf, np.inf
    i = int(np.argmin(np.where(H <= ALPHA, J, np.inf)))
    fine = np.linspace(grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)], 101)
    J2, H2 = evaluate(fine)
    j = int(np.argmin(np.where(H2 <= ALPHA, J2, np.inf)))
    return (fine[j], J2[j]) if J2[j] < J[i] else (grid[i], J[i])      # chỉ thay khi tốt hơn hẳn


class BinOracle:
    """Oracle bin (K10): thống kê của I thật theo ô phân vị (ρ̂_cur, ρ̂_alt), ước lượng DỌC quỹ đạo tham chiếu."""

    def __init__(self, orients, eps_ms, n_bin=N_BIN, min_count=30):
        rc = np.concatenate([o["rh_cur"] for o in orients])
        ra = np.concatenate([o["rh_alt"] for o in orients])
        I = np.concatenate([o["I"] for o in orients])
        self.edges = np.unique(np.quantile(np.concatenate([rc, ra]), np.linspace(0, 1, n_bin + 1)))
        nb = len(self.edges) - 1
        idx = self._idx(rc) * nb + self._idx(ra)
        cnt = np.bincount(idx, minlength=nb * nb).astype(float)
        s1 = np.bincount(idx, I, nb * nb)
        s2 = np.bincount(idx, I * I, nb * nb)
        sdn = np.bincount(idx, (I < -eps_ms).astype(float), nb * nb)
        self.min_count, self.nb = min_count, nb
        g_mean, g_pdn = I.mean(), (I < -eps_ms).mean()
        with np.errstate(invalid="ignore", divide="ignore"):
            self.ibar = np.where(cnt >= min_count, s1 / cnt, np.nan)
            self.pdn = np.where(cnt >= min_count, sdn / cnt, np.nan)
            self.sd = np.where(cnt >= min_count, np.sqrt(np.maximum(s2 / cnt - (s1 / cnt) ** 2, 0)), np.nan)
        self.frac_sparse = float(np.mean(cnt[idx] < min_count))   # tỉ lệ epoch rơi vào ô thưa
        # ô thưa: dùng giá trị TB toàn cục — báo tỉ lệ, không giấu
        for arr, gval in ((self.ibar, g_mean), (self.pdn, g_pdn), (self.sd, I.std())):
            arr[np.isnan(arr)] = gval

    def _idx(self, x):
        return np.clip(np.searchsorted(self.edges, x, side="right") - 1, 0, len(self.edges) - 2)

    def predict(self, o):
        k = self._idx(o["rh_cur"]) * self.nb + self._idx(o["rh_alt"])
        return self.ibar[k], self.pdn[k], self.sd[k]


def tune_lambda(preds, c):
    def harm(lam):
        return np.mean([np.mean((ib - lam * pd > c) * pd) for ib, pd in preds])
    if harm(0.0) <= ALPHA:
        return 0.0
    lo, hi = 0.0, 1.0
    while harm(hi) > ALPHA:
        hi *= 2
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if harm(mid) <= ALPHA else (mid, hi)
    return hi


def h2_indices(o, ibar, pdn, sd, lam, c):
    u = ibar - lam * pdn
    ec = ibar > c
    ihat_ec, u_ec = o["Ihat"][ec], u[ec]
    # Spearman không xác định khi một hạng là hằng; quy ước 0 vì không quan sát được đảo thứ tự.
    degenerate = ec.sum() < 3 or np.ptp(ihat_ec) == 0 or np.ptp(u_ec) == 0
    rd = 0.0 if degenerate else 1.0 - stats.spearmanr(ihat_ec, u_ec).statistic
    edges = np.quantile(o["Ihat"], np.linspace(0, 1, 21))
    b = np.clip(np.searchsorted(edges, o["Ihat"], side="right") - 1, 0, 19)
    ls = np.log(np.maximum(sd, 1e-9))
    groups = [(ls[b == k].std(), (b == k).sum()) for k in range(20) if (b == k).sum() > 1]
    sdls = float(np.average([g[0] for g in groups], weights=[g[1] for g in groups]))
    a_k2 = u > c                                          # self_gap_twin (twin = oracle dưới M0: kiểm chứng)
    budget, order = np.mean(a_k2 * pdn), np.argsort(-o["Ihat"])
    feas = (np.cumsum(pdn[order]) <= budget * len(order) + 1e-12) & (o["Ihat"][order] > c)
    a_st = np.zeros(len(order), bool)
    a_st[order[:int(np.argmin(feas)) if not feas.all() else len(order)]] = True
    return rd, sdls, float(np.mean(a_k2 * (ibar - c)) - np.mean(a_st * (ibar - c)))


def ci(x):
    x = np.asarray(x, float)
    return float(x.mean()), float(T975 * x.std(ddof=1) / np.sqrt(len(x)))


def run_cell(cell, cell_id, variant_id, cache, oracle="bin"):
    psa = cache.setdefault(cell.k, PSA(cell.k))
    mc = oracle == "mc"
    cal = [simulate(cell, psa, s, cell_id, variant_id, mc) for s in CAL_SEEDS]
    test = [simulate(cell, psa, s, cell_id, variant_id, mc) for s in TEST_SEEDS]
    orc = [] if mc else [simulate(cell, psa, s, cell_id, variant_id) for s in ORACLE_SEEDS]
    eps_ms, results = EPS_OVER_S * cell.s_ms, {}
    for cf in C_FACTORS:
        c = cf * cell.s_ms
        tuned = {kd: tune_static(cal, kd, c, eps_ms) for kd in ("abs", "rel")}
        kind = min(tuned, key=lambda kd: tuned[kd][1])
        thr = tuned[kind][0]
        ref = lambda ep: orient(ep, static_run(ep, kind, thr)[1][0])
        if mc:
            predict = lambda o: (o["mcIbar"], o["mcPdn"], o["mcSd"])
            sparse = 0.0
        else:
            bo = BinOracle([ref(ep) for ep in orc], eps_ms)
            predict, sparse = bo.predict, bo.frac_sparse
        lam = tune_lambda([predict(ref(ep))[:2] for ep in cal], c)
        rows = []
        for ep in test:
            act, cur = static_run(ep, kind, thr)
            o = orient(ep, cur[0])
            ibar, pdn, sd = predict(o)
            a_st, a_k2, a_inf = act[0], ibar - lam * pdn > c, ibar > c
            g = lambda a: float(np.mean(a * (o["I"] - c)))
            rd, sdls, sgt = h2_indices(o, ibar, pdn, sd, lam, c)
            rows.append(dict(gain_static=g(a_st), gain_k2=g(a_k2), gain_k2_inf=g(a_inf),
                             headroom=float(np.mean(np.maximum(o["I"] - c, 0))),
                             harm_static=float(np.mean(a_st * (o["I"] < -eps_ms))),
                             harm_k2=float(np.mean(a_k2 * (o["I"] < -eps_ms))),
                             harm_k2_exp=float(np.mean(a_k2 * pdn)),
                             frac_harm_possible=float(np.mean(o["I"] < -eps_ms)),
                             oracle_bias=float(np.mean(o["I"] - ibar)), switch_static=float(a_st.mean()),
                             rd_score=rd, sd_log_s_cond=sdls, self_gap_twin=sgt))
        agg = {k_: ci([r[k_] for r in rows]) for k_ in rows[0]}
        gaps = np.array([r["gain_k2"] - r["gain_static"] for r in rows])
        heads = np.array([r["headroom"] for r in rows])
        agg.update(gap=ci(gaps), d_abs=ci(gaps - M_SESOI_MS), d_rel=ci(gaps - R_SESOI * heads),
                   price_of_safety=ci([r["gain_k2_inf"] - r["gain_k2"] for r in rows]))
        lo = lambda k_: agg[k_][0] - agg[k_][1]
        hi = lambda k_: agg[k_][0] + agg[k_][1]
        verdict = ("CÓ Ý NGHĨA" if lo("d_abs") > 0 and lo("d_rel") > 0 else
                   "KHÔNG ĐÁNG KỂ" if hi("d_abs") < 0 or hi("d_rel") < 0 else "CHƯA KẾT LUẬN")
        results[cf] = dict(static_kind=kind, static_thr=float(thr), lam=float(lam), verdict=verdict,
                           frac_sparse_bins=sparse, clip=max(ep["clip"] for ep in test), **agg)
    return results


GRID = [Cell(f"K{k}_r{rb}_{tag}", 4, k, rb, sg, ta)
        for k in (11, 100) for rb in (0.5, 0.7, 0.85, 0.95)
        for tag, sg, ta in (("s03t10", 0.03, 10.0), ("s10t2", 0.10, 2.0))]
PRIMARY = {"P1": Cell("P1", 4, 11, 0.85, 0.03, 10.0), "P2": Cell("P2", 4, 100, 0.95, 0.10, 2.0)}


def variants(cell):
    return {"base": cell, "age_only": replace(cell, noise=False), "noise_only": replace(cell, lag=0.0, act=0.0),
            "control": replace(cell, lag=0.0, act=0.0, win=0.0, hold=0.0, noise=False)}


def check_mode(cache):
    """Ô NGOÀI lưới. Chỉ in phép kiểm hợp lệ của oracle, KHÔNG in gain/gap."""
    cell = Cell("check", 4, 30, 0.80, 0.05, 5.0)
    psa = cache.setdefault(cell.k, PSA(cell.k))
    eps_ms = EPS_OVER_S * cell.s_ms
    test = [simulate(cell, psa, s, 999, 0, True) for s in TEST_SEEDS]
    kind, thr = "abs", 0.0
    rng = np.random.default_rng(123)
    for label, refn in (("tham chiếu NGẪU NHIÊN", lambda ep: rng.random(N_EPOCH) < 0.5),
                        ("tham chiếu = luật tĩnh", lambda ep: static_run(ep, kind, thr)[1][0])):
        bias, pexp, preal = [], [], []
        for ep in test:
            o = orient(ep, refn(ep))
            sel = o["mcIbar"] > 0                             # tập 'đổi' của luật Ī > 0
            bias.append(np.mean(o["I"] - o["mcIbar"]))
            pexp.append(np.mean(sel * o["mcPdn"]))
            preal.append(np.mean(sel * (o["I"] < -eps_ms)))
        b, pe, pr = ci(bias), ci(pexp), ci(preal)
        print(f"[check] nested MC, {label:24s}: lệch TB(I − Ī) = {b[0]:+.3f} ± {b[1]:.3f} ms | "
              f"harm dự đoán {pe[0]:.4f} vs thực {pr[0]:.4f} ± {pr[1]:.4f}")
    orc = [simulate(cell, psa, s, 999, 0) for s in ORACLE_SEEDS]
    bo = BinOracle([orient(ep, static_run(ep, kind, thr)[1][0]) for ep in orc], eps_ms)
    bias, pexp, preal = [], [], []
    for ep in test:
        o = orient(ep, static_run(ep, kind, thr)[1][0])
        ib, pd, _ = bo.predict(o)
        sel = ib > 0
        bias.append(np.mean(o["I"] - ib)); pexp.append(np.mean(sel * pd)); preal.append(np.mean(sel * (o["I"] < -eps_ms)))
    b, pe, pr = ci(bias), ci(pexp), ci(preal)
    print(f"[check] oracle BIN,  {'tham chiếu = luật tĩnh':24s}: lệch TB(I − Ī) = {b[0]:+.3f} ± {b[1]:.3f} ms | "
          f"harm dự đoán {pe[0]:.4f} vs thực {pr[0]:.4f} ± {pr[1]:.4f} | ô thưa {bo.frac_sparse:.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("control", "check", "grid"), required=True)
    mode, cache, t0 = ap.parse_args().mode, {}, time.time()
    if mode == "control":
        for name, cell in PRIMARY.items():                 # twin biết đúng I_D ⇒ khoảng cách phải = 0
            r = run_cell(variants(cell)["control"], 900 + int(name[1]), 3, cache, oracle="mc")[0.0]
            print(f"[control {name}] gap = {r['gap'][0]:+.2e} ± {r['gap'][1]:.1e} ms; λ = {r['lam']:.3g}; "
                  f"luật tĩnh {r['static_kind']} ngưỡng {r['static_thr']:.3g}")
    elif mode == "check":
        check_mode(cache)
    else:
        out_dir = Path("experiments/results/f02")
        out_dir.mkdir(parents=True, exist_ok=True)
        allres = {}
        for cid, cell in enumerate(GRID):
            allres[cell.name] = res = run_cell(cell, cid, 0, cache)
            r = res[0.0]
            print(f"{cell.name:16s} gap {r['gap'][0]:+7.3f}±{r['gap'][1]:.3f} | head {r['headroom'][0]:7.3f} | "
                  f"{r['static_kind']} | λ {r['lam']:6.2f} | harm_pos {r['frac_harm_possible'][0]:.3f} | "
                  f"bias {r['oracle_bias'][0]:+.2f} | rd {r['rd_score'][0]:.3f} sdls {r['sd_log_s_cond'][0]:.3f} "
                  f"sgt {r['self_gap_twin'][0]:+.3f}")
        for name, cell in PRIMARY.items():
            for vid, (vname, vcell) in enumerate(variants(cell).items()):
                res = run_cell(vcell, 900 + int(name[1]), vid, cache, oracle="mc" if vname == "control" else "bin")
                allres[f"{name}_{vname}"] = res
                r = res[0.0]
                print(f"{name}/{vname:10s} gap {r['gap'][0]:+7.3f}±{r['gap'][1]:.3f} | D_abs {r['d_abs'][0]:+.3f}"
                      f"±{r['d_abs'][1]:.3f} | D_rel {r['d_rel'][0]:+.3f}±{r['d_rel'][1]:.3f} | {r['verdict']}")
        cells = [c_.name for c_ in GRID]
        gap = [allres[n][0.0]["gap"][0] for n in cells]
        for ind in ("rd_score", "sd_log_s_cond", "self_gap_twin"):
            rho_s = stats.spearmanr([allres[n][0.0][ind][0] for n in cells], gap).statistic
            print(f"Spearman({ind}, gap) qua {len(cells)} ô = {rho_s:+.3f}")
        (out_dir / "f02_results.json").write_text(json.dumps(
            {k_: {str(c_): v for c_, v in res.items()} for k_, res in allres.items()}, indent=1, ensure_ascii=False))
        print(f"Thời gian {time.time() - t0:.0f} s; đầy đủ (mọi c): experiments/results/f02/f02_results.json")
