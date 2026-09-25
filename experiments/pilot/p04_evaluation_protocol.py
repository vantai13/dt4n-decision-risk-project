# ─── PROVENANCE (2026-09-25, Phase 0 v2 / L0.5) ──────────────────────────
# Tạo bởi : Claude (AI) theo yêu cầu tác giả, khi soạn L0.5; tác giả chạy lại và kiểm
# Sinh ra : experiments/pilot/results/p04_evaluation_protocol_output.txt
# Trích ở : 05_evaluation_protocol.md v1 (mục 2, 3); ADR K16
# Trạng thái: PILOT LÝ THUYẾT (exploratory) — KHÔNG phải bằng chứng RQ1/RQ2
# Seed    : 9105–9114 (chỉ dùng cho pilot này)
# Chạy lại: python experiments/pilot/p04_evaluation_protocol.py   (~30 s)
# ───────────────────────────────────────────────────────────────────────
"""P04 — PILOT LÝ THUYẾT (EXPLORATORY). Kiểm hai khẳng định của L0.5; KHÔNG phải bằng chứng RQ1/RQ2.

(1) Khi mỗi luật tự đi quỹ đạo riêng (trajectory-level), các luật gặp tập quyết định khác nhau;
    decision-level (cùng đường hiện tại cho mọi luật) mới cho so sánh sạch.
(2) "Oracle" chỉ là cận trên nếu thấy ít nhất những gì luật thấy: một luật dùng 2 cửa sổ telemetry
    có thể thắng oracle chỉ dùng 1 cửa sổ.

Thế giới: 2 đường, tải mỗi đường AR(1) theo epoch; delay T(ρ) = prop + 1/(1 − ρ) (đơn vị S, M/M/1, chặn 0,98).
Telemetry: y = ρ(e − L) + nhiễu đếm. Xác suất có điều kiện tính CHÍNH XÁC bằng điều kiện hoá Gauss rồi Monte Carlo.
Seed 9105–9114: chỉ dùng cho pilot này.
"""

import numpy as np

N, M, L = 40_000, 400, 2
EPS, ALPHA, KAPPA = 0.5, 0.01, 0.01
PHI = np.exp(-0.1)
PATHS = {
    "A": dict(mu=0.80, sig=0.06, prop=0.0),
    "B": dict(mu=0.70, sig=0.03, prop=1.5),
}
SIG_N = 0.03


def delay(rho, prop):
    return prop + 1.0 / (1.0 - np.minimum(rho, 0.98))


def simulate(rng):
    rho, y = {}, {}
    for k, p in PATHS.items():
        x = np.empty(N)
        x[0] = rng.normal(0, p["sig"])
        e = rng.normal(0, p["sig"] * np.sqrt(1 - PHI**2), N)
        for t in range(1, N):
            x[t] = PHI * x[t - 1] + e[t]
        rho[k] = p["mu"] + x
        y[k] = rho[k] + rng.normal(0, SIG_N, N)
    return rho, y


def posterior_weights(sig, lags):
    """Hệ số hồi quy và phương sai của x(e) | y(e-lag), lag in lags."""
    lags = np.asarray(lags)
    c_yy = sig**2 * PHI ** np.abs(lags[:, None] - lags[None, :]) + SIG_N**2 * np.eye(len(lags))
    c_xy = sig**2 * PHI**lags
    w = np.linalg.solve(c_yy, c_xy)
    return w, sig**2 - c_xy @ w


def probabilities(rho, y, lags, rng):
    """Î, p+, p- cho quyết định đổi A sang B, dùng thông tin y tại các độ trễ lags."""
    idx = np.arange(max(lags), N)
    samp, plug = {}, {}
    for k, p in PATHS.items():
        w, v = posterior_weights(p["sig"], lags)
        m = p["mu"] + sum(wi * (y[k][idx - lag] - p["mu"]) for wi, lag in zip(w, lags))
        plug[k] = delay(m, p["prop"])
        samp[k] = delay(m[:, None] + np.sqrt(v) * rng.normal(size=(len(idx), M)), p["prop"])
    imp = samp["A"] - samp["B"]
    out = np.full((3, N), np.nan)
    out[0, idx] = plug["A"] - plug["B"]
    out[1, idx] = (imp > EPS).mean(1)
    out[2, idx] = (imp < -EPS).mean(1)
    return out


def orient(q, cur_is_a):
    """Đổi hướng khi đường hiện tại là B: Î thành -Î, p+ đổi p-."""
    i_hat = np.where(cur_is_a, q[0], -q[0])
    return i_hat, np.where(cur_is_a, q[1], q[2]), np.where(cur_is_a, q[2], q[1])


def rates(sw, true_i):
    return np.mean(sw & (true_i < -EPS)), np.mean(~sw & (true_i > EPS)), sw.mean()


