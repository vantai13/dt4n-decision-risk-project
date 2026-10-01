# Chạy từ gốc repo:  python -m experiments.gocheck.posthoc_reliability
"""HẬU KIỂM (khám phá, KHÔNG thuộc tiền đăng ký): vì sao K2 thua SC ở FF?
(1) Độ tin của p₋ theo bin (mọi epoch có Ī > 0): xác suất hại twin dự đoán vs tần suất hại thật.
(2) Trong rollout α = 0,2%: lần đổi của mỗi luật — lợi kỳ vọng Ī vs lợi thật, p₋ vs hại thật."""
import numpy as np
from experiments.gocheck.info_arrangement import arrangement_inputs, load_info_worlds, tune_info
from experiments.gocheck.rollout import EPS, score
from experiments.scan import go_test as g

R1 = g.scenarios()[0][0]
cal_w = load_info_worlds(R1, range(94001, 94021), "94001"); test_w = load_info_worlds(R1, range(95001, 95021), "95001")
cal_in = [arrangement_inputs(w, R1) for w in cal_w]; test_in = [arrangement_inputs(w, R1) for w in test_w]

print("(1) ĐỘ TIN CỦA p₋ (test, mọi epoch có Ī > 0): dự đoán TB → hại thật [số epoch]")
edges = [0, 1e-5, 1e-4, 1e-3, 1e-2, 0.05, 0.2, 1.0001]
cases = {"FIX đang ở B → đích A TƯƠI": ("FIX", 1, "B"), "SYM đang ở B → đích A tươi": ("SYM", 1, "B"),
         "FIX đang ở A → đích B CŨ": ("FIX", 0, "A"), "FF  đang ở B → đích A CŨ": ("FF", 1, "B")}
for name, (arr, i, cur) in cases.items():
    P, H = [], []
    for ci, w in zip(test_in, test_w):
        d = ci[arr][i]
        ib = d["Ibar_A"] if cur == "A" else -d["Ibar_A"]
        p = d["pdn_A"] if cur == "A" else d["pup_A"]
        gain = (w["A"]["D"] - w["B"]["D"]) if cur == "A" else (w["B"]["D"] - w["A"]["D"])
        m = ib > 0; P.append(p[m]); H.append(gain[m] < -EPS)
    P, H = np.concatenate(P), np.concatenate(H)
    cells = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (P >= lo) & (P < hi)
        if m.sum() >= 50:
            cells.append(f"{P[m].mean():.0e}→{H[m].mean():.0e}[{m.sum()}]")
    print(f"  {name:28s} " + "  ".join(cells))

print("\n(2) LẦN ĐỔI TRONG ROLLOUT (test, α = 0,2%, cooldown 0)")
for arr in ("FIX", "FF"):
    for rule in ("SC", "K2"):
        thr, _ = tune_info(arr, rule, cal_in, cal_w, 0.002, 0)
        ibs, ps, gains = [], [], []
        for ci, w in zip(test_in, test_w):
            dA, dB = ci[arr]; DA, DB = w["A"]["D"], w["B"]["D"]; onA = True
            for k in range(len(DA)):
                ib, p = (dA["Ibar_A"][k], dA["pdn_A"][k]) if onA else (-dB["Ibar_A"][k], dB["pup_A"][k])
                if score(rule, ib, p) > thr:
                    ibs.append(ib); ps.append(p); gains.append((DA[k] - DB[k]) if onA else (DB[k] - DA[k])); onA = not onA
        ibs, ps, gains = map(np.array, (ibs, ps, gains))
        print(f"  {arr:3s} {rule}: {len(gains):5d} lần đổi | Ī TB {ibs.mean():6.2f} → lợi thật TB {gains.mean():6.2f} ms "
              f"| p₋ TB {ps.mean():.4f} → hại thật {np.mean(gains < -EPS):.4f} | lợi thật trung vị {np.median(gains):5.2f} ms")
