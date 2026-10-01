"""Cổng GO v1: thêm GIỚI HẠN TẦN SUẤT ĐỔI và CHI PHÍ ĐỔI (bài kiểm GO v0 coi đổi đường là miễn phí).
SC: đổi nếu Ī > h.   K2 hai ràng buộc: đổi nếu Ī − μ − λ·p₋ > 0  (μ = "giá" của mỗi lần đổi).
Mọi tham số (h; λ, μ) chọn trên CALIBRATION với cả ràng buộc harm lẫn ràng buộc tần suất/chi phí; đo NGOÀI MẪU trên test.
Chạy từ gốc repo:   python -m experiments.scan.go_switch"""
import csv
import json
import time
from pathlib import Path

import numpy as np
from scipy import stats

from experiments.scan import go_test as g
from experiments.scan.cell import _pool
from experiments.scan.rules import orient, s0_trajectory, tune_threshold
from experiments.scan.strict_frontier import prefixes

OUT = Path("results/go_test/go_switch_v1.csv")
MUS = np.r_[0.0, np.linspace(1.0, 80.0, 80)]                     # lưới "giá mỗi lần đổi" μ (ms) cho K2
SETTINGS = [("không giới hạn", None, 0.0), ("1 lần/30 s", 30.0, 0.0), ("1 lần/60 s", 60.0, 0.0),
            ("1 lần/120 s", 120.0, 0.0), ("chi phí 5 ms/lần", None, 5.0), ("chi phí 10 ms/lần", None, 10.0)]
ALPHAS = (0.002, 0.01)
PRIMARY = "1 lần/30 s"                                           # tiêu chí GO v1 đọc ở thiết lập này (KHÓA)


def save_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def GO_SWITCH(r, alpha, period):
    """Đạt nếu: K2 hơn SC ngoài mẫu (cận dưới CI > 0) VÀ hơn ≥ 10% gain ròng của SC
    VÀ cả hai giữ ngân sách harm (≤ 1,5α) VÀ tần suất đổi thực tế ≤ 1,2 × trần."""
    cap_ok = period is None or max(r["sw_SC"], r["sw_K2"]) <= 1.2 * r["H"] / period
    return bool(r["lo"] > 0 and r["d"] >= 0.10 * max(r["g_SC"], 1e-9) and cap_ok
                and r["h_SC"] <= 1.5 * alpha and r["h_K2"] <= 1.5 * alpha)


def k2_score(o, mu):
    s = np.full(len(o["Ibar"]), -np.inf)
    m = o["Ibar"] > mu
    s[m] = (o["Ibar"][m] - mu) / np.maximum(o["pdn"][m], 1e-300)
    return s


def fit(cal, eps, alpha, cap_frac, cost, rule):
    """Chọn tham số trên calibration: gain ròng lớn nhất với harm ≤ α·n VÀ số lần đổi ≤ trần."""
    n, harmful = len(cal["I"]), cal["I"] < -eps
    cap = n if cap_frac is None else cap_frac * n
    best_val, best = -np.inf, None
    for mu in (MUS if rule == "K2" else [None]):
        score = cal["Ibar"] if rule == "SC" else k2_score(cal, mu)
        cg, ch, cnt, thr = prefixes(score, cal["I"] - cost, harmful)
        ok = (ch <= alpha * n) & (cnt <= cap)
        j = int(np.argmax(np.where(ok, cg, -np.inf)))
        if cg[j] > best_val:
            best_val, best = cg[j], (mu, thr[j])
    return best


def act(o, rule, params):
    mu, thr = params
    return (o["Ibar"] if rule == "SC" else k2_score(o, mu)) > thr


