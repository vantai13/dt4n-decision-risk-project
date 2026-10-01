"""Xác nhận ứng viên của map v0 bằng thang 3 bậc, trên CÙNG thế giới DES ghép cặp, seed MỚI (dải đã để dành).
  Bậc A: tune bằng kỳ vọng twin, sự thật PSA  → bộ quét trên seed mới       (chết ở đây = may mắn khi quét)
  Bậc B: tune bằng hại THẬT,     sự thật PSA  → ép ngân sách harm thật       (chết ở đây = do p₋ của twin lệch)
  Bậc C: tune bằng hại THẬT,     sự thật DES  → sự thật là hàng đợi gói      (chết ở đây = do PSA lạc quan)
Chạy từ gốc repo:   python -m experiments.scan.confirm"""
import csv
import time
from pathlib import Path

from experiments.scan.cell import evaluate_cell, get_curve, twin_inputs
from experiments.scan.des_world import simulate_world_des
from experiments.scan.grid import controls, grid

CAL_SEEDS, TEST_SEEDS = range(30001, 30021), range(20001, 20021)    # dải để dành cho xác nhận — chưa từng dùng
OUT = Path("results/scan/confirm_v0.csv")

# Ô cần xác nhận — KHÓA TRƯỚC khi chạy: toàn bộ 21 ứng viên của map v0 + đối chứng âm
CELLS = ["m053", "m069", "m068", "m071", "m075", "m085", "m070", "m037", "m087", "m084", "m036",
         "m093", "m065", "m067", "m086", "m032", "m033", "m041", "m081", "m080", "m083"]

# Tiêu chí "xác nhận" ở mỗi bậc — KHÓA TRƯỚC khi chạy (chép y nguyên vào notes/map/confirm_spec.md)
HARM_SLACK = 1.5                 # harm thật trên seed kiểm tra của cả K2 lẫn SC phải ≤ 1,5·α


def confirmed(r, alpha):
    return bool(r["width_ms"] - r["width_ci"] > 0                   # độ rộng: cận dưới CI > 0
                and r["width_pct"] >= 2.0                           # ≥ 2% headroom
                and r["width_ms"] >= 0.20 * max(r["gain_SC"], 1e-9)  # ≥ 20% gain của SC
                and r["vs_best_ms"] - r["vs_best_ci"] > 0           # thắng cả baseline tốt nhất
                and r["harm_K2"] <= HARM_SLACK * alpha and r["harm_SC"] <= HARM_SLACK * alpha)


def decisions_paired(seed, cell, curve, eps_ms):
    """Một seed DES → hai bộ quyết định GIỐNG HỆT nhau, chỉ khác 'sự thật' dùng để chấm điểm."""
    w = simulate_world_des(seed, cell)
    common = twin_inputs(w, cell, curve, eps_ms)
    psa = dict(common, I_A=curve(w["A"]["G_true"]) - curve(w["B"]["G_true"]))
    des = dict(common, I_A=w["A"]["D_des"] - w["B"]["D_des"])
    return psa, des


def confirm_cell(cell):
    curve, s_ms = get_curve(cell)
    eps_ms, alpha = cell["eps_over_s"] * s_ms, cell["alpha"]
    cal = [decisions_paired(s, cell, curve, eps_ms) for s in CAL_SEEDS]
    test = [decisions_paired(s, cell, curve, eps_ms) for s in TEST_SEEDS]
    pick = lambda pairs, i: [p[i] for p in pairs]
    levels = {"A": (0, "expected"), "B": (0, "realized"), "C": (1, "realized")}
    out = {}
    for lv, (truth, tuning) in levels.items():
        r = evaluate_cell(pick(cal, truth), pick(test, truth), alpha, eps_ms, s_ms, tuning=tuning)
        r["confirmed"] = confirmed(r, alpha)
        out[lv] = r
    return out


def main():
    all_cells = {c["name"]: c for c in grid()}
    todo = [controls()[0]] + [all_cells[n] for n in CELLS]
    rows, t0 = [], time.time()
    print(f"{'ô':10s} {'bậc':3s} {'width (ms)':>16s} {'%head':>6s} {'%SC':>5s} {'harmK2/α':>8s} {'harmSC/α':>8s}  xác nhận")
    for c in todo:
        res = confirm_cell(c)
        for lv, r in res.items():
            sc = max(r["gain_SC"], 1e-9)
            print(f"{c['name']:10s} {lv:3s} {r['width_ms']:+8.3f}±{r['width_ci']:.3f} {r['width_pct']:6.1f} "
                  f"{100 * r['width_ms'] / sc:5.0f} {r['harm_K2'] / c['alpha']:8.2f} {r['harm_SC'] / c['alpha']:8.2f}  "
                  f"{'CÓ' if r['confirmed'] else '—'}")
            rows.append(dict(name=c["name"], level=lv, **c.get("axes", {}), **r))
        print(f"{'':10s} ({time.time() - t0:.0f} s)")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader()
        w.writerows(rows)
    print(f"\nĐã lưu {OUT}")
    for lv in "ABC":
        ok = [r["name"] for r in rows if r["level"] == lv and r["confirmed"] and r["name"] in CELLS]
        print(f"Bậc {lv}: {len(ok)}/{len(CELLS)} ứng viên đạt  {ok}")


if __name__ == "__main__":
    main()