def calibrate(kind, q, cur, true_i):
    """Tiêu chí K2: min missed + kappa*switch, harm <= alpha; xác suất dùng KKT."""
    i_hat, pu, pd = orient(q, cur)
    if kind == "fixed":
        best, arg = np.inf, None
        for h in np.quantile(i_hat, np.linspace(0, 1, 401)):
            harm, missed, rate = rates(i_hat > h, true_i)
            if harm <= ALPHA and missed + KAPPA * rate < best:
                best, arg = missed + KAPPA * rate, h
        return arg
    lam_ok = lambda lam: rates((pu - lam * pd) > KAPPA, true_i)[0] <= ALPHA
    if lam_ok(0.0):
        return 0.0
    lo, hi = 0.0, 1e4
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if lam_ok(mid) else (mid, hi)
    return hi


def decide(kind, par, q, cur):
    i_hat, pu, pd = orient(q, cur)
    return i_hat > par if kind == "fixed" else (pu - par * pd) > KAPPA


def trajectory(kind, par, q, idx, true_ab, delays):
    """Luật tự đi quỹ đạo riêng, bắt đầu ở A. Trả về trạng thái, J, delay TB."""
    cur = True
    states, sw, ti, dl = [], [], [], []
    for e in idx:
        states.append(cur)
        s = bool(decide(kind, par, q[:, [e]], np.array([cur]))[0])
        sw.append(s)
        ti.append(true_ab[e] if cur else -true_ab[e])
        cur = (not cur) if s else cur
        dl.append(delays["A"][e] if cur else delays["B"][e])
    h, m, r = rates(np.array(sw), np.array(ti))
    return np.array(states), m + KAPPA * r, float(np.mean(dl))


def one_seed(seed):
    rng = np.random.default_rng(seed)
    rho, y = simulate(rng)
    delays = {k: delay(rho[k], p["prop"]) for k, p in PATHS.items()}
    true_ab = delays["A"] - delays["B"]
    q1 = probabilities(rho, y, [L], rng)
    q2 = probabilities(rho, y, [L, L + 1], rng)
    valid = np.arange(L + 2, N)
    cal, test = valid[: len(valid) // 2], valid[len(valid) // 2 :]
    rand_cur = rng.random(N) < 0.5
    flip = lambda st, idx: np.where(st, true_ab[idx], -true_ab[idx])
    h0 = calibrate("fixed", q1[:, cal], rand_cur[cal], flip(rand_cur[cal], cal))
    refs = {
        "ngẫu nhiên": (rand_cur[cal], rand_cur[test]),
        "thực tế": (
            trajectory("fixed", h0, q1, cal, true_ab, delays)[0],
            trajectory("fixed", h0, q1, test, true_ab, delays)[0],
        ),
    }
    rules = {"fix": ("fixed", q1), "orc": ("odds", q1), "ext": ("odds", q2)}
    row = {}
    for ref_name, (st_cal, st_test) in refs.items():
        for name, (kind, q) in rules.items():
            par = calibrate(kind, q[:, cal], st_cal, flip(st_cal, cal))
            h, m, r = rates(decide(kind, par, q[:, test], st_test), flip(st_test, test))
            _, j_tr, d_tr = trajectory(kind, par, q, test, true_ab, delays)
            row[(ref_name, name)] = (m + KAPPA * r, j_tr, d_tr)
    return row


if __name__ == "__main__":
    seeds = range(9105, 9115)
    rows = [one_seed(s) for s in seeds]
    print(f"N = {N}, M = {M}, L = {L}, ε = {EPS}, α = {ALPHA:.0%}, κ = {KAPPA}; seed {seeds[0]}–{seeds[-1]}")
    print("fix = tĩnh H (F chính); orc = oracle (F chính); ext = odds (F mở rộng, 2 cửa sổ)")
    print("J_dl: decision-level trên nửa test; J_tr, delay: trajectory-level (mỗi luật tự đi, bắt đầu ở A)")
    for ref_name in ("ngẫu nhiên", "thực tế"):
        print(f"\n== Quỹ đạo tham chiếu (hiệu chỉnh + decision-level): {ref_name}")
        print(f"{'luật':5s} {'J_dl TB':>9s} {'J_tr TB':>9s} {'delay TB':>9s}")
        for name in ("fix", "orc", "ext"):
            v = np.array([r[(ref_name, name)] for r in rows])
            print(f"{name:5s} {v[:, 0].mean():9.4%} {v[:, 1].mean():9.4%} {v[:, 2].mean():9.4f}")
        get = lambda n, i: np.array([r[(ref_name, n)][i] for r in rows])
        print(
            f"số seed (trên 10): J_dl ext<orc {np.sum(get('ext', 0) < get('orc', 0))}, "
            f"orc<fix {np.sum(get('orc', 0) < get('fix', 0))} | J_tr ext<orc {np.sum(get('ext', 1) < get('orc', 1))}, "
            f"orc<fix {np.sum(get('orc', 1) < get('fix', 1))} | delay ext<orc {np.sum(get('ext', 2) < get('orc', 2))}"
        )
