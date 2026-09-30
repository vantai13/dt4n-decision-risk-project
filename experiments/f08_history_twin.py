"""f08 (P1v2/L1.9) — F8: twin có lịch sử (Kalman từng path). Thực thi F8 §2B, khoá tại tag prereg-f7 (9a4ac69).

Câu hỏi (F8 §2B): khi MỌI luật và oracle dùng lịch sử số đo, κ̂ có tăng ở τ = 10 s như T5/t07 dự đoán, gần như không đổi
ở τ = 2 s (P2, đối chứng âm), và khoảng thông tin có thu hẹp không?

Chế độ, theo thứ tự khoá (outcome F7 đã commit → anchor → validity [commit] → outcome [commit]):
  anchor   — điều kiện F1 chạy qua ĐƯỜNG CODE CỦA f08 trên seed f04b, khoá 713 (τ = 10 s) và 711 (P2), oracle F20x2 như
             f05c; phải tái lập f05c đến chữ số in ra. Kiểm thêm: mô phỏng kéo dài (cửa sổ khởi động) cho ρ̂ và D trùng
             từng bit với f04b ở 1500 epoch thật.
  validity — (a) lý thuyết: AR(1)-Kalman so với hiệp phương sai chính xác của t06 (→ F8 §1); (b) chuỗi OU dài: R² thực
             nghiệm của bộ lọc khớp R² giải tích; (c) mỗi thế giới × điều kiện: CHỈ calibration + oracle — tham số tune,
             cổng harm, ô thưa; kiểm thao tác trên cal (ρ_s² tâm–D; quét độ nhớ). KHÔNG seed test, KHÔNG κ̂, KHÔNG gap.
  outcome  — 90 seed test: phân rã năm bậc, κ̂ (theo seed, gộp, sàn D6), M8 (i)(ii), phụ share_info, V, cổng, VoIP.
  smoke    — dữ liệu NGẪU NHIÊN tổng hợp (không DES, không thế giới F8) để chạy mọi nhánh của outcome; số liệu vô nghĩa.

Cài đặt các chỗ văn bản khoá để ngỏ (commit TRƯỚC mọi lần chạy chính thức; không đổi estimand hay tiêu chí):
  (1) Dùng lại NGUYÊN hàm đã khoá của f07 (build, evaluate_test, pooled_summary, kappa, ci_n, verdict) ở dạng KHÔNG chiều:
      S0 tune theo J (f02.tune_static, abs|rel), quỹ đạo tham chiếu = quỹ đạo S0, oracle bin 20 × 20 trên (rh_cur, rh_alt),
      λ và ngưỡng SC tune bằng harm dự đoán. CI95 t với bậc tự do n − 1 theo số seed thật.
  (2) Twin FH: rh ← m̂ (tải dự báo cho khoảng giữ, đơn vị ρ); Ĉ = T(m̂)·S; Î = Ĉ_A − Ĉ_B. Mọi luật và oracle đọc CÙNG các
      trường này ⇒ knowledge parity theo cấu trúc. F1: rh = ρ̂ plug-in (đúng f04b).
  (3) Kalman AR(1) đúng F8 §2B: trạng thái x = trung bình cửa sổ − μ, μ = ρ̄; φ = e^(−W/τ); Q = V(W)(1 − φ²), V(W) = phương
      sai trung bình cửa sổ của OU; R = ρ̄S/W; độ lợi DỪNG K từ nghiệm đóng của phương trình Riccati, dùng từ đầu.
      Dự báo m̂ = μ + e^(−g/τ)·x̂⁺, g = lag + a. Twin biết (ρ̄, σ, τ) của path (giả định như t06/t07).
  (4) Khởi động bộ lọc: x̂ = 0 tại t = 0; lọc qua N_PRE = 40 cửa sổ 0,5 s nằm trọn trong burn-in trước epoch quyết định đầu
      tiên. Các cửa sổ này đếm trên CÙNG chuỗi gói đến (không rút thêm số ngẫu nhiên) ⇒ F1 trùng f04b từng bit.
  (5) Cổng hợp lệ lúc outcome, như F7, cho từng thế giới × điều kiện: harm ≤ α trên cal theo tiêu chí tune; ô thưa < 1%;
      K2 − S0 ≥ −2SE. Cổng không đạt ⇒ estimand dựa trên oracle của ô đó không được diễn giải.
  (6) κ̂ theo seed: D4 (f07.kappa) trên epoch test của seed; gộp: D4 trên mọi epoch test; sàn D6 trên dữ liệu gộp.
  (7) M8 (i): Δ₁₀ theo seed = κ̂_FH − κ̂_F1 (cùng seed, cùng DES); cận dưới CI > 0. M8 (ii): Δ₁₀ − Δ_P2 theo chỉ số seed;
      cận dưới CI > 0. M8 ĐẠT ⇔ (i) và (ii).
  (8) Phụ: share_info theo seed = (headroom − K2(∞))/headroom; hiệu FH − F1 ở τ = 10 s theo seed; ĐẠT ⇔ cận trên CI < 0.
  (9) V (r = 10%): cận dưới CI của (K2 − S0) − 0,10·headroom > 0 ở FH, τ = 10 s; ba ô còn lại báo, không quyết định.
  (10) Epoch đầy buffer suốt khoảng giữ: giữ như f04b (K·S) để anchor tái lập; báo n_nan (F7: 0).
  (11) Báo kèm, KHÔNG đăng ký: J(S0_F1) − J(S0_FH) — lẫn giá trị lịch sử với giá trị sửa tâm (F1 là plug-in, FH co về μ).
  (12) Kiểm thao tác (báo, không cổng): Spearman² giữa tâm và D — bất biến đơn điệu như oracle bin, nên đo THÔNG TIN mà
       không lẫn sửa tâm; Pearson² trên Ĉ báo kèm để thấy phần lẫn. Quét độ nhớ a của bộ làm trơn mũ: a tối ưu cho D so với
       a Kalman tối ưu cho tải (dấu hiệu bộ nhớ hàng đợi mà mô hình t06/t07 bỏ qua).
Provenance: Claude (AI) viết theo F8 §2B; tác giả đọc từng hàm, chạy chính thức, commit theo thứ tự khoá.
Chạy: python experiments/f08_history_twin.py --mode {anchor|validity|outcome|smoke}
      | tee experiments/results/f08_<mode>_output.txt
"""
import argparse
import json
import sys
import time
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
import t06_history_information as t6

