"""Quét bản đồ v0. Chạy: python -m experiments.scan.run_scan"""
import csv
import time
from pathlib import Path

from experiments.scan.cell import run_cell
from experiments.scan.grid import AXES, controls, grid

CAL_SEEDS, TEST_SEEDS = range(60001, 60011), range(61001, 61011)
CTRL_CAL, CTRL_TEST = range(62001, 62021), range(63001, 63021)
OUT = Path("results/scan/map_v0.csv")

MIN_WIDTH_PCT_HEADROOM = 2.0
MIN_WIDTH_PCT_OF_SC = 20.0
MIN_FLOWS = 10


def is_candidate(cell, r):
    return bool(r["width_ms"] - r["width_ci"] > 0
                and r["width_pct"] >= MIN_WIDTH_PCT_HEADROOM
                and r["width_ms"] >= MIN_WIDTH_PCT_OF_SC / 100 * max(r["gain_SC"], 1e-9)
                and cell["n_flows_min"] >= MIN_FLOWS)


def check_controls():
    neg, pos = controls()
    rn, rp = run_cell(neg, CTRL_CAL, CTRL_TEST), run_cell(pos, CTRL_CAL, CTRL_TEST)
    ok_neg = abs(rn["width_pct"]) < 1.0 and not is_candidate(neg, rn)
    ok_pos = rp["width_ms"] - rp["width_ci"] > 0
    for tag, r, ok in (("ÂM  (góc P2 cũ)", rn, ok_neg), ("DƯƠNG (B probe thưa)", rp, ok_pos)):
        print(f"Đối chứng {tag:22s}: width {r['width_ms']:+.3f} ± {r['width_ci']:.3f} ms "
              f"({r['width_pct']:+.2f}% headroom; SC {r['gain_SC']:.2f} → K2 {r['gain_K2']:.2f}) | harm SC {r['harm_SC']:.4f} K2 {r['harm_K2']:.4f} → {'ĐẠT' if ok else 'HỎNG'}")
    return ok_neg and ok_pos


def report(rows):
    cands = sorted([r for r in rows if r["candidate"]], key=lambda r: -r["width_pct"])
    print(f"\n{len(cands)}/{len(rows)} ô đạt tiêu chí ứng viên.")
    for r in cands[:15]:
        print(f"  {r['name']} {', '.join(f'{k}={r[k]}' for k in AXES)} | width {r['width_ms']:+.3f}±{r['width_ci']:.3f} ms "
              f"({r['width_pct']:.1f}% headroom; SC {r['gain_SC']:.2f} → K2 {r['gain_K2']:.2f})")
    print("\nTrục nào quan trọng? (trung bình width % headroom | số ô ứng viên) theo từng mức:")
    for ax, levels in AXES.items():
        cells = []
        for lv in levels:
            sub = [r for r in rows if r[ax] == lv]
            cells.append(f"{lv}: {sum(r['width_pct'] for r in sub) / len(sub):+.2f}% | {sum(r['candidate'] for r in sub)}")
        print(f"  {ax:8s} " + "   ".join(cells))
    print("\nKẾT LUẬN THEO TIÊU CHÍ ĐÃ KHÓA: " + (
        "PIVOT trong mô hình này — không ô nào đạt." if not cands else
        "Có ứng viên → bước tiếp: kiểm TÍNH THỰC TẾ của các ô này (có nguồn không?) rồi xác nhận bằng DES."))


def main():
    if not check_controls():
        print("Đối chứng hỏng → KHÔNG tin bản đồ. Dừng lại, tìm lỗi trước.")
        return
    cells, rows, t0 = list(grid()), [], time.time()
    for i, c in enumerate(cells, 1):
        r = run_cell(c, CAL_SEEDS, TEST_SEEDS)
        rows.append(dict(name=c["name"], **c["axes"], n_flows_min=round(c["n_flows_min"]),
                         candidate=is_candidate(c, r), **r))
        print(f"\r  đã chạy {i}/{len(cells)} ô ({time.time() - t0:.0f} s)", end="", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nĐã lưu {OUT}")
    report(rows)


if __name__ == "__main__":
    main()
