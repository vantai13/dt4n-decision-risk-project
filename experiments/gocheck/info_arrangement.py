"""GO-check · Bước 2: CÙNG một thế giới vật lý, BA cách bố trí telemetry.

Câu hỏi DUY NHẤT: lợi thế rollout của K2 so với SC (Bước 1) có phụ thuộc vào việc path nào được đo tươi không?

  FIX : A luôn đo 1 s, B luôn đo 60 s               (= R1 của GO v0 — dùng làm NEO để kiểm)
  SYM : cả hai path đều đo 1 s                       (đối xứng: "mọi tunnel cùng nhịp")
  FF  : path ĐANG MANG luồng đo 1 s, path kia 60 s   ("độ tươi đi theo luồng", kiểu đo thụ động)

Thiết kế ghép cặp: cùng tải OU, cùng gói đến, cùng delay thật D_A, D_B. CHỈ thông tin của twin khác nhau.
Luồng RNG chính giống hệt go_test.simulate (neo bit-exact); telemetry bổ sung dùng một luồng RNG RIÊNG,
nên thêm telemetry không làm xê dịch thế giới.
Giản lược (ghi vào limitation): trong FF, path vừa được đổi sang có ngay số đo 1 s (không có thời gian "ấm máy").

Chạy từ gốc repo:
    python -m experiments.gocheck.info_arrangement --mode validity                  # chỉ kiểm, KHÔNG in kết quả SYM/FF
    python -m experiments.gocheck.info_arrangement --mode outcome --cal 94001 --test 95001
"""
import argparse
import copy
import pickle
import time

import numpy as np

from experiments.f04b_des_gap import workload_after
from experiments.gocheck.rollout import EPS, GRID, RAW, paired_ci, score
from experiments.gocheck.rollout import rollout as rollout_single
from experiments.gocheck.rollout import require_committed_spec
from experiments.scan import go_test as g
from experiments.scan.des_world import N_PROBE, latest_available
from experiments.scan.world import PKT_BITS, simulate_ou

FAST, SLOW = 1.0, 60.0
ARRANGEMENTS = ("FIX", "SYM", "FF")
ALPHAS, COOLDOWNS = (0.002, 0.01), (0, 30)
EXTRA_STREAM = 424242                       # khoá của luồng RNG riêng cho telemetry bổ sung


# ------------------------------------------------ thế giới ------------------------------------------------------
def des_path_keep_arrivals(rng, cell, p, t_dec, t_end, dt):
    """Chép NGUYÊN des_world.des_path (cùng các lần gọi rng, cùng thứ tự), chỉ thêm: trả về cả 'arrivals'."""
    s = PKT_BITS / (cell["mbps"] * 1e6)
    n_grid = int(np.ceil(t_end / dt)) + 1
    rho = simulate_ou(rng, n_grid, dt, p["rho_bar"], p["sigma"], p["tau"])
    t_grid = np.arange(n_grid + 1) * dt
    cum_lam = np.concatenate([[0.0], np.cumsum(np.clip(rho, 0.0, None) / s * dt)])
    u = np.cumsum(rng.exponential(1.0, int(cum_lam[-1] * 1.05) + 1000))
    arrivals = np.interp(u[u < cum_lam[-1]], cum_lam, t_grid)
    full = (cell["k"] - 1) * s
    v_after = workload_after(arrivals, s, full)
    T = p["T_tel"]
    r = np.arange(rng.uniform(0, T) + T, t_end, T)
    count = np.searchsorted(arrivals, r) - np.searchsorted(arrivals, r - T)
    stall = np.where(rng.random(len(r)) < p["stall_p"], rng.exponential(p["stall_mean"], len(r)), 0.0)
    rhohat, age = latest_available(r, count * s / T, r + p["d"] + stall, t_dec)
    probes = (t_dec + cell["a"])[:, None] + np.linspace(0.0, cell["H"], N_PROBE)[None, :]
    j = np.maximum(np.searchsorted(arrivals, probes, side="right") - 1, 0)
    v = np.maximum(v_after[j] - (probes - arrivals[j]), 0.0)
    v = np.where(probes >= arrivals[0], v, 0.0)
    ok = v <= full
    n_ok = ok.sum(1)
    D = np.where(n_ok > 0, np.where(ok, v + s, 0.0).sum(1) / np.maximum(n_ok, 1), cell["k"] * s) * 1e3
    return dict(rhohat=rhohat, age=age, D=D), arrivals


