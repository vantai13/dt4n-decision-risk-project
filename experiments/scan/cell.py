"""Chạy MỘT ô của bản đồ: nhiều seed → quỹ đạo tham chiếu → tune trên seed hiệu chỉnh → đo trên seed kiểm tra."""
import numpy as np
from scipy import stats

from experiments.scan.rules import (orient, s0_trajectory, tune_bucket_thresholds,
                                    tune_lambda, tune_lambda_realized, tune_threshold)
from experiments.scan.twin import DelayCurve, posterior, twin_view
from experiments.scan.world import PKT_BITS, simulate_world

RULES = ("S0", "Sage", "SC", "K2", "K2inf")
N_AGE_BUCKET = 4
_CURVES = {}


def twin_inputs(w, cell, curve, eps_ms):
    """Phần twin dùng chung cho mọi thế giới: từ (tải đo được, tuổi) của 2 path → Î_plug, Ī, p₋, p₊."""
    s_sec = PKT_BITS / (cell["mbps"] * 1e6)
    post = {}
    for name in "AB":
        p, o = cell[name], w[name]
        R = p["rho_bar"] * s_sec / p["T_tel"]                    # twin biết mô hình nhiễu đếm
        post[name] = posterior(o["rhohat"], o["age"] + cell["a"], p["T_tel"], cell["H"],
                               p["rho_bar"], p["sigma"], p["tau"], R)
    Ibar, pdn, pup = twin_view(curve, *post["A"], *post["B"], eps_ms)
    return dict(Iplug_A=curve(w["A"]["rhohat"]) - curve(w["B"]["rhohat"]),   # twin "ngây thơ": cắm số đo vào
                Ibar_A=Ibar, pdn_A=pdn, pup_A=pup, age_A=w["A"]["age"], age_B=w["B"]["age"])


def decisions(seed, cell, curve, eps_ms):
    """Thế giới của bộ quét: sự thật = T(tải TB khoảng giữ)."""
    w = simulate_world(seed, cell)
    return dict(twin_inputs(w, cell, curve, eps_ms),
                I_A=curve(w["A"]["G_true"]) - curve(w["B"]["G_true"]))      # sự thật (để chấm điểm)


def _pool(dicts):
    return {k: np.concatenate([d[k] for d in dicts]) for k in dicts[0]}


def get_curve(cell):
    s_ms = PKT_BITS / (cell["mbps"] * 1e6) * 1e3
    key = (cell["k"], round(s_ms, 9))
    if key not in _CURVES:
        _CURVES[key] = DelayCurve(cell["k"], s_ms)
    return _CURVES[key], s_ms


def run_cell(cell, cal_seeds, test_seeds):
    """Bộ quét: thế giới PSA + tune bằng kỳ vọng của twin (giữ NGUYÊN như lúc quét map v0)."""
    curve, s_ms = get_curve(cell)
    eps_ms = cell["eps_over_s"] * s_ms
    cal_raw = [decisions(s, cell, curve, eps_ms) for s in cal_seeds]
    test_raw = [decisions(s, cell, curve, eps_ms) for s in test_seeds]
    return evaluate_cell(cal_raw, test_raw, cell["alpha"], eps_ms, s_ms, tuning="expected")


def evaluate_cell(cal_raw, test_raw, alpha, eps_ms, s_ms, tuning="expected"):
    """Đánh giá trên các quyết định đã mô phỏng sẵn.
    tuning="expected": tune bằng kỳ vọng của twin (gain = Ī, harm = p₋)  — như bộ quét.
    tuning="realized": tune bằng kết quả THẬT trên seed hiệu chỉnh (gain = I, harm = 1[I < −ε])."""
    def targets(c):
        if tuning == "expected":
            return c["Ibar"], c["pdn"]
        return c["I"], (c["I"] < -eps_ms).astype(float)

    # 1) Quỹ đạo tham chiếu = quỹ đạo của S0 đã tune (lặp 2 vòng để ngưỡng và quỹ đạo khớp nhau)
    h0 = 0.0
    for _ in range(2):
        cal = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_raw])
        h0 = tune_threshold(cal["Iplug"], *targets(cal), alpha)
    cal = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_raw])
    g, hm = targets(cal)

    # 2) Tune các luật còn lại trên seed hiệu chỉnh (cùng ngân sách harm α)
    edges = np.quantile(cal["age"], np.linspace(0, 1, N_AGE_BUCKET + 1)[1:-1])
    th_age = tune_bucket_thresholds(cal["Iplug"], np.searchsorted(edges, cal["age"]), g, hm, alpha, N_AGE_BUCKET)
    h_c = tune_threshold(cal["Ibar"], g, hm, alpha)
    lam = (tune_lambda(cal["Ibar"], cal["pdn"], alpha) if tuning == "expected"
           else tune_lambda_realized(cal["Ibar"], cal["pdn"], g, hm, alpha))

    def act(o):
        return dict(S0=o["Iplug"] > h0, Sage=o["Iplug"] > th_age[np.searchsorted(edges, o["age"])],
                    SC=o["Ibar"] > h_c, K2=o["Ibar"] - lam * o["pdn"] > 0, K2inf=o["Ibar"] > 0)

    a_cal = act(cal)                                       # baseline "tốt nhất" chọn trên CALIBRATION
    best = max(("S0", "Sage", "SC"), key=lambda r: float(np.mean(a_cal[r] * g)))

    # 3) Đo trên seed kiểm tra, mỗi seed một dòng (đơn vị lặp lại = seed)
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
    for name, x in [("width", col("gain_K2") - col("gain_SC")),          # giá trị của ĐỘ RỘNG (cùng tâm)
                    ("vs_best", col("gain_K2") - col(f"gain_{best}")),   # K2 so với baseline tốt nhất
                    ("center", col("gain_SC") - col("gain_S0"))]:        # giá trị của TÂM (twin sửa tuổi)
        out[f"{name}_ms"], out[f"{name}_ci"] = mci(x)
        out[f"{name}_pct"] = 100 * float(x.mean() / hr.mean()) if hr.mean() > 0 else np.nan
    return out
