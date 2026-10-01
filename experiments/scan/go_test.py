"""Bài kiểm GO/NO-GO thực tế.  Chạy từ gốc repo:   python -m experiments.scan.go_test
Phần 1  Kịch bản thực tế (R1, R2): mỗi tham số gắn nhãn [nguồn] hoặc [giả định] trong SCENARIOS.
Phần 2  Độ bền: twin đoán SAI σ, τ, ρ̄ của mạng (twin thật phải tự ước lượng các tham số này).
Phần 3  Quét biên quanh R1: hiệu ứng xuất hiện / biến mất ở đâu.
Mọi thứ trên DES, seed mới, so ngoài mẫu + so ở cùng harm (frontier). Tiêu chí GO khóa ở GO_RULE."""
import copy
import csv
import json
import time
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.stats import norm

from experiments.scan.cell import _pool
from experiments.scan.des_world import des_path
from experiments.scan.rules import orient, s0_trajectory, tune_threshold
from experiments.scan.strict_frontier import matched, optimum, ranking_scores
from experiments.scan.twin import GH_W, GH_X, DelayCurve, posterior
from experiments.scan.world import PKT_BITS

CAL, TEST = range(80001, 80021), range(81001, 81021)          # dải seed MỚI, chưa từng dùng
N_BOOT = 100
OUT = Path("results/go_test/go_v0.csv")


def path(mbps, buffer_ms, rho, r_f, tau, T_tel, d=0.1):
    s_ms = PKT_BITS / (mbps * 1e6) * 1e3
    return dict(mbps=mbps, k=max(2, round(buffer_ms / s_ms)), rho=rho, sigma=float(np.sqrt(rho * r_f / (mbps * 1e6))),
                tau=tau, T_tel=T_tel, d=d, n_flows=rho * mbps * 1e6 / r_f)


# ----------------------------------------------------------------------------------------------------------------
# KỊCH BẢN THỰC TẾ (đổi ở đây nếu bạn tìm được nguồn tốt hơn — NHƯNG trước khi chạy)
#  [nguồn] telemetry: streaming 1 s là mức mịn có nền tảng hỗ trợ; SNMP thường 30 s–5 phút (tài liệu nhà cung cấp)
#  [nguồn] path di động được probe thưa hơn để tiết kiệm dữ liệu (Cisco: hello BFD theo từng loại đường; Prisma: giảm probe)
#  [nguồn] mạng di động giữ buffer lớn, độ trễ khứ hồi tới vài giây (Jiang và cs., IMC 2012)
#  [giả định] tốc độ link, tải giờ cao điểm 0,7–0,8, cỡ flow nền, τ, nhịp quyết định H = 1 s, a = 50 ms
# ----------------------------------------------------------------------------------------------------------------
def scenarios():
    R1 = dict(name="R1_dualISP", H=1.0, a=0.05, eps_ms=1.0, tau_note="giả định",
              A=path(20, 150, 0.8, 500e3, 60, 1.0),             # ISP 1: streaming telemetry 1 s
              B=path(20, 150, 0.8, 500e3, 60, 60.0))            # ISP 2: chỉ có số đo thưa 60 s
    R2 = dict(name="R2_bb_LTE", H=1.0, a=0.05, eps_ms=1.0, tau_note="giả định",
              A=path(20, 100, 0.8, 500e3, 60, 1.0),             # broadband: buffer 100 ms, telemetry 1 s
              B=path(10, 500, 0.7, 250e3, 60, 60.0))            # LTE: chậm hơn, buffer sâu 500 ms, probe thưa 60 s
    base = [R1, R2]
    sweep = []                                                  # quét biên quanh R1, mỗi lần đổi MỘT thứ
    for T in (1.0, 10.0, 30.0, 300.0):
        s = copy.deepcopy(R1); s["name"] = f"R1_TB{T:g}"; s["B"]["T_tel"] = T; sweep.append(s)
    s = copy.deepcopy(R1); s["name"] = "R1_quietB"; s["B"]["sigma"] /= 2; sweep.append(s)
    s = copy.deepcopy(R1); s["name"] = "R1_tau15"
    s["A"]["tau"] = s["B"]["tau"] = 15.0; sweep.append(s)
    for buf in (50, 500):
        s = copy.deepcopy(R1); s["name"] = f"R1_buf{buf}"
        for p in "AB":
            s[p]["k"] = max(2, round(buf / (PKT_BITS / (s[p]["mbps"] * 1e6) * 1e3)))
        sweep.append(s)
    return base, sweep