def extra_telemetry(rng_x, arrivals, s, T, d, t_dec, t_end):
    """Telemetry ở nhịp T khác, đếm trên CÙNG các gói đến (cùng thế giới), pha lấy từ luồng RNG riêng."""
    r = np.arange(rng_x.uniform(0, T) + T, t_end, T)
    count = np.searchsorted(arrivals, r) - np.searchsorted(arrivals, r - T)
    rhohat, age = latest_available(r, count * s / T, r + d, t_dec)
    return dict(rhohat=rhohat, age=age)


def simulate_info(seed, sc):
    """Như go_test.simulate (giữ nguyên n, dt, warm, t_dec), cộng thêm telemetry ở nhịp còn lại cho mỗi path."""
    rng = np.random.default_rng(seed)
    rng_x = np.random.default_rng([seed, EXTRA_STREAM])
    H, a = sc["H"], sc["a"]
    paths = (sc["A"], sc["B"])
    n = max(4000, int(100 * max(p["tau"] for p in paths) / H))
    dt = min(min(min(p["T_tel"] for p in paths), H) / 10, min(p["tau"] for p in paths) / 20)
    warm = 3 * max(p["T_tel"] for p in paths) + max(p["d"] for p in paths)
    t_dec = warm + H * np.arange(n)
    t_end = t_dec[-1] + a + 2 * H
    out = {}
    for name, p in zip("AB", paths):
        pc = dict(mbps=p["mbps"], k=p["k"], a=a, H=H)
        pp = dict(rho_bar=p["rho"], sigma=p["sigma"], tau=p["tau"], T_tel=p["T_tel"], d=p["d"], stall_p=0.0, stall_mean=0.0)
        main, arrivals = des_path_keep_arrivals(rng, pc, pp, t_dec, t_end, dt)
        T_other = SLOW if p["T_tel"] == FAST else FAST
        s = PKT_BITS / (p["mbps"] * 1e6)
        out[name] = main                                                       # nhịp gốc của R1
        out[name + "_x"] = extra_telemetry(rng_x, arrivals, s, T_other, p["d"], t_dec, t_end)   # nhịp còn lại
    return out


def load_info_worlds(sc, seeds, tag):
    RAW.mkdir(parents=True, exist_ok=True)
    f = RAW / f"{sc['name']}_info_{tag}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    worlds = [simulate_info(s, sc) for s in seeds]
    f.write_bytes(pickle.dumps(worlds))
    return worlds


# ------------------------------------------------ thông tin của twin ---------------------------------------------
def twin_outputs(w, sc, speed_A, speed_B):
    """Twin khi path A được đo ở nhịp speed_A, path B ở nhịp speed_B (FAST hoặc SLOW). Delay thật D không đổi."""
    s = copy.deepcopy(sc)
    world = {}
    for name, speed in (("A", speed_A), ("B", speed_B)):
        src = w[name] if sc[name]["T_tel"] == speed else w[name + "_x"]
        s[name]["T_tel"] = speed                                   # twin dùng đúng độ dài cửa sổ và nhiễu đếm của nhịp đó
        world[name] = dict(rhohat=src["rhohat"], age=src["age"], D=w[name]["D"])
    return g.decisions(world, s, {}, EPS)


def arrangement_inputs(w, sc):
    """Mỗi cách bố trí = (thông tin twin dùng khi luồng ĐANG Ở A, thông tin twin dùng khi luồng ĐANG Ở B)."""
    fix = twin_outputs(w, sc, FAST, SLOW)
    sym = twin_outputs(w, sc, FAST, FAST)
    on_B = twin_outputs(w, sc, SLOW, FAST)                         # FF khi đang ở B: B tươi, A cũ
    return {"FIX": (fix, fix), "SYM": (sym, sym), "FF": (fix, on_B)}