ALPHA, STREAM, N_PRE, TOY_SEED = f.ALPHA, 730, 40, 11941
SEEDS = dict(cal=tuple(range(11001, 11009)), test=tuple(range(11011, 11101)), orc=tuple(range(11101, 11698)))
WORLDS = {"T10": "K100_r0.95_s03t10", "P2": "P2"}          # thế giới F8 → ô f04b (tham số và khoá neo)
CONDS = ("F1", "FH")
ANCHOR = {"K100_r0.95_s03t10": dict(stream=713, lam=58.59, t0=18.86, pure=(0.000, 0.000), k=0.151),
          "P2": dict(stream=711, lam=151.24, t0=39.89, pure=(0.086, 0.114), k=0.165)}
F05C_JSON = HERE / "results" / "f05c" / "f05c_results.json"
OUT = HERE / "results" / "f08"


# ---------------------------------------------------------------- Kalman
def kalman_params(cell):
    """AR(1) cho trung bình cửa sổ + độ lợi dừng. Riccati dạng trước cập nhật: P = φ²·P·R/(P + R) + Q
    ⇔ P² + (R(1 − φ²) − Q)·P − Q·R = 0 ⇒ lấy nghiệm dương."""
    W, tau = cell.win, cell.tau
    phi = np.exp(-W / tau)
    V = f.v_avg(W, cell.sigma, tau)
    Q = V * (1.0 - phi**2)
    R = cell.rho_bar * cell.s_ms * 1e-3 / W
    bq = R * (1.0 - phi**2) - Q
    P = 0.5 * (-bq + np.sqrt(bq * bq + 4.0 * Q * R))
    K = P / (P + R)
    return dict(phi=phi, V=V, Q=Q, R=R, P_prior=P, P_post=(1.0 - K) * P, K=K, a=phi * (1.0 - K),
                c=np.exp(-(cell.lag + cell.act) / tau), mu=cell.rho_bar)


def kalman_center(y, kp):
    """x̂⁺_k = φx̂⁺_{k−1} + K(y_k − μ − φx̂⁺_{k−1}) = a·x̂⁺_{k−1} + K·(y_k − μ), x̂⁺_{−1} = 0. Trả m̂ = μ + c·x̂⁺."""
    x = lfilter([kp["K"]], [1.0, -kp["a"]], np.asarray(y, float) - kp["mu"])
    return kp["mu"] + kp["c"] * x