TWIN_ERRORS = {"đúng": {}, "σ×0.7": {"sig": 0.7}, "σ×1.3": {"sig": 1.3}, "τ×0.5": {"tau": 0.5},
               "τ×2": {"tau": 2.0}, "ρ̄−0.05": {"rho": -0.05}, "ρ̄+0.05": {"rho": 0.05}}
ALPHAS = (0.01, 0.002)
EPS_EXTRA = 8.1                                                 # ε bằng SESOI VoIP: chỉ báo cáo, không dùng để quyết định


def GO_RULE(r, alpha):
    """Một lần đánh giá 'đạt' nếu đủ CẢ 4 nhóm điều kiện (khóa trước khi chạy)."""
    return bool(r["oos_lo"] > 0                                 # 1) ngoài mẫu: K2 hơn SC, cận dưới CI > 0
                and r["fr_pct"] >= 3.0 and r["fr_lo"] > 0       # 2) cùng harm: Δ ≥ 3% headroom, bootstrap > 0
                and r["harm_ratio"] <= 0.7                       # 3) K2 cần ≤ 70% số lần hại của SC để có cùng gain
                and r["oos_hSC"] <= 1.5 * alpha and r["oos_hK2"] <= 1.5 * alpha)   # 4) giữ ngân sách harm


# ---------------------------------------------- mô phỏng + twin --------------------------------------------------
_CURVES = {}


def curve_of(p):
    s_ms = PKT_BITS / (p["mbps"] * 1e6) * 1e3
    key = (p["k"], round(s_ms, 9))
    if key not in _CURVES:
        _CURVES[key] = DelayCurve(p["k"], s_ms)
    return _CURVES[key]


def simulate(seed, sc):
    """Một seed DES với hai path KHÁC tốc độ/buffer (dùng lại des_path đã kiểm)."""
    rng = np.random.default_rng(seed)
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
        w = des_path(rng, pc, pp, t_dec, t_end, dt)
        out[name] = dict(rhohat=w["rhohat"], age=w["age"], D=w["D_des"])
    return out


def twin_view2(cA, cB, mA, vA, mB, vB, eps):
    """Như twin.twin_view nhưng mỗi path một đường cong delay riêng."""
    sA, sB = np.sqrt(2 * vA)[:, None], np.sqrt(2 * vB)[:, None]
    TA, TB = cA(mA[:, None] + sA * GH_X[None, :]), cB(mB[:, None] + sB * GH_X[None, :])
    Ibar = (TA - TB) @ GH_W
    p_dn = norm.sf((cB.inverse(TA + eps) - mB[:, None]) / np.sqrt(vB)[:, None]) @ GH_W
    p_up = norm.sf((cA.inverse(TB + eps) - mA[:, None]) / np.sqrt(vA)[:, None]) @ GH_W
    return Ibar, p_dn, p_up


