"""rollout_v4 — KHÁM PHÁ (POST HOC). Đòn phản biện mạnh nhất cho R3: bảng ngưỡng mịn hơn có bắt kịp K2 không?

SCtab24: ngưỡng trên Ī theo (chiều × tuổi path đích 4 bucket × tải đo cuối của path đích 3 bucket) = 24 tham số,
         coordinate descent 4 vòng khởi đầu từ SCtab (8 tham số). Cùng thông tin twin có (tuổi, ρ̂), cùng hold-down.
Twin dự đoán đúng chân trời = hold-down. Seed test 89001–89020 đã được Claude chạy trong sandbox; calibration 86001–86020.
Đây là tái lập POST HOC, không phải kiểm định trên seed chưa từng dùng.
Chạy:  python -m experiments.scan.rollout_v4 | tee results/go_test/rollout_v4_output.txt
"""
import argparse
import csv
import time
from pathlib import Path

import numpy as np
from numba import njit

from experiments.scan import rollout_v2 as v2
from experiments.scan import rollout_v3 as v3

TEST_NEW = range(89001, 89021)
HD, ALPHA = 30, 0.002
RHO_EDGES = np.array([0.75, 0.90])          # tải đo cuối của path đích → 3 bucket
NR = len(RHO_EDGES) + 1


@njit(cache=True)
def rollout_tab24(ibA, agA, agB, rhA, rhB, DA, DB, tab, a_edges, r_edges, hd, eps=1.0):
    n_pol, n = tab.shape[0], len(DA)
    na, nr = len(a_edges) + 1, len(r_edges) + 1
    delay, nsw, harm = np.zeros(n_pol), np.zeros(n_pol), np.zeros(n_pol)
    for p in range(n_pol):
        cur, last = 0, -10**9
        for e in range(n):
            ib, ag, rh = (ibA[e], agB[e], rhB[e]) if cur == 0 else (-ibA[e], agA[e], rhA[e])
            if e - last >= hd:
                b = 0
                while b < na - 1 and ag >= a_edges[b]:
                    b += 1
                c = 0
                while c < nr - 1 and rh >= r_edges[c]:
                    c += 1
                if ib > tab[p, (cur * na + b) * nr + c]:
                    nsw[p] += 1
                    gain = DA[e] - DB[e] if cur == 0 else DB[e] - DA[e]
                    if gain < -eps:
                        harm[p] += 1
                    cur, last = 1 - cur, e
            delay[p] += DA[e] if cur == 0 else DB[e]
    return delay, nsw, harm


def run24(data, tab):
    res = audit24(data, tab)
    return res[0], res[2]


def audit24(data, tab, eps=1.0):
    """Đo harm thật của bảng 24, không sửa objective/tune trong code được cung cấp."""
    res = [rollout_tab24(d["Ibar_A"], d["age_A"], d["age_B"], d["rh_A"], d["rh_B"], d["DA"], d["DB"],
                         tab, v2.AGE_EDGES, RHO_EDGES, HD, eps) for d in data]
    n = len(data[0]["DA"])
    return tuple(np.array([r[i] for r in res]) / n for i in (0, 2, 1))


def tune24(cal, start8):
    """Khởi đầu từ SCtab 8 tham số (chiều × tuổi), nhân ra theo bucket tải, rồi coordinate descent."""
    grid = v2.thr_grid(np.concatenate([d["Ibar_A"] for d in cal]))
    best = np.repeat(start8, NR)                  # thứ tự (cur, tuổi, tải) khớp với rollout_tab24
    for _ in range(4):
        for c in range(len(best)):
            tab = np.repeat(best[None, :], len(grid), 0)
            tab[:, c] = grid
            best = tab[int(np.argmin(run24(cal, tab)[0].mean(0)))].copy()   # harm không cắn ở hold-down 30 s
    return best


