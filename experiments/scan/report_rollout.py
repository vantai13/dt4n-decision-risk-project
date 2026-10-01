"""Tổng hợp CSV v2–v4; không tune hay sinh thêm seed.

Chạy sau ba rollout: python -m experiments.scan.report_rollout.
"""
import csv
import json
import platform
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

import numba
import numpy as np
import scipy

from experiments.scan.rollout_v2 import ci

OUT = Path("results/go_test")
KEYS = ("stage", "world", "alpha", "hold_down_s", "twin_horizon_s")
# Số đã công bố trong attachment, không phải dự đoán tiền đăng ký.
EXPECTED_V4 = {
    ("R1_dualISP", "S0dir"): (-.19, -.67, .29),
    ("R1_dualISP", "SCtab"): (-.14, -.58, .30),
    ("R1_dualISP", "SCtab24"): (-.22, -.67, .23),
    ("R3_outage", "S0dir"): (1.06, .72, 1.40),
    ("R3_outage", "SCtab"): (.60, .27, .93),
    ("R3_outage", "SCtab24"): (.12, -.07, .31),
    ("R3_outageB", "S0dir"): (.60, .37, .83),
    ("R3_outageB", "SCtab"): (.34, .17, .50),
    ("R3_outageB", "SCtab24"): (.15, -.09, .38),
}