def decisions(world, sc, err, eps):
    """Twin (có thể đoán SAI tham số theo err) → các đại lượng cho từng quyết định."""
    post = {}
    for name in "AB":
        p, o = sc[name], world[name]
        S = PKT_BITS / (p["mbps"] * 1e6)
        rho_t = p["rho"] + err.get("rho", 0.0)
        post[name] = posterior(o["rhohat"], o["age"] + sc["a"], p["T_tel"], sc["H"], rho_t,
                               p["sigma"] * err.get("sig", 1.0), p["tau"] * err.get("tau", 1.0), rho_t * S / p["T_tel"])
    cA, cB = curve_of(sc["A"]), curve_of(sc["B"])
    Ibar, pdn, pup = twin_view2(cA, cB, *post["A"], *post["B"], eps)
    return dict(Iplug_A=cA(world["A"]["rhohat"]) - cB(world["B"]["rhohat"]), Ibar_A=Ibar, pdn_A=pdn, pup_A=pup,
                I_A=world["A"]["D"] - world["B"]["D"], age_A=world["A"]["age"], age_B=world["B"]["age"])


# ---------------------------------------------- đánh giá ---------------------------------------------------------
def evaluate(cal_d, test_d, alpha, eps):
    h0 = 0.0                                                    # quỹ đạo tham chiếu = S0 tune bằng hại thật (như bậc C)
    for _ in range(2):
        c = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_d])
        h0 = tune_threshold(c["Iplug"], c["I"], (c["I"] < -eps).astype(float), alpha)
    cal = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_d])
    test = [orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in test_d]

    fr = matched(_pool(test), alpha, eps)                       # so ở cùng harm trên test
    rng = np.random.default_rng(54321)
    boot = [matched(_pool([test[i] for i in rng.integers(0, len(test), len(test))]), alpha, eps)["width_ms"]
            for _ in range(N_BOOT)]

    scal, n = ranking_scores(cal), len(cal["I"])                # ngoài mẫu: ngưỡng học trên calibration
    thr = {r: optimum(s, cal["I"], cal["I"] < -eps, alpha * n)["threshold"] for r, s in scal.items()}
    rows = []
    for t in test:
        ss, harmful = ranking_scores(t), t["I"] < -eps
        rows.append({**{f"g_{r}": float(((ss[r] > thr[r]) * t["I"]).mean()) for r in ss},
                     **{f"h_{r}": float(((ss[r] > thr[r]) & harmful).mean()) for r in ss}})
    w = np.array([x["g_K2"] - x["g_SC"] for x in rows])
    ci = stats.t.ppf(0.975, len(w) - 1) * w.std(ddof=1) / np.sqrt(len(w))
    # strict_frontier returns harm needed / alpha, not / harm actually used by SC.
    h_needed = fr["harm_ratio"] * alpha
    ratio = actual_harm_ratio(h_needed, fr["harm_SC"])
    return dict(headroom=fr["headroom"], fr_ms=fr["width_ms"], fr_pct=fr["width_pct"],
                fr_lo=float(np.percentile(boot, 2.5)), fr_hi=float(np.percentile(boot, 97.5)),
                harm_ratio=ratio, harm_ratio_budget=fr["harm_ratio"],
                fr_hSC=fr["harm_SC"], fr_hK2=fr["harm_K2"], harm_needed_K2=h_needed,
                oos_ms=float(w.mean()), oos_lo=float(w.mean() - ci), oos_hi=float(w.mean() + ci),
                oos_hSC=float(np.mean([x["h_SC"] for x in rows])), oos_hK2=float(np.mean([x["h_K2"] for x in rows])))


def actual_harm_ratio(needed, used_sc):
    """A zero-harm SC cannot demonstrate a percentage reduction in harm."""
    return float(needed / used_sc) if used_sc > 0 else float('inf')