# ---------------------------------------------------------------- mô phỏng
def path_series(rng, cell, psa):
    """Một path: gọi NGUYÊN g.one_path trên lưới quyết định kéo dài thêm N_PRE epoch khởi động trong burn-in.
    Số ngẫu nhiên rút ra chỉ phụ thuộc thời điểm quyết định CUỐI ⇒ trùng từng bit f04b ở 1500 epoch thật."""
    t_dec = g.BURN_IN + cell.lag + cell.win + cell.hold * np.arange(-N_PRE, f.N_EPOCH)
    assert t_dec[0] - cell.lag - cell.win >= -1e-9, "cửa sổ khởi động đầu tiên phải nằm trong [0, burn-in]"
    rh, des, _, _, clip = g.one_path(rng, cell, psa, t_dec)
    full_ms = cell.k * (cell.s_ms * 1e-3) * 1e3                 # đúng biểu thức của one_path cho epoch đầy trọn
    return dict(rh_all=rh, rh=rh[N_PRE:], des=des[N_PRE:], n_nan=int(np.sum(des[N_PRE:] == full_ms)), clip=clip)


def episode(pa, pb, cell, psa, cond, kp):
    """Episode đúng định dạng f02/f07. F1: tâm = ρ̂ (f04b). FH: tâm = m̂ Kalman. D, I giống hệt giữa hai điều kiện."""
    if cond == "F1":
        ca, cb = pa["rh"], pb["rh"]
    else:
        ca, cb = kalman_center(pa["rh_all"], kp)[N_PRE:], kalman_center(pb["rh_all"], kp)[N_PRE:]
    da, db = psa.point(ca) * cell.s_ms, psa.point(cb) * cell.s_ms
    return dict(D_A=pa["des"], D_B=pb["des"], I_A=pa["des"] - pb["des"], Ihat_A=da - db, Chat_A=da, Chat_B=db,
                rh_A=ca, rh_B=cb, n_nan=pa["n_nan"] + pb["n_nan"], clip=max(pa["clip"], pb["clip"]))


def simulate(cell, seeds, stream, conds=CONDS):
    """CRN: một lần mô phỏng DES mỗi (seed, khe); F1 và FH dựng trên CÙNG hai path. Khe như f04b."""
    psa, kp = r7.psa_for(cell.k), kalman_params(cell)
    out = {c: [] for c in conds}
    for s in seeds:
        pa, pb = (path_series(np.random.default_rng(ch), cell, psa)
                  for ch in np.random.SeedSequence([s, stream]).spawn(2))
        for c in conds:
            out[c].append(episode(pa, pb, cell, psa, c, kp))
    return out


# ---------------------------------------------------------------- lý thuyết (validity a, b)
def ar1_vs_exact(cell, n_max=80):
    """R² của AR(1)-Kalman DƯỚI hiệp phương sai CHÍNH XÁC của OU (công thức đóng t06), so với dự báo tuyến tính tốt nhất."""
    assert (cell.win, cell.hold, cell.lag + cell.act) == (t6.W, t6.H, t6.LAG + t6.ACT)
    kp = kalman_params(cell)
    wins, hold = t6.intervals(n_max)
    cov = lambda i1, i2: t6.cov_closed(i1, i2, cell.sigma, cell.tau)
    Sy = np.array([[cov(a, b) for b in wins] for a in wins]) + kp["R"] * np.eye(n_max)
    c = np.array([cov(a, hold) for a in wins])
    vg = cov(hold, hold)
    w = kp["c"] * kp["K"] * kp["a"] ** np.arange(n_max)             # trọng số lên cửa sổ, mới nhất trước
    cmg, vm = float(w @ c), float(w @ Sy @ w)
    lag1_true = cov(wins[0], wins[1]) / cov(wins[0], wins[0])
    return dict(kp=kp, r2_corr=cmg**2 / (vm * vg), r2_mse=1.0 - (vg - 2.0 * cmg + vm) / vg, beta_opt=cmg / vm,
                exact={n: t6.r2(n, cell.rho_bar, cell.sigma, cell.tau, t6.cov_closed) for n in (1, 2, 5, 10, 20, 40, 80)},
                lag1_true=lag1_true, lag1_ar1=kp["phi"], memory=1.0 / (1.0 - kp["a"]))