def save_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    grouped = defaultdict(lambda: defaultdict(dict))
    n_rows = 0
    for stage in ("rollout_v2", "rollout_v3", "rollout_v4"):
        with (OUT / f"{stage}_seeds.csv").open() as f:
            for row in csv.DictReader(f):
                key = tuple(row[k] for k in KEYS)
                slot = (row["split"], row["rule"])
                seed = int(row["seed"])
                if seed in grouped[key][slot]:
                    raise ValueError(f"Duplicate seed: {key}, {slot}, {seed}")
                grouped[key][slot][seed] = row
                n_rows += 1

    summaries, comparisons = [], []
    for key, results in grouped.items():
        info = dict(zip(KEYS, key))
        rules = [r for split, r in results if split == "test"]
        cal_scores = {}
        for rule in rules:
            cal = results[("calibration", rule)]
            if len(cal) != 20:
                raise ValueError(f"Incomplete calibration: {key}, {rule}")
            cal_harm = np.mean([float(x["harm_per_epoch"]) for x in cal.values()])
            if rule != "K2":
                cal_scores[rule] = (np.mean([float(x["delay_ms"]) for x in cal.values()])
                                    if cal_harm <= float(info["alpha"]) else np.inf)
            for split in ("calibration", "test"):
                rows = results[(split, rule)]
                if len(rows) != 20:
                    raise ValueError(f"Incomplete split: {key}, {split}, {rule}")
                vals = np.array([[float(x[c]) for c in
                                 ("delay_ms", "harm_per_epoch", "switches_per_epoch")]
                                 for _, x in sorted(rows.items())])
                if not np.isfinite(vals).all():
                    raise ValueError(f"Nonfinite measurements: {key}, {rule}")
                summaries.append({**info, "rule": rule, "split": split,
                                  "n_seeds": len(rows), "delay_ms": vals[:, 0].mean(),
                                  "harm_per_epoch": vals[:, 1].mean(),
                                  "switches_per_min": 60 * vals[:, 2].mean(),
                                  "harm_within_alpha": bool(vals[:, 1].mean() <= float(info["alpha"]))})
        best = min(cal_scores, key=cal_scores.get)
        k2 = results[("test", "K2")]
        for baseline in rules:
            if baseline == "K2":
                continue
            base = results[("test", baseline)]
            if base.keys() != k2.keys():
                raise ValueError("Cannot pair different seeds")
            seeds = sorted(base)
            b = np.array([float(base[s]["delay_ms"]) for s in seeds])
            k = np.array([float(k2[s]["delay_ms"]) for s in seeds])
            m, lo, hi = ci(b - k)
            expected = EXPECTED_V4.get((info["world"], baseline)) if info["stage"] == "rollout_v4" else None
            comparisons.append({**info, "baseline": baseline, "n_seeds": len(seeds),
                                "baseline_delay_ms": b.mean(), "k2_delay_ms": k.mean(),
                                "delta_ms": m, "lo95_ms": lo, "hi95_ms": hi,
                                "improvement_pct": 100 * m / b.mean(),
                                "best_baseline_on_cal": baseline == best,
                                "max_attachment_difference_ms": (float(np.max(np.abs(np.array((m, lo, hi)) - expected)))
                                                                 if expected else ""),
                                "matches_attachment_rounding": (bool(np.max(np.abs(np.array((m, lo, hi)) - expected)) <= .005 + 1e-12)
                                                                if expected else "")})

    save_csv(OUT / "rollout_summary.csv", summaries)
    save_csv(OUT / "rollout_comparisons.csv", comparisons)
    final = [x for x in comparisons if x["stage"] == "rollout_v4" and x["baseline"] in ("S0dir", "SCtab", "SCtab24")]
    match = all(x["matches_attachment_rounding"] for x in final)
    lines = ["# Closed-loop v2–v4: tái lập POST HOC", "",
             f"{n_rows:,} dòng seed; {len(grouped)} cấu hình; 20 seed calibration + 20 seed test mỗi cấu hình.",
             f"Bảng v4 khớp số làm tròn trong attachment: {sum(x['matches_attachment_rounding'] for x in final)}/9.", "",
             "Dương = delay baseline − delay K2 > 0, nghĩa là K2 tốt hơn. CI t ghép cặp 95% qua seed.", "",
             "| Thế giới | Baseline | Δ ms [CI 95%] | Giảm delay |",
             "|---|---|---:|---:|"]
    for x in final:
        lines.append(f"| {x['world']} | {x['baseline']} | {x['delta_ms']:+.3f} [{x['lo95_ms']:+.3f}; {x['hi95_ms']:+.3f}] | {x['improvement_pct']:+.2f}% |")
    mismatches = [x for x in final if not x["matches_attachment_rounding"]]
    if mismatches:
        lines.extend(["", "Đối chiếu attachment: chênh lệch trung bình của cả 9 dòng khớp ở độ chính xác 0,01 ms."])
        for x in mismatches:
            ex = EXPECTED_V4[x['world'], x['baseline']]
            lines.append(f"Riêng {x['world']}/{x['baseline']}: CI thực [{x['lo95_ms']:.6f}; {x['hi95_ms']:.6f}] "
                         f"so với [{ex[1]:.2f}; {ex[2]:.2f}] trong attachment; sai khác tối đa "
                         f"{x['max_attachment_difference_ms']:.6f} ms. Không thay dấu hay kết luận CI loại 0.")
    lines.extend(["", "## Calibration → test (v4)", "",
                  "| Thế giới | Luật | Calibration ms | Test ms | Harm cal/test (% epoch) |",
                  "|---|---|---:|---:|---:|"])
    lookup = {(x['world'], x['rule'], x['split']): x for x in summaries if x['stage'] == 'rollout_v4'}
    for world in ("R1_dualISP", "R3_outage", "R3_outageB"):
        for rule in ("SCtab", "SCtab24", "K2"):
            a, b = lookup[world, rule, 'calibration'], lookup[world, rule, 'test']
            lines.append(f"| {world} | {rule} | {a['delay_ms']:.3f} | {b['delay_ms']:.3f} | {100*a['harm_per_epoch']:.4f}/{100*b['harm_per_epoch']:.4f} |")
    lines.extend(["", "## Đọc kết quả", "",
                  "- R1: không chứng minh K2 hơn baseline theo chiều/tuổi/tải khi horizon khớp hold-down.",
                  "- R3/R3B: so bảng 8 ngưỡng, CI lợi thế K2 loại 0; so bảng 24, CI chứa 0.",
                  "  Chưa chứng minh hơn hoặc tương đương bảng 24; chưa kiểm hiệu quả dữ liệu hay dịch chế độ.",
                  "- Gap calibration/test chỉ là dấu hiệu mô tả; không tự chứng minh overfit.",
                  "- Cả ba dải seed đã được Claude chạy trước trong sandbox; R3 được thiết kế sau kết quả R1.",
                  "  Các CI mang tính khám phá, không hiệu chỉnh đa so sánh; không phải xác nhận độc lập.",
                  "- Mục tiêu mới không thay thế phán quyết và SESOI VoIP đã đăng ký.", "",
                  "## Công thức / giới hạn", "",
                  "Delay luật = (1/N) Σ D_{đường luật chọn sau hành động}(t).",
                  "Harm = số lần đổi có D_hiện_tại − D_đích < −1 ms / N epoch.",
                  "K2 đổi khi Ī > μ và (Ī − μ)/p₋ > θ, nếu hết hold-down.",
                  "v4 tách nhịp quyết định 1 s khỏi hold-down và horizon twin 30 s.",
                  "Nhãn delay vẫn là trung bình probe từng giây, không phải delay từng gói của ứng dụng thực.",
                  "Tải nền/hàng đợi được sinh trước, không đổi theo luật; không mô hình chi phí chuyển đường.",
                  "Harm đo theo nhãn một giây, KHÔNG phải harm tích lũy suốt 30 s cam kết.",
                  "SCtab24 tune không ràng buộc harm theo code nguồn; số harm hậu nghiệm được báo trong CSV.",
                  "Coordinate descent là heuristic, không bảo đảm tìm cực tiểu toàn cục cho bảng 8/24.", "",
                  "## Tệp", "",
                  "- `rollout_v{2,3,4}_output.txt`: log đầy đủ.",
                  "- `rollout_v{2,3,4}_seeds.csv`: từng seed, cả hai split, μ và ngưỡng đã tune.",
                  "- `rollout_summary.csv`: delay, harm, tần suất chuyển theo cấu hình/luật/split.",
                  "- `rollout_comparisons.csv`: chênh lệch và CI của mọi baseline, đánh dấu baseline chọn trên calibration.",
                  "- `rollout_manifest.json`: seed, môi trường, provenance."])
    (OUT / "rollout_reproduction_report.md").write_text("\n".join(lines) + "\n")
    manifest = dict(base_commit="7c60c76", classification="POST HOC reproduction",
                    calibration_seeds=[86001, 86020], test_v2_v3_seeds=[87001, 87020],
                    test_v4_seeds=[89001, 89020], all_seeds_previously_used_in_claude_sandbox=True,
                    r3_designed_after_r1_results=True, v4_matches_attachment_rounding=match,
                    seed_rows=n_rows, settings=len(grouped), python=platform.python_version(),
                    numpy=np.__version__, scipy=scipy.__version__, numba=numba.__version__,
                    ci="paired seed-level t 95%, unadjusted exploratory comparisons",
                    sc_tab24_tuning="delay-only coordinate descent; harm audited, not constrained",
                    sha256={str(p): sha256(p.read_bytes()).hexdigest()
                            for p in [*(Path(f"experiments/scan/rollout_v{i}.py") for i in (2, 3, 4)),
                                      *(OUT / f"rollout_v{i}_{suffix}" for i in (2, 3, 4)
                                        for suffix in ("output.txt", "seeds.csv"))]},
                    changes_to_supplied_code=["correct used-seed labels", "export seed-level calibration/test CSV",
                                              "audit SCtab24 harm", "print K2 calibration",
                                              "v4 world selection/append for interrupted run"],
                    run_interruption="v4 completed R1 and R3, then resumed R3B with --world R3_outageB --append")
    (OUT / "rollout_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print("\n".join(lines[:17]))
    print(f"\nSaved report, summary, comparisons, manifest to {OUT}")


if __name__ == "__main__":
    main()