def save_rows(rows):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def run_world(sc, variants):
    t0 = time.time()
    cal_w, test_w = [simulate(s, sc) for s in CAL], [simulate(s, sc) for s in TEST]
    out = []
    for (err_name, alpha, eps) in variants:
        err = TWIN_ERRORS[err_name]
        r = evaluate([decisions(w, sc, err, eps) for w in cal_w], [decisions(w, sc, err, eps) for w in test_w], alpha, eps)
        r.update(name=sc["name"], twin=err_name, alpha=alpha, eps=eps, passed=GO_RULE(r, alpha),
                 nflows_min=min(sc["A"]["n_flows"], sc["B"]["n_flows"]))
        out.append(r)
        print(f"  {sc['name']:12s} twin={err_name:7s} α={alpha:<5} ε={eps:<4} | OOS {r['oos_ms']:+7.3f} [{r['oos_lo']:+.3f}] ms | "
              f"cùng harm {r['fr_ms']:+7.3f} ms ({r['fr_pct']:5.1f}%, lo {r['fr_lo']:+.3f}) | harm ratio {r['harm_ratio']:.2f} | "
              f"hSC/α {r['oos_hSC'] / alpha:.2f} hK2/α {r['oos_hK2'] / alpha:.2f} | {'ĐẠT' if r['passed'] else '—'}", flush=True)
    print(f"  ({time.time() - t0:.0f} s)")
    return out


def verdict(rows, name):
    conditional = None
    for alpha in ALPHAS:
        base = [r for r in rows if r["name"] == name and r["alpha"] == alpha and r["eps"] == 1.0]
        ok_base = any(r["passed"] for r in base if r["twin"] == "đúng")
        ok_all = len(base) == len(TWIN_ERRORS) and {r['twin'] for r in base} == set(TWIN_ERRORS) and all(r["passed"] for r in base)
        if ok_base:
            ms = next(r["oos_lo"] for r in base if r["twin"] == "đúng")
            if ok_all:
                return "GO", alpha, ms
            if conditional is None:
                conditional = ("GO CÓ ĐIỀU KIỆN (nhạy với sai số của twin)", alpha, ms)
    return conditional or ("NO-GO", None, None)


def main():
    base, sweep = scenarios()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = dict(cal_seeds=list(CAL), test_seeds=list(TEST), n_boot=N_BOOT,
                    alphas=ALPHAS, primary_epsilon_ms=1.0, report_only_epsilon_ms=EPS_EXTRA,
                    twin_errors=TWIN_ERRORS, base=base, sweep=sweep,
                    source_status='source-inspired assumptions; citations and mapping not independently verified here')
    (OUT.parent/'go_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    rows = []
    print("=== PHẦN 1+2: kịch bản thực tế + twin đoán sai tham số ===")
    for sc in base:
        print(f"{sc['name']}: số flow nền tối thiểu ≈ {min(sc['A']['n_flows'], sc['B']['n_flows']):.0f}")
        variants = [(e, a, sc["eps_ms"]) for a in ALPHAS for e in TWIN_ERRORS] + [("đúng", 0.002, EPS_EXTRA)]
        rows += run_world(sc, variants)
        save_rows(rows)
    print("=== PHẦN 3: quét biên quanh R1 (twin đúng, α = 0,2%) ===")
    for sc in sweep:
        rows += run_world(sc, [("đúng", 0.002, sc["eps_ms"])])
        save_rows(rows)
    print(f"\nĐã lưu {OUT}\n=== KẾT LUẬN ===")
    for sc in base:
        v, alpha, ms = verdict(rows, sc["name"])
        extra = "" if alpha is None else f" (ở α = {alpha}; cận dưới Δ ngoài mẫu = {ms:.2f} ms; SESOI VoIP 8,1 ms → {'VƯỢT' if ms >= 8.1 else 'chưa vượt'})"
        print(f"  {sc['name']}: {v}{extra}")
    labels = [verdict(rows, sc['name'])[0] for sc in base]
    overall = ('GO' if 'GO' in labels else 'GO CÓ ĐIỀU KIỆN' if any(x.startswith('GO CÓ') for x in labels) else 'NO-GO')
    print(f"  Tổng: {overall}. Quét biên và ε=8,1 ms không dùng để quyết định.")


if __name__ == "__main__":
    main()