def long_chain(cell, n_win=200_000, n_batch=20, seed=TOY_SEED):
    """Chuỗi OU + nhiễu đếm Poisson dài (KHÔNG DES): R² thực nghiệm của m̂ Kalman theo G (tải TB khoảng giữ)."""
    rng = np.random.default_rng([seed, int(round(cell.tau * 100)), int(round(cell.sigma * 1000))])
    kp = kalman_params(cell)
    sw, sg, sh = (int(round(v / f.DT)) for v in (cell.win, cell.lag + cell.act, cell.hold))
    n = n_win * sw + sg + sh + 1
    r = np.exp(-f.DT / cell.tau)
    x0 = cell.sigma * rng.standard_normal()
    e = cell.sigma * np.sqrt(1 - r * r) * rng.standard_normal(n - 1)
    rho = cell.rho_bar + np.concatenate([[x0], lfilter([1.0], [1.0, -r], e, zi=[r * x0])[0]])
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (rho[1:] + rho[:-1]) * f.DT)])      # tích phân hình thang
    ends = sw * np.arange(1, n_win + 1)
    m_win = (cum[ends] - cum[ends - sw]) / cell.win
    G = (cum[ends + sg + sh] - cum[ends + sg]) / cell.hold
    S = cell.s_ms * 1e-3
    y = rng.poisson(cell.win * np.maximum(m_win, 0.0) / S) * S / cell.win
    mh = kalman_center(y, kp)
    keep = slice(200, None)                                                          # bỏ quá độ đầu chuỗi
    gb, mb = np.array_split(G[keep], n_batch), np.array_split(mh[keep], n_batch)
    r2c = np.array([np.corrcoef(a, b)[0, 1] ** 2 for a, b in zip(gb, mb)])
    r2m = np.array([1 - np.mean((a - b) ** 2) / np.var(a) for a, b in zip(gb, mb)])
    one = np.array([np.corrcoef(a, b)[0, 1] ** 2 for a, b in zip(gb, np.array_split(y[keep], n_batch))])
    se = lambda x: float(x.std(ddof=1) / np.sqrt(len(x)))
    return dict(r2_corr=(float(r2c.mean()), se(r2c)), r2_mse=(float(r2m.mean()), se(r2m)),
                r2_one=(float(one.mean()), se(one)))


def info_check(eps):
    """Kiểm thao tác trên CAL (không phải estimand), gộp hai path, epoch, seed.
    ρ_s² = Spearman²(tâm, D): BẤT BIẾN với mọi phép biến đổi đơn điệu (T, co về μ) ⇒ chỉ đo THÔNG TIN — cùng bất biến
    với oracle bin phân vị. corr²(Ĉ, D) = Pearson² trên Ĉ = T(tâm)·S: lẫn thông tin với sửa tâm (plug-in méo qua T lồi)."""
    cen = np.concatenate([np.concatenate([ep["rh_A"], ep["rh_B"]]) for ep in eps])
    ch = np.concatenate([np.concatenate([ep["Chat_A"], ep["Chat_B"]]) for ep in eps])
    d = np.concatenate([np.concatenate([ep["D_A"], ep["D_B"]]) for ep in eps])
    return float(stats.spearmanr(cen, d)[0] ** 2), float(np.corrcoef(ch, d)[0, 1] ** 2)


MEM_GRID = (0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95)


def memory_scan(cell, seeds):
    """Kiểm thao tác mở rộng trên CAL (báo, không cổng): ρ_s²(bộ làm trơn mũ độ nhớ a, D). a = 0: một cửa sổ (F1);
    a = φ(1 − K): Kalman tối ưu cho TẢI. Nếu a tối ưu cho DELAY lệch khỏi a Kalman ⇒ D có bộ nhớ khác tải (hàng đợi)."""
    psa, kp = r7.psa_for(cell.k), kalman_params(cell)
    ys, ds = [], []
    for s in seeds:
        for ch in np.random.SeedSequence([s, STREAM]).spawn(2):
            p = path_series(np.random.default_rng(ch), cell, psa)
            ys.append(p["rh_all"] - cell.rho_bar)
            ds.append(p["des"])
    d = np.concatenate(ds)
    smooth = lambda a: np.concatenate([lfilter([1.0 - a], [1.0, -a], y)[N_PRE:] for y in ys])
    grid = sorted(set(MEM_GRID) | {round(float(kp["a"]), 4)})
    return {a: float(stats.spearmanr(smooth(a), d)[0] ** 2) for a in grid}, float(kp["a"])