def evaluate(cal_d, test_d, sc, alpha, eps, period, cost, seed_rows=None):
    h0 = 0.0
    for _ in range(2):
        c = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_d])
        h0 = tune_threshold(c["Iplug"], c["I"], (c["I"] < -eps).astype(float), alpha)
    cal = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal_d])
    test = [orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in test_d]
    cap_frac = None if period is None else sc["H"] / period
    params = {r: fit(cal, eps, alpha, cap_frac, cost, r) for r in ("SC", "K2")}
    per = {r: [] for r in ("SC", "K2")}
    for t in test:
        harmful = t["I"] < -eps
        for r in per:
            a = act(t, r, params[r])
            per[r].append(((a * (t["I"] - cost)).mean(), (a & harmful).mean(), a.mean()))
    w = np.array([k[0] - s[0] for k, s in zip(per["K2"], per["SC"])])
    ci = stats.t.ppf(0.975, len(w) - 1) * w.std(ddof=1) / np.sqrt(len(w))
    m = lambda r, i: float(np.mean([x[i] for x in per[r]]))
    if seed_rows is not None:
        for i, (s, k) in enumerate(zip(per['SC'], per['K2'])):
            seed_rows.append(dict(seed=list(g.TEST)[i], g_SC=float(s[0]), g_K2=float(k[0]),
                                  h_SC=float(s[1]), h_K2=float(k[1]), sw_SC=float(s[2]),
                                  sw_K2=float(k[2]), d=float(k[0]-s[0])))
    extra = {}
    for rule in params:
        ac = act(cal, rule, params[rule])
        extra[f'cal_sw_{rule}'] = float(ac.mean())
        extra[f'cal_h_{rule}'] = float((ac & (cal['I'] < -eps)).mean())
        extra[f'threshold_{rule}'] = float(params[rule][1])
    return dict(d=float(w.mean()), lo=float(w.mean() - ci), hi=float(w.mean() + ci),
                g_SC=m("SC", 0), g_K2=m("K2", 0), h_SC=m("SC", 1), h_K2=m("K2", 1),
                sw_SC=m("SC", 2), sw_K2=m("K2", 2), mu_K2=params["K2"][0], H=sc["H"], **extra)


def main():
    base, sweep = g.scenarios()
    rows, t0 = [], time.time()
    seed_rows = []
    OUT.parent.mkdir(parents=True, exist_ok=True)
    (OUT.parent/'go_switch_manifest.json').write_text(json.dumps(dict(
        cal_seeds=list(g.CAL), test_seeds=list(g.TEST), scenarios=base+sweep,
        alphas=ALPHAS, settings=SETTINGS, mus=MUS.tolist(), primary=PRIMARY,
        test_status='reused GO v0 test; not a fresh independent holdout'), ensure_ascii=False, indent=2))
    for sc in base + sweep:
        cal_w, test_w = [g.simulate(s, sc) for s in g.CAL], [g.simulate(s, sc) for s in g.TEST]
        cal_d = [g.decisions(w, sc, {}, sc["eps_ms"]) for w in cal_w]
        test_d = [g.decisions(w, sc, {}, sc["eps_ms"]) for w in test_w]
        for alpha in ALPHAS:
            for label, period, cost in SETTINGS:
                per_seed = []
                r = evaluate(cal_d, test_d, sc, alpha, sc["eps_ms"], period, cost, per_seed)
                r.update(name=sc["name"], alpha=alpha, setting=label, passed=GO_SWITCH(r, alpha, period))
                rows.append(r)
                seed_rows.extend(dict(name=sc['name'], alpha=alpha, setting=label, **sr) for sr in per_seed)
                save_csv(OUT, rows)
                save_csv(OUT.parent/'go_switch_seeds.csv', seed_rows)
                print(f"{sc['name']:12s} α={alpha:<5} {label:16s} | Δ ngoài mẫu {r['d']:+.3f} [{r['lo']:+.3f}, {r['hi']:+.3f}] ms "
                      f"| gain ròng SC {r['g_SC']:.3f} K2 {r['g_K2']:.3f} | đổi SC 1/{1 / max(r['sw_SC'], 1e-9):.0f} "
                      f"K2 1/{1 / max(r['sw_K2'], 1e-9):.0f} quyết định | {'ĐẠT' if r['passed'] else '—'}", flush=True)
        print(f"  ({time.time() - t0:.0f} s)")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nĐã lưu {OUT}\n=== KẾT LUẬN GO v1 (đọc ở '{PRIMARY}', kịch bản thực tế R1/R2) ===")
    for sc in base:
        ok = [a for a in ALPHAS for r in rows if r["name"] == sc["name"] and r["alpha"] == a
              and r["setting"] == PRIMARY and r["passed"]]
        print(f"  {sc['name']}: {'GO' if ok else 'NO-GO khi đổi đường bị giới hạn'}" + (f" (α = {ok[0]})" if ok else ""))
    print("  Các thiết lập khác và quét biên: để vẽ RANH GIỚI (đổi rẻ đến đâu thì bất định còn có giá trị), không dùng để quyết định.")


if __name__ == "__main__":
    main()