# ------------------------------------------------ rollout -------------------------------------------------------
def rollout_info(d_onA, d_onB, w, rule, thr, cooldown):
    """Như rollout.py, nhưng thông tin twin phụ thuộc path đang đi. Trả về (delay TB, tỉ lệ hại, số lần đổi/1000)."""
    ibA, pdnA = d_onA["Ibar_A"], d_onA["pdn_A"]
    ibB, pupB = d_onB["Ibar_A"], d_onB["pup_A"]
    D_A, D_B = w["A"]["D"], w["B"]["D"]
    n = len(ibA)
    on_A, last_switch = True, -10**9
    total_delay, n_harm, n_switch = 0.0, 0, 0
    for k in range(n):
        if k - last_switch >= cooldown:
            ibar, p = (ibA[k], pdnA[k]) if on_A else (-ibB[k], pupB[k])
            if score(rule, ibar, p) > thr:
                d_cur, d_new = (D_A[k], D_B[k]) if on_A else (D_B[k], D_A[k])
                n_harm += (d_cur - d_new) < -EPS
                n_switch += 1
                on_A, last_switch = not on_A, k
        total_delay += D_A[k] if on_A else D_B[k]
    return total_delay / n, n_harm / n, 1000 * n_switch / n


def tune_info(arr, rule, cal_in, cal_w, alpha, cooldown):
    """Ngưỡng tốt nhất trên CALIBRATION cho đúng cách bố trí này. Báo nếu ngưỡng chạm biên lưới."""
    best_delay, best_thr = np.inf, np.inf
    for thr in GRID[rule]:
        r = np.array([rollout_info(*ci[arr], w, rule, thr, cooldown) for ci, w in zip(cal_in, cal_w)])
        if r[:, 1].mean() <= alpha and r[:, 0].mean() < best_delay:
            best_delay, best_thr = r[:, 0].mean(), thr
    finite = GRID[rule][np.isfinite(GRID[rule])]
    edge = "ngưỡng = +inf (không bao giờ đổi)" if np.isinf(best_thr) else ("CHẠM BIÊN TRÊN của lưới — mở rộng lưới!"
                                                                         if best_thr == finite.max() else "")
    return best_thr, edge


# ------------------------------------------------ hai chế độ chạy ------------------------------------------------
def validity(R1):
    print("=== VALIDITY (seed go0) — không in kết quả SC vs K2 của SYM/FF ===")
    ok_all = True
    for seed in (80001, 81001):                                               # V1: thế giới trùng từng bit
        a, b = g.simulate(seed, R1), simulate_info(seed, R1)
        same = all(np.array_equal(a[p][k], b[p][k]) for p in "AB" for k in ("rhohat", "age", "D"))
        ok_all &= same
        print(f"V1 seed {seed}: luồng chính trùng go_test.simulate từng bit: {same}")
    cal_w = load_info_worlds(R1, range(80001, 80021), "go0_cal")
    test_w = load_info_worlds(R1, range(81001, 81021), "go0_test")
    cal_in = [arrangement_inputs(w, R1) for w in cal_w]
    test_in = [arrangement_inputs(w, R1) for w in test_w]
    d0, w0 = test_in[0]["FIX"][0], test_w[0]                                  # V2: hàm rollout mới = hàm cũ khi FIX
    same = all(rollout_info(d0, d0, w0, r, t, c) == rollout_single(d0, w0, r, t, c)
               for r, t, c in (("SC", 5.0, 0), ("SC", 20.0, 30), ("K2", 100.0, 0), ("K2", 1e4, 30)))
    ok_all &= same
    print(f"V2 rollout_info(FIX) == rollout.py trên 4 cặp (luật, ngưỡng, cooldown): {same}")
    res = {}
    for rule in ("SC", "K2"):
        thr, _ = tune_info("FIX", rule, cal_in, cal_w, 0.002, 0)
        res[rule] = np.array([rollout_info(*ci["FIX"], w, rule, thr, 0) for ci, w in zip(test_in, test_w)])
    m, lo, hi = paired_ci(res["SC"][:, 0] - res["K2"][:, 0])
    ok_all &= bool(np.allclose([m, lo, hi], [1.652, 1.225, 2.080], atol=0.0006, rtol=0))
    print(f"V3 neo FIX, α=0.002, cooldown 0: SC−K2 = {m:+.3f} [{lo:+.3f}, {hi:+.3f}] ms  (Bước 1: +1.652 [+1.225, +2.080])")
    for path, cad in (("A", "nhịp 60 s (bổ sung)"), ("B", "nhịp 1 s (bổ sung)")):     # V4: luồng bổ sung có lý không
        x = np.concatenate([w[path + "_x"]["age"] for w in cal_w])
        T = SLOW if path == "A" else FAST
        rh = np.concatenate([w[path + "_x"]["rhohat"] for w in cal_w])
        # Across seeds the phase is random; permit five standard errors.
        age_expected = R1[path]["d"] + T / 2
        age_tolerance = 5 * T / np.sqrt(12 * len(cal_w))
        ok_all &= bool(abs(x.mean() - age_expected) < age_tolerance
                       and abs(rh.mean() - R1[path]["rho"]) < 0.05)
        print(f"V4 {path} {cad}: tuổi TB {x.mean():6.2f} s (lý thuyết ≈ d + T/2 = {0.1 + T / 2:.2f} s) · ρ̂ TB {rh.mean():.3f} (ρ̄ = 0.8)")
    finite = all(np.isfinite(ci[a][i][k]).all() for ci in test_in for a in ARRANGEMENTS for i in (0, 1)
                 for k in ("Ibar_A", "pdn_A", "pup_A"))
    probe = [rollout_info(*test_in[0][a], test_w[0], r, t, 0) for a in ("SYM", "FF") for r, t in (("SC", 5.0), ("K2", 100.0))]
    runs = finite and all(np.isfinite(v).all() for v in probe)
    ok_all &= runs
    print(f"V5 đường ống SYM/FF chạy được, mọi đầu ra twin hữu hạn: {runs}   (KHÔNG in số liệu)")
    print("=> VALIDITY:", "ĐẠT" if ok_all else "TRƯỢT — dừng lại, tìm lỗi trước khi chạy outcome")
    if not ok_all:
        raise ValueError("Validity failed; outcome must not run.")


