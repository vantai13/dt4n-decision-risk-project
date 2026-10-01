# Chạy từ gốc repo:  python -m experiments.gocheck.posthoc_switch_errors
"""HẬU KIỂM 2 (khám phá): tại lúc đổi, twin dự đoán delay của path HIỆN TẠI và path ĐÍCH sai thế nào so với thật?"""
import copy
import numpy as np
from experiments.gocheck.info_arrangement import FAST, SLOW, arrangement_inputs, load_info_worlds, tune_info
from experiments.gocheck.rollout import score
from experiments.scan import go_test as g
from experiments.scan.twin import GH_W, GH_X, posterior
from experiments.scan.world import PKT_BITS

R1 = g.scenarios()[0][0]
cal_w = load_info_worlds(R1, range(94001, 94021), "94001"); test_w = load_info_worlds(R1, range(95001, 95021), "95001")
cal_in = [arrangement_inputs(w, R1) for w in cal_w]; test_in = [arrangement_inputs(w, R1) for w in test_w]

def pred_delay(w, speed_A, speed_B):
    """E[T(ρ)] twin dự đoán cho mỗi path (cùng cách tính với go_test.decisions)."""
    out = {}
    for name, speed in (("A", speed_A), ("B", speed_B)):
        p = R1[name]; src = w[name] if p["T_tel"] == speed else w[name + "_x"]
        S = PKT_BITS / (p["mbps"] * 1e6)
        m, v = posterior(src["rhohat"], src["age"] + R1["a"], speed, R1["H"], p["rho"], p["sigma"], p["tau"], p["rho"] * S / speed)
        out[name] = g.curve_of(p)(m[:, None] + np.sqrt(2 * v)[:, None] * GH_X[None, :]) @ GH_W
    return out

for arr in ("FIX", "FF"):
    for rule in ("SC", "K2"):
        thr, _ = tune_info(arr, rule, cal_in, cal_w, 0.002, 0)
        rows = []
        for ci, w in zip(test_in, test_w):
            onA_info, onB_info = ci[arr]
            pA = pred_delay(w, FAST, SLOW)                                  # thông tin khi đang ở A (cả FIX và FF)
            pB = pA if arr == "FIX" else pred_delay(w, SLOW, FAST)          # khi đang ở B
            DA, DB = w["A"]["D"], w["B"]["D"]; onA = True
            for k in range(len(DA)):
                ib, pp = (onA_info["Ibar_A"][k], onA_info["pdn_A"][k]) if onA else (-onB_info["Ibar_A"][k], onB_info["pup_A"][k])
                if score(rule, ib, pp) > thr:
                    if onA: rows.append((pA["A"][k], DA[k], pA["B"][k], DB[k]))
                    else:   rows.append((pB["B"][k], DB[k], pB["A"][k], DA[k]))
                    onA = not onA
        r = np.array(rows)
        print(f"{arr:3s} {rule}: {len(r):4d} lần đổi | HIỆN TẠI: dự đoán TB {r[:,0].mean():6.1f} → thật {r[:,1].mean():6.1f} ms "
              f"(trung vị {np.median(r[:,0]):5.1f} → {np.median(r[:,1]):5.1f}) | ĐÍCH: dự đoán TB {r[:,2].mean():5.1f} → thật {r[:,3].mean():5.1f} ms "
              f"| % lần đổi mà hiện tại bị thổi phồng > 20 ms: {100*np.mean(r[:,0] - r[:,1] > 20):4.1f}%")