def with_rh(data, worlds_raw):
    for d, w in zip(data, worlds_raw):
        d["rh_A"], d["rh_B"] = w["A"]["rhohat"], w["B"]["rhohat"]
    return data


WORLD_NAMES = ("R1_dualISP", "R3_outage", "R3_outageB")


def result_path(names, append):
    if len(names) != len(set(names)):
        raise ValueError("Mỗi thế giới chỉ được chạy một lần trong một lệnh.")
    if not append:
        return v2.begin_results("rollout_v4")
    output = Path("results/go_test/rollout_v4_seeds.csv")
    with output.open() as f:
        existing = {row["world"] for row in csv.DictReader(f)}
    if existing.intersection(names):
        raise ValueError("Không append thế giới đã có trong CSV; tránh trùng seed.")
    return output


def main(names=WORLD_NAMES, append=False):
    t0 = time.time()
    output = result_path(names, append)
    by_name = {sc["name"]: sc for sc in v2.worlds()}
    for name in names:
        sc = by_name[name]
        cal_w = [v2.simulate(s, sc) for s in v2.CAL]
        test_w = [v2.simulate(s, sc) for s in TEST_NEW]
        cal = with_rh(v3.twin_for(cal_w, sc, HD), cal_w)
        test = with_rh(v3.twin_for(test_w, sc, HD), test_w)
        pol = v2.tune(cal, sc["eps_ms"], ALPHA, HD)
        tab24 = tune24(cal, pol["SCtab"][2])
        cal_audit = audit24(cal, tab24[None, :], sc["eps_ms"])
        test_audit = audit24(test, tab24[None, :], sc["eps_ms"])
        v2.record_results(output, sc, ALPHA, HD, HD, pol, cal, test, TEST_NEW,
                          extra=[("SCtab24", 1, 0.0, tab24, cal_audit, test_audit)])
        dl = {}
        for r in v2.RULES:
            kd, m, tab = pol[r]
            dl[r] = v2.run(test, np.array([kd]), np.array([m]), tab[None, :], sc["eps_ms"], HD)[0][:, 0]
        dl["SCtab24"] = run24(test, tab24[None, :])[0][:, 0]
        cal24 = run24(cal, tab24[None, :])[0][:, 0].mean()
        cal8 = v2.run(cal, np.array([1]), np.array([0.0]), pol["SCtab"][2][None, :], sc["eps_ms"], HD)[0][:, 0].mean()
        print(f"\n######## {name} | hold-down {HD} s, twin H_tw = {HD} s | test seed tái lập 89001–89020 | "
              f"{time.time() - t0:.0f} s")
        print("  delay TB test: " + " ".join(f"{r} {dl[r].mean():.2f}" for r in (*v2.RULES, "SCtab24")))
        print(f"  calibration (trong mẫu): SCtab {cal8:.3f} → SCtab24 {cal24:.3f} ms")
        cal_k2 = v2.run(cal, np.array([pol["K2"][0]]), np.array([pol["K2"][1]]),
                        pol["K2"][2][None, :], sc["eps_ms"], HD)[0].mean()
        print(f"  calibration K2 {cal_k2:.3f} ms | SCtab24 harm cal/test "
              f"{cal_audit[1].mean():.4%}/{test_audit[1].mean():.4%} (α {ALPHA:.1%})")
        for b in ("S0dir", "SCtab", "SCtab24"):
            m, lo, hi = v2.ci(dl[b] - dl["K2"])
            print(f"  {b:8s} − K2 = {m:+.3f} [{lo:+.3f}; {hi:+.3f}] ms  ({100 * m / dl[b].mean():+.1f}%)", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", action="append", choices=WORLD_NAMES,
                        help="Chỉ chạy thế giới được chọn; mặc định chạy cả ba.")
    parser.add_argument("--append", action="store_true",
                        help="Tiếp tục CSV sau gián đoạn, không chạy lại thế giới đã lưu.")
    args = parser.parse_args()
    main(WORLD_NAMES if args.world is None else tuple(args.world), args.append)
