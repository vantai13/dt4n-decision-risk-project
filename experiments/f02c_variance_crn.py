"""f02c — Chẩn đoán độ ổn định của gap F2 tại P2 (KHÔNG phải lần chạy F2 mới, KHÔNG đổi phán quyết đã đăng ký).

Ba câu hỏi về CÔNG CỤ ĐO (validity), không phải về kết quả:
  A. Phương sai của gap đến từ đâu?
  B. Cùng cấu hình, khác luồng ngẫu nhiên thì ước lượng gap dao động bao nhiêu?
  C. So sánh biến thể có paired (CRN) không? Kết luận "bỏ tuổi làm gap tăng" có vững không?
Seed: tái dùng đúng seed F2 (cal 9701–9708, test 9711–9718, oracle 9801–9999).
Khoá luồng: 902 = đúng luồng P2 của F2 (tái lập); 950–953 = luồng mới cùng seed (chỉ để đo độ dao động).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f02_existence_surrogate as f

CACHE = {}


def evaluate(cell, stream, vid):
    """Tái dựng run_cell (c = 0) nhưng giữ số liệu TỪNG seed test để phân tích."""
    psa = CACHE.setdefault(cell.k, f.PSA(cell.k))
    eps_ms = f.EPS_OVER_S * cell.s_ms
    sim = lambda seeds: [f.simulate(cell, psa, s, stream, vid) for s in seeds]
    cal, test, orc = sim(f.CAL_SEEDS), sim(f.TEST_SEEDS), sim(f.ORACLE_SEEDS)
    tuned = {kd: f.tune_static(cal, kd, 0.0, eps_ms) for kd in ("abs", "rel")}
    kind = min(tuned, key=lambda kd: tuned[kd][1])
    thr = tuned[kind][0]
    ref = lambda ep: f.orient(ep, f.static_run(ep, kind, thr)[1][0])
    oracle = f.BinOracle([ref(ep) for ep in orc], eps_ms)
    lam = f.tune_lambda([oracle.predict(ref(ep))[:2] for ep in cal], 0.0)
    out = dict(kind=kind, J={k: v[1] for k, v in tuned.items()}, lam=lam, gap=[], n_dis=[], contrib=[], dharm=[])
    for ep in test:
        act, cur = f.static_run(ep, kind, thr)
        o = f.orient(ep, cur[0])
        ibar, pdn, _ = oracle.predict(o)
        a_st, a_k2 = act[0], (ibar - lam * pdn) > 0
        contrib = (a_k2.astype(float) - a_st) * o["I"]
        harm_evt = o["I"] < -eps_ms
        out["gap"].append(contrib.mean())
        out["n_dis"].append(int((a_k2 != a_st).sum()))
        out["contrib"].append(contrib[a_k2 != a_st])
        out["dharm"].append(np.mean(a_k2 * harm_evt) - np.mean(a_st * harm_evt))
    out["gap"] = np.array(out["gap"])
    return out


def show(label, gaps):
    m, h = f.ci(gaps)
    print(f"    {label:34s} {m:+.3f} ± {h:.3f} ms")


if __name__ == "__main__":
    p2 = f.PRIMARY["P2"]
    base = evaluate(p2, 902, 0)
    print("A. Giải phẫu phương sai (P2, luồng 902 = đúng F2)")
    print(f"    gap = {base['gap'].mean():+.3f} ms; λ = {base['lam']:.1f} ms; họ tĩnh chọn '{base['kind']}', "
          f"J(abs) = {base['J']['abs']:.2f}, J(rel) = {base['J']['rel']:.2f} ms")
    c = np.concatenate(base["contrib"])
    print(f"    epoch bất đồng mỗi seed: {base['n_dis']} / {f.N_EPOCH}")
    print(f"    đóng góp ở epoch bất đồng: TB {c.mean():+.1f} ms, sd {c.std():.1f} ms  (tín hiệu/nhiễu ≈ {c.mean()/c.std():.2f})")
    print(f"    harm(K2) − harm(tĩnh) theo seed (điểm %): {np.round(np.array(base['dharm']) * 100, 2)}")
    print(f"    => mỗi 0,1 điểm % harm 'đáng giá' ≈ λ × 0,001 = {base['lam'] * 1e-3:.2f} ms gain")

    print("\nB. Cùng cấu hình P2, khác luồng ngẫu nhiên")
    reps = [evaluate(p2, s, 0) for s in (950, 951, 952, 953)]
    for s, r in zip((950, 951, 952, 953), reps):
        show(f"luồng {s} (họ tĩnh '{r['kind']}')", r["gap"])
    means = np.array([base["gap"].mean()] + [r["gap"].mean() for r in reps])
    print(f"    SD giữa 5 luồng của ước lượng gap = {means.std(ddof=1):.3f} ms (min {means.min():+.3f}, max {means.max():+.3f})")

    print("\nC. Biến thể: KHÔNG paired (như F2) so với CRN (cùng luồng tải + nhiễu)")
    variants = {k: v for k, v in f.variants(p2).items() if k != "control"}
    unpaired = {k: (base if k == "base" else evaluate(v, 902, i)) for i, (k, v) in enumerate(variants.items())}
    crn = {k: (base if k == "base" else evaluate(v, 902, 0)) for k, v in variants.items()}
    for name in variants:
        show(f"{name:10s} không paired", unpaired[name]["gap"])
        show(f"{name:10s} CRN", crn[name]["gap"])
    for a in ("age_only", "noise_only"):
        show(f"{a} − base (CRN, ghép cặp)", crn[a]["gap"] - crn["base"]["gap"])