# ---------------------------------------------------------------- các chế độ
def mode_anchor():
    out = {}
    for name, a in ANCHOR.items():
        cell, stream = g.CELLS[name]
        assert stream == a["stream"]
        eps_ms = f.EPS_OVER_S * cell.s_ms
        sim = lambda seeds, st: simulate(cell, seeds, st, conds=("F1",))["F1"]
        eps = dict(cal=sim(f.CAL_SEEDS, stream), test=sim(f.TEST_SEEDS, stream),
                   orc=sim(f.ORACLE_SEEDS, stream) + sim(f.ORACLE_SEEDS, stream + q.EXTRA))
        ref = g.simulate_pair(cell, r7.psa_for(cell.k), f.TEST_SEEDS[0], stream)[0]
        same = all(np.array_equal(ref[k], eps["test"][0][k]) for k in ("rh_A", "D_A", "rh_B", "D_B", "Ihat_A", "Chat_A"))
        b = r7.build(eps, eps_ms, directional=False)
        per, pool = r7.evaluate_test(eps["test"], b, eps_ms, directional=False)
        k_pool = r7.kappa(pool["ibar"], pool["log_s"])[0]
        pure = r7.ci_n(per["gain_K2"] - per["gain_SC"])
        printed = (round(b["lam"], 2) == a["lam"] and round(b["h_c"], 2) == a["t0"]
                   and (round(pure[0], 3), round(pure[1], 3)) == a["pure"] and round(k_pool, 3) == a["k"])
        rj = json.loads(F05C_JSON.read_text(encoding="utf-8"))[f"{name}/A0"]
        dev = max(abs(b["lam"] - rj["lam"]), abs(b["h_c"] - rj["t0"]), abs(pure[0] - rj["pure"][0]),
                  abs(pure[1] - rj["pure"][1]), abs(k_pool - rj["k_pure"]))
        print(f"ANCHOR — F1 qua đường code f08 | ô {name} | khoá {stream} (+{q.EXTRA}) | ρ̂, D, Î trùng f04b: {same}")
        print(f"  λ = {b['lam']:.2f} | t₀ = {b['h_c']:.2f} | K2 − SC = {pure[0]:+.3f} ± {pure[1]:.3f} | κ̂ gộp = {k_pool:.3f}"
              f" | khớp chữ số in ra: {printed} | lệch tối đa so với f05c JSON: {dev:.1e}")
        assert same and printed, "ANCHOR KHÔNG KHỚP — dừng, tìm lỗi trước mọi chế độ khác"
        out[name] = dict(world_same=same, lam=b["lam"], t0=b["h_c"], pure=pure, k_pure=k_pool, max_dev_json=dev)
    return out


