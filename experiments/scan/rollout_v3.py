"""rollout_v3 — KHÁM PHÁ (POST HOC). Lợi thế của K2 khi có hold-down có phải chỉ vì twin dự đoán SAI CHÂN TRỜI không?

Hold-down T_hd = 30 s nghĩa là mỗi lần đổi bị khoá ít nhất 30 s, nhưng twin của go_test dự đoán cho khoảng giữ H = 1 s.
Ở đây CÙNG thế giới, CÙNG seed; chỉ đổi chân trời dự đoán của twin H_tw ∈ {1 s, T_hd}:
  posterior(tải TB trên [t + a, t + a + H_tw])  →  Ī, p₋ cho chân trời đó. Nhãn chấm điểm vẫn là delay từng giây.
Chỉ tiêu chính: DELAY TB NGƯỜI DÙNG TRẢI QUA trong rollout (harm báo kèm; ở T_hd = 30 s ràng buộc harm không cắn).
Chạy:  python -m experiments.scan.rollout_v3 | tee results/go_test/rollout_v3_output.txt
"""
import copy
import time

import numpy as np

from experiments.scan import go_test as g
from experiments.scan import rollout_v2 as v2

ALPHA = 0.002
CASES = [("R1_dualISP", 30), ("R3_outage", 30), ("R3_outageB", 30), ("R1_dualISP", 60), ("R3_outage", 60)]


def twin_for(worlds_raw, sc, h_tw):
    sc_tw = copy.deepcopy(sc)
    sc_tw["H"] = float(h_tw)                     # CHỈ đổi chân trời của twin; thế giới vẫn epoch 1 s
    out = []
    for w in worlds_raw:
        d = g.decisions(w, sc_tw, {}, sc["eps_ms"])
        d["DA"], d["DB"] = w["A"]["D"], w["B"]["D"]
        out.append(d)
    return out


def main():
    t0 = time.time()
    output = v2.begin_results("rollout_v3")
    by_name = {sc["name"]: sc for sc in v2.worlds()}
    cache = {}
    for name, hd in CASES:
        sc = by_name[name]
        if name not in cache:
            cache[name] = ([v2.simulate(s, sc) for s in v2.CAL], [v2.simulate(s, sc) for s in v2.TEST])
        cal_w, test_w = cache[name]
        print(f"\n######## {name} | hold-down {hd} s | α {ALPHA:.1%} | {time.time() - t0:.0f} s", flush=True)
        for h_tw in (1, hd):
            cal, test = twin_for(cal_w, sc, h_tw), twin_for(test_w, sc, h_tw)
            pol = v2.tune(cal, sc["eps_ms"], ALPHA, hd)
            v2.record_results(output, sc, ALPHA, hd, h_tw, pol, cal, test, v2.TEST)
            dl, hm, sw = {}, {}, {}
            for r in v2.RULES:
                kd, m, tab = pol[r]
                res = v2.run(test, np.array([kd]), np.array([m]), tab[None, :], sc["eps_ms"], hd)
                dl[r], hm[r], sw[r] = res[0][:, 0], res[1][:, 0], res[2][:, 0]
            cal_score = {r: v2.pick(*v2.run(cal, np.array([pol[r][0]]), np.array([pol[r][1]]), pol[r][2][None, :],
                                            sc["eps_ms"], hd)[:2], ALPHA)[1] for r in v2.RULES if r != "K2"}
            best = min(cal_score, key=cal_score.get)
            m, lo, hi = v2.ci(dl[best] - dl["K2"])
            print(f"  twin H_tw = {h_tw:2d} s | delay TB " + " ".join(f"{r} {dl[r].mean():.2f}" for r in v2.RULES) +
                  " | đổi/phút " + "/".join(f"{60 * sw[r].mean():.2f}" for r in v2.RULES) +
                  " | harm% " + "/".join(f"{100 * hm[r].mean():.2f}" for r in v2.RULES))
            print(f"      baseline mạnh nhất trên cal = {best}: {best} − K2 = {m:+.3f} [{lo:+.3f}; {hi:+.3f}] ms "
                  f"({100 * m / dl[best].mean():+.1f}% delay của baseline)", flush=True)


if __name__ == "__main__":
    main()