def outcome(R1, cal0, test0, n):
    cal_seeds, test_seeds = range(cal0, cal0 + n), range(test0, test0 + n)
    t0 = time.time()
    cal_w = load_info_worlds(R1, cal_seeds, f"{cal0}")
    test_w = load_info_worlds(R1, test_seeds, f"{test0}")
    cal_in = [arrangement_inputs(w, R1) for w in cal_w]
    test_in = [arrangement_inputs(w, R1) for w in test_w]
    print(f"=== OUTCOME · cal {cal0}–{cal0 + n - 1} · test {test0}–{test0 + n - 1} · {time.time() - t0:.0f} s ===")
    for cooldown in COOLDOWNS:
        for alpha in ALPHAS:
            diff = {}
            print(f"\n--- cooldown {cooldown:>2} s · α = {alpha} ---")
            for arr in ARRANGEMENTS:
                res = {}
                for rule in ("SC", "K2"):
                    thr, edge = tune_info(arr, rule, cal_in, cal_w, alpha, cooldown)
                    res[rule] = np.array([rollout_info(*ci[arr], w, rule, thr, cooldown) for ci, w in zip(test_in, test_w)])
                    if edge:
                        print(f"  [cảnh báo] {arr} {rule}: {edge}")
                diff[arr] = res["SC"][:, 0] - res["K2"][:, 0]
                m, lo, hi = paired_ci(diff[arr])
                print(f"  {arr:3s} | SC {res['SC'][:, 0].mean():6.3f} ms (harm {res['SC'][:, 1].mean() / alpha:4.2f}α, "
                      f"{res['SC'][:, 2].mean():4.1f} đổi/1000) | K2 {res['K2'][:, 0].mean():6.3f} ms "
                      f"(harm {res['K2'][:, 1].mean() / alpha:4.2f}α, {res['K2'][:, 2].mean():4.1f} đổi/1000) "
                      f"| SC−K2 {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            for other in ("SYM", "FF"):                                        # hiệu của hiệu: ghép cặp theo seed
                m, lo, hi = paired_ci(diff["FIX"] - diff[other])
                print(f"  (SC−K2)_FIX − (SC−K2)_{other} = {m:+.3f} [{lo:+.3f}, {hi:+.3f}] ms")
    print(f"\n({time.time() - t0:.0f} s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("validity", "outcome"), required=True)
    ap.add_argument("--cal", type=int, default=94001)
    ap.add_argument("--test", type=int, default=95001)
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()
    R1 = g.scenarios()[0][0]
    if args.mode == "validity":
        validity(R1)
    else:
        require_committed_spec("notes/gocheck/info_arrangement_spec.md")
        if (args.cal, args.test, args.n) != (94001, 95001, 20):
            raise ValueError("Outcome chỉ dùng dải đã dành 94001/95001, n=20.")
        outcome(R1, args.cal, args.test, args.n)


if __name__ == "__main__":
    main()