def mode_validity():
    for k in ("cal", "test"):
        assert not set(SEEDS[k]) & set(SEEDS["orc"])
    assert not set(SEEDS["cal"]) & set(SEEDS["test"])
    print(f"VALIDITY — (a) lý thuyết, (b) chuỗi OU dài (seed toy {TOY_SEED}), (c) CHỈ cal {SEEDS['cal'][0]}–"
          f"{SEEDS['cal'][-1]} + oracle {SEEDS['orc'][0]}–{SEEDS['orc'][-1]}; KHÔNG seed test, KHÔNG κ̂/gap | khoá {STREAM}")
    out, ok_all = {}, True
    print("\n(a) AR(1)-Kalman dưới hiệp phương sai CHÍNH XÁC (→ F8 §1)")
    for w, name in WORLDS.items():
        cell = g.CELLS[name][0]
        th = ar1_vs_exact(cell)
        kp = th["kp"]
        ex = th["exact"]
        print(f"[{w}] φ {kp['phi']:.4f} (tương quan lag-1 thật {th['lag1_true']:.4f}) | R/V(W) {kp['R'] / kp['V']:.2f} | "
              f"K {kp['K']:.4f} | a = φ(1 − K) {kp['a']:.4f} | nhớ ~{th['memory']:.1f} cửa sổ | c = e^(−g/τ) {kp['c']:.4f}")
        print(f"     R² chính xác theo n: " + " ".join(f"{n}:{v:.3f}" for n, v in ex.items())
              + f" | AR(1)-Kalman: corr² {th['r2_corr']:.3f}, MSE {th['r2_mse']:.3f} | hệ số tối ưu/hệ số dùng "
              f"{th['beta_opt']:.3f} | mất so với tốt nhất {ex[80] - th['r2_corr']:.4f}")
        lc = long_chain(cell)
        ok_chain = abs(lc["r2_corr"][0] - th["r2_corr"]) <= 3 * lc["r2_corr"][1] + 0.005
        ok_all &= ok_chain
        print(f"(b) [{w}] chuỗi dài: R² corr {lc['r2_corr'][0]:.3f} ± {lc['r2_corr'][1]:.3f} (giải tích "
              f"{th['r2_corr']:.3f}) | R² MSE {lc['r2_mse'][0]:.3f} ± {lc['r2_mse'][1]:.3f} (giải tích {th['r2_mse']:.3f}) | "
              f"một cửa sổ {lc['r2_one'][0]:.3f} (t06 {ex[1]:.3f}) | {'KHỚP' if ok_chain else 'KHÔNG KHỚP'}")
        out[w] = dict(theory=th, chain=lc, chain_ok=ok_chain)
    print("\n(c) Mỗi thế giới × điều kiện: tune và cổng trên calibration + oracle")
    for w, name in WORLDS.items():
        cell = g.CELLS[name][0]
        eps_ms = f.EPS_OVER_S * cell.s_ms
        cal, orc = simulate(cell, SEEDS["cal"], STREAM), simulate(cell, SEEDS["orc"], STREAM)
        for c in CONDS:
            b = r7.build(dict(cal=cal[c], orc=orc[c]), eps_ms, directional=False)
            sp = b["oracle"].frac_sparse
            gates_ok = all(v <= ALPHA + 1e-9 for v in b["gates"].values()) and sp < 0.01
            ok_all &= gates_ok
            r0 = b["rule0"]
            ic = info_check(cal[c])
            print(f"[{w}/{c}] S0: {r0[1]} ngưỡng {r0[2]:.4g} (J cal {r0[3]:.3f}) | λ {b['lam']:.2f} | H_c {b['h_c']:.2f} | "
                  f"ô thưa {100 * sp:.2f}% | kiểm thao tác (cal, báo): ρ_s²(tâm, D) {ic[0]:.3f} · corr²(Ĉ, D) {ic[1]:.3f}")
            print("     cổng harm (≤ 1%): " + " | ".join(f"{k} {100 * v:.3f}%" for k, v in b["gates"].items())
                  + " || báo: " + " | ".join(f"{k} {100 * v:.3f}%" for k, v in b["reported"].items())
                  + f" || CỔNG {'ĐẠT' if gates_ok else 'KHÔNG ĐẠT'}")
            out[f"{w}/{c}"] = dict(gates=b["gates"], reported=b["reported"], sparse=sp, lam=b["lam"], h_c=b["h_c"],
                                   rule0=list(r0), info_check=ic, ok=gates_ok)
        scan, a_k = memory_scan(cell, SEEDS["cal"])
        best = max(scan, key=scan.get)
        print(f"[{w}] quét độ nhớ (cal, báo): " + " ".join(f"a={a:.2f}:{v:.3f}" for a, v in scan.items())
              + f" | a Kalman (tối ưu cho tải) {a_k:.3f} | a tốt nhất cho D {best:.2f}")
        out[f"{w}/memory_scan"] = dict(scan=scan, a_kalman=a_k, a_best_delay=best)
    print(f"\nVALIDITY TỔNG: {'ĐẠT' if ok_all else 'KHÔNG ĐẠT — dừng, không chạy outcome'}")
    out["ok"] = bool(ok_all)
    return out


