"""f05b (post hoc sau f05) — K2 và ngưỡng tĩnh trên tâm SC có chọn cùng epoch không?

Mục tiêu: phân biệt hai trường hợp đều có K2 − SC gần 0: hai luật thật sự chọn cùng tập epoch, hoặc chúng chọn
khác nhưng gain triệt tiêu. Script tái dùng nguyên thế giới, oracle, seed và cách tune của f05; không có outcome mới,
không đổi quyết định đã khóa. Provenance: Codex (AI) viết theo mô tả lesson; tác giả kiểm.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f02_existence_surrogate as f
import f04b_des_gap as g
import f05_oracle_age as q


def decisions(name, regime):
    """Dựng lại đúng dữ liệu/evaluation f05 và trả thống kê quyết định cho từng oracle."""
    cell, stream = g.CELLS[name]
    psa = f.PSA(cell.k)
    eps_ms = f.EPS_OVER_S * cell.s_ms
    jitter = regime == "A1"
    sim = lambda seeds, st: [q.simulate(cell, psa, s, st, jitter) for s in seeds]
    eps = dict(
        cal=sim(f.CAL_SEEDS, stream),
        test=sim(f.TEST_SEEDS, stream),
        orc=sim(f.ORACLE_SEEDS, stream) + sim(f.ORACLE_SEEDS, stream + q.EXTRA),
    )

    tuned = {kind: f.tune_static(eps["cal"], kind, 0.0, eps_ms) for kind in ("abs", "rel")}
    static_kind = min(tuned, key=lambda kind: tuned[kind][1])
    threshold = tuned[static_kind][0]
    ref = lambda ep: q.orient_ext(ep, f.static_run(ep, static_kind, threshold)[1][0])
    r_orc = [ref(ep) for ep in eps["orc"]]
    r_cal = [ref(ep) for ep in eps["cal"]]
    r_test = [q.orient_ext(ep, f.static_run(ep, static_kind, threshold)[1][0]) for ep in eps["test"]]

    rows = []
    for oracle_name, (feature_kind, n_bin, n_age, x2) in q.SPECS[regime].items():
        oracle = q.GridOracle(
            r_orc if x2 else r_orc[:len(f.ORACLE_SEEDS)], feature_kind, n_bin, n_age, eps_ms
        )
        cal_predictions = [oracle.predict(o) for o in r_cal]
        lam = f.tune_lambda(cal_predictions, 0.0)
        center_threshold = q.tune_center(cal_predictions)
        disagree = total = 0
        for o in r_test:
            ibar, p_down = oracle.predict(o)
            k2 = (ibar - lam * p_down) > 0
            sc = ibar > center_threshold
            disagree += int(np.count_nonzero(k2 != sc))
            total += len(k2)
        rows.append((oracle_name, disagree, total, int(np.count_nonzero(oracle.ibar > 0)), len(oracle.ibar)))
    return rows


if __name__ == "__main__":
    print("f05b | KHÁM PHÁ post hoc | tỉ lệ epoch test có quyết định K2 ≠ SC")
    print(f"{'ô':22s} {'tuổi':4s} {'oracle':7s} {'bất đồng':>10s} {'tỉ lệ':>8s} {'ô Ī>0':>11s}")
    rates = []
    for cell_name in q.CELLS:
        for age_regime in ("A0", "A1"):
            for oracle_name, n_disagree, n_total, n_positive, n_cells in decisions(cell_name, age_regime):
                rate = 100.0 * n_disagree / n_total
                rates.append(rate)
                print(f"{cell_name:22s} {age_regime:4s} {oracle_name:7s} {n_disagree:5d}/{n_total:<4d} "
                      f"{rate:7.2f}% {n_positive:4d}/{n_cells}")
    print(f"\nKhoảng tỉ lệ bất đồng qua {len(rates)} tổ hợp: {min(rates):.2f}%–{max(rates):.2f}%")
