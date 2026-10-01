"""Chạy MỘT ô: nhiều seed → quỹ đạo tham chiếu → tune → đo trên seed kiểm tra."""
import numpy as np
from scipy import stats

from experiments.scan.rules import (orient, s0_trajectory, tune_bucket_thresholds,
                                    tune_lambda, tune_threshold)
from experiments.scan.twin import DelayCurve, posterior, twin_view
from experiments.scan.world import PKT_BITS, simulate_world

RULES = ("S0", "Sage", "SC", "K2", "K2inf")
N_AGE_BUCKET = 4
_CURVES = {}


def decisions(seed, cell, curve, eps_ms):
    """Mọi thứ cần cho từng quyết định, nhìn từ góc 'A so với B'."""
    w = simulate_world(seed, cell)
    s_sec = PKT_BITS / (cell["mbps"] * 1e6)
    post = {}
    for name in "AB":
        p, o = cell[name], w[name]
        R = p["rho_bar"] * s_sec / p["T_tel"]
        post[name] = posterior(o["rhohat"], o["age"] + cell["a"], p["T_tel"], cell["H"],
                               p["rho_bar"], p["sigma"], p["tau"], R)
    Ibar, pdn, pup = twin_view(curve, *post["A"], *post["B"], eps_ms)
    return dict(Iplug_A=curve(w["A"]["rhohat"]) - curve(w["B"]["rhohat"]),
                Ibar_A=Ibar, pdn_A=pdn, pup_A=pup,
                I_A=curve(w["A"]["G_true"]) - curve(w["B"]["G_true"]),
                age_A=w["A"]["age"], age_B=w["B"]["age"])


def _pool(dicts):
    return {k: np.concatenate([d[k] for d in dicts]) for k in dicts[0]}


def run_cell(cell, cal_seeds, test_seeds):
    s_ms = PKT_BITS / (cell["mbps"] * 1e6) * 1e3
    key = (cell["k"], round(s_ms, 9))
    if key not in _CURVES:
        _CURVES[key] = DelayCurve(cell["k"], s_ms)
    curve, eps_ms, alpha = _CURVES[key], cell["eps_over_s"] * s_ms, cell["alpha"]
    cal_raw = [decisions(s, cell, curve, eps_ms) for s in cal_seeds]
    test_raw = [decisions(s, cell, curve, eps_ms) for s in test_seeds]

    h0 = 0.0
    for _ in range(2):
        cal = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_raw])
        h0 = tune_threshold(cal["Iplug"], cal["Ibar"], cal["pdn"], alpha)
    cal = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_raw])

    edges = np.quantile(cal["age"], np.linspace(0, 1, N_AGE_BUCKET + 1)[1:-1])
    th_age = tune_bucket_thresholds(cal["Iplug"], np.searchsorted(edges, cal["age"]),
                                    cal["Ibar"], cal["pdn"], alpha, N_AGE_BUCKET)
    h_c = tune_threshold(cal["Ibar"], cal["Ibar"], cal["pdn"], alpha)
    lam = tune_lambda(cal["Ibar"], cal["pdn"], alpha)

    def act(o):
        return dict(S0=o["Iplug"] > h0, Sage=o["Iplug"] > th_age[np.searchsorted(edges, o["age"])],
                    SC=o["Ibar"] > h_c, K2=o["Ibar"] - lam * o["pdn"] > 0, K2inf=o["Ibar"] > 0)

    a_cal = act(cal)
    best = max(("S0", "Sage", "SC"), key=lambda r: float(np.mean(a_cal[r] * cal["Ibar"])))

    rows = []
    for d in test_raw:
        o = orient(d, s0_trajectory(d["Iplug_A"], h0))
        a = act(o)
        harmful = o["I"] < -eps_ms
        row = dict(headroom=float(np.mean(np.maximum(o["I"], 0.0))))
        for r in RULES:
            row[f"gain_{r}"] = float(np.mean(a[r] * o["I"]))
            row[f"harm_{r}"] = float(np.mean(a[r] & harmful))
        rows.append(row)
    return summarize(rows, best, s_ms)


def summarize(rows, best, s_ms):
    n = len(rows)
    t = stats.t.ppf(0.975, n - 1)
    col = lambda k: np.array([r[k] for r in rows])

    def mci(x):
        return float(x.mean()), float(t * x.std(ddof=1) / np.sqrt(n))

    hr = col("headroom")
    out = dict(s_ms=s_ms, best_baseline=best, headroom=float(hr.mean()))
    for r in RULES:
        out[f"gain_{r}"] = float(col(f"gain_{r}").mean())
        out[f"harm_{r}"] = float(col(f"harm_{r}").mean())
    for name, x in [("width", col("gain_K2") - col("gain_SC")),
                    ("vs_best", col("gain_K2") - col(f"gain_{best}")),
                    ("center", col("gain_SC") - col("gain_S0"))]:
        out[f"{name}_ms"], out[f"{name}_ci"] = mci(x)
        out[f"{name}_pct"] = 100 * float(x.mean() / hr.mean()) if hr.mean() > 0 else np.nan
    return out