def run_outcome(data, eps_ms):
    """data[w][c] = dict(cal, test, orc). Chung cho outcome và smoke."""
    res = {}
    for w in data:
        for c in CONDS:
            b = r7.build(data[w][c], eps_ms[w], directional=False)
            per, pool = r7.evaluate_test(data[w][c]["test"], b, eps_ms[w], directional=False)
            res[(w, c)] = dict(b=b, per=per, summ=r7.pooled_summary(pool, b, False))
    P = {k: v["per"] for k, v in res.items()}
    S = {k: v["summ"] for k, v in res.items()}
    n = len(P[("T10", "F1")]["headroom"])
    txt = r7.txt

    print(f"\nBẢNG 1 — phân rã năm bậc trên quỹ đạo S0 của chính điều kiện (ms/epoch; CI95 t theo {n} seed)")
    for (w, c), p in P.items():
        h = p["headroom"].mean()
        terms = dict(S0=p["gain_ref"], tâm=p["gain_SC"] - p["gain_ref"], thuần=p["gain_K2"] - p["gain_SC"],
                     an_toàn=p["gain_K2inf"] - p["gain_K2"], thông_tin=p["headroom"] - p["gain_K2inf"])
        print(f"[{w}/{c}] headroom {txt(p['headroom'])} | " + " | ".join(
            f"{k} {txt(v)} ({100 * v.mean() / h:.1f}%)" for k, v in terms.items()))
        print(f"      harm test S0 {100 * p['harm_ref'].mean():.2f}% · K2 {100 * p['harm_K2'].mean():.2f}% | "
              f"n_nan TB {p['n_nan'].mean():.1f} | VoIP (m, r) trên K2 − S0: "
              f"{r7.verdict(p['gain_K2'] - p['gain_ref'], p['headroom'])}")

    print("\nBẢNG 2 — κ̂ (D4): theo seed (CI) và gộp; sàn D6")
    for (w, c), p in P.items():
        s = S[(w, c)]
        print(f"[{w}/{c}] κ̂ theo seed {txt(p['k_chung'])} | gộp {s['k_chung']:.3f} | sàn bin {s['floor_bin']:.3f}, "
              f"mẫu {s['floor_smp']:.3f}, tổng {s['floor']:.3f} | thuần dự đoán D7 {s['pred_pure']:.3f} ms")

    gates = {}
    for (w, c), r in res.items():
        p, b = r["per"], r["b"]
        diff = p["gain_K2"] - p["gain_ref"]
        gates[f"{w}/{c}"] = {"harm cal": all(v <= ALPHA + 1e-9 for v in b["gates"].values()),
                             "ô thưa < 1%": b["oracle"].frac_sparse < 0.01,
                             "K2 − S0 ≥ −2SE": bool(diff.mean() >= -2 * diff.std(ddof=1) / np.sqrt(len(diff)))}
    valid = all(all(v.values()) for v in gates.values())
    print("\nCỔNG HỢP LỆ: " + " | ".join(f"{k}: " + ", ".join(f"{kk} {'✓' if vv else '✗'}" for kk, vv in v.items())
                                     for k, v in gates.items()))

    kap = lambda w, c: P[(w, c)]["k_chung"]
    d10, dp2 = kap("T10", "FH") - kap("T10", "F1"), kap("P2", "FH") - kap("P2", "F1")
    share = lambda w, c: (P[(w, c)]["headroom"] - P[(w, c)]["gain_K2inf"]) / P[(w, c)]["headroom"]
    pT = P[("T10", "FH")]
    m8i, m8ii, dp2c = r7.ci_n(d10), r7.ci_n(d10 - dp2), r7.ci_n(dp2)
    sub = r7.ci_n(share("T10", "FH") - share("T10", "F1"))
    v = r7.ci_n(pT["gain_K2"] - pT["gain_ref"] - f.R_SESOI * pT["headroom"])
    tests = {"M8(i)": m8i[0] - m8i[1] > 0, "M8(ii)": m8ii[0] - m8ii[1] > 0, "phụ share_info": sub[0] + sub[1] < 0,
             "V": v[0] - v[1] > 0}
    tests["M8"] = tests["M8(i)"] and tests["M8(ii)"]
    ok = lambda b_: "ĐẠT" if b_ else "KHÔNG ĐẠT"
    print("\nPHÉP KIỂM (F8 §2B)")
    print(f"  M8 (i)  Δ₁₀ = κ̂_FH − κ̂_F1 (τ = 10 s)          = {m8i[0]:+.3f} ± {m8i[1]:.3f} → {ok(tests['M8(i)'])}")
    print(f"          Δ_P2 (đối chứng, báo)                     = {dp2c[0]:+.3f} ± {dp2c[1]:.3f}")
    print(f"  M8 (ii) Δ₁₀ − Δ_P2 (ghép theo chỉ số seed)       = {m8ii[0]:+.3f} ± {m8ii[1]:.3f} → {ok(tests['M8(ii)'])}")
    print(f"  M8 = (i) ∧ (ii) → {ok(tests['M8'])}")
    print(f"  Phụ   share_info(FH) − share_info(F1), τ = 10 s = {100 * sub[0]:+.2f} ± {100 * sub[1]:.2f} điểm % "
          f"→ {ok(tests['phụ share_info'])}")
    print(f"  V     (K2 − S0) − 0,10·headroom, FH τ = 10 s     = {v[0]:+.3f} ± {v[1]:.3f} ms → {ok(tests['V'])}")
    extra = {w: r7.ci_n(P[(w, "F1")]["J_S0"] - P[(w, "FH")]["J_S0"]) for w in data}
    print("  Báo kèm, KHÔNG đăng ký (lẫn lịch sử + sửa tâm): J(S0_F1) − J(S0_FH) = "
          + " | ".join(f"{w} {m:+.3f} ± {h:.3f} ms" for w, (m, h) in extra.items()))
    print(f"\nCỔNG: {'ĐẠT' if valid else 'KHÔNG ĐẠT — không diễn giải estimand oracle của ô không đạt'} | "
          f"M8 {ok(tests['M8'])} | V {ok(tests['V'])}")

    print("\n--- Khối Markdown cho F8 §3 (dán nguyên văn; số lấy từ output này) ---")
    print("| | Kết quả | Kết luận |\n|---|---|---|")
    print(f"| M8 (i) Δ₁₀ | {m8i[0]:+.3f} ± {m8i[1]:.3f} | {ok(tests['M8(i)'])} |")
    print(f"| Δ_P2 (báo) | {dp2c[0]:+.3f} ± {dp2c[1]:.3f} | — |")
    print(f"| M8 (ii) Δ₁₀ − Δ_P2 | {m8ii[0]:+.3f} ± {m8ii[1]:.3f} | {ok(tests['M8(ii)'])} |")
    print(f"| Phụ share_info FH − F1 (τ = 10 s) | {100 * sub[0]:+.2f} ± {100 * sub[1]:.2f} điểm % | "
          f"{ok(tests['phụ share_info'])} |")
    print(f"| V (FH, τ = 10 s) | {v[0]:+.3f} ± {v[1]:.3f} ms | {ok(tests['V'])} |")

    store = {f"{w}/{c}": dict(per={k: v_.tolist() for k, v_ in r["per"].items()}, summary=r["summ"], lam=r["b"]["lam"],
                              h_c=r["b"]["h_c"], rule0=list(r["b"]["rule0"]), gates_cal=r["b"]["gates"],
                              sparse=r["b"]["oracle"].frac_sparse) for (w, c), r in res.items()}
    store.update(tests=dict(M8i=m8i, M8ii=m8ii, D_P2=dp2c, share_info=sub, V=v, passed=tests),
                 extra_J=extra, gates=gates, valid=valid)
    return store


def mode_outcome():
    print(f"OUTCOME — {len(SEEDS['test'])} seed test {SEEDS['test'][0]}–{SEEDS['test'][-1]} | khoá {STREAM}")
    data, eps_ms = {}, {}
    for w, name in WORLDS.items():
        cell = g.CELLS[name][0]
        eps_ms[w] = f.EPS_OVER_S * cell.s_ms
        sims = {k: simulate(cell, SEEDS[k], STREAM) for k in ("cal", "test", "orc")}
        data[w] = {c: {k: sims[k][c] for k in sims} for c in CONDS}
    return run_outcome(data, eps_ms)


def synthetic_ep(rng, noise):
    """Episode ngẫu nhiên đúng định dạng — KHÔNG phải thế giới F8; chỉ để chạy thử code."""
    ra, rb = rng.uniform(0.8, 1.05, f.N_EPOCH), rng.uniform(0.8, 1.05, f.N_EPOCH)
    da, db = rng.gamma(2.0, 10.0, f.N_EPOCH), rng.gamma(2.0, 10.0, f.N_EPOCH)
    ca, cb = da * rng.uniform(1 - noise, 1 + noise, f.N_EPOCH), db * rng.uniform(1 - noise, 1 + noise, f.N_EPOCH)
    return dict(D_A=da, D_B=db, I_A=da - db, Ihat_A=ca - cb, Chat_A=ca, Chat_B=cb, rh_A=ra, rh_B=rb, n_nan=0, clip=0.0)


def mode_smoke():
    print("SMOKE — dữ liệu NGẪU NHIÊN tổng hợp, không DES, không thế giới F8; mọi con số VÔ NGHĨA")
    rng = np.random.default_rng(12345)
    noise = {"F1": 0.4, "FH": 0.2}
    data = {w: {c: {k: [synthetic_ep(rng, noise[c]) for _ in range(nn)] for k, nn in (("cal", 2), ("test", 5),
                                                                                     ("orc", 8))} for c in CONDS}
            for w in WORLDS}
    return run_outcome(data, {w: f.EPS_OVER_S * 3.024 for w in WORLDS})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("anchor", "validity", "outcome", "smoke"), required=True)
    mode, t0 = ap.parse_args().mode, time.time()
    print(f"f08 | engine {g.ENGINE} | mode {mode} | tiền đăng ký: tag prereg-f7 (F8 §2B)")
    result = dict(anchor=mode_anchor, validity=mode_validity, outcome=mode_outcome, smoke=mode_smoke)[mode]()
    if mode != "smoke":
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"f08_{mode}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False, default=float),
                                             encoding="utf-8")
    print(f"Thời gian {time.time() - t0:.0f} s", file=sys.stderr)
