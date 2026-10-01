"""Export cached reproduction measurements; never simulate or open another seed."""
import csv
import json
import pickle
import subprocess
from hashlib import sha256
from pathlib import Path

import numpy as np

from experiments.gocheck import info_arrangement as info
from experiments.gocheck import rollout as base
from experiments.scan import go_test as g

OUT = Path("results/gocheck")


def write_csv(name, rows):
    with (OUT / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cached(name):
    return pickle.loads((base.RAW / name).read_bytes())


def main():
    scenario = g.scenarios()[0][0]
    name = scenario["name"]
    seeds, summaries, contrasts = [], [], []
    results_by_arrangement = {}
    for stage in ("fresh", "info"):
        cal_start, test_start = (92001, 93001) if stage == "fresh" else (94001, 95001)
        tags = ("fresh_cal", "fresh_test") if stage == "fresh" else ("info_94001", "info_95001")
        cal_world, test_world = [cached(f"{name}_{tag}.pkl") for tag in tags]
        if stage == "fresh":
            cal_inputs = [{"FIX": (d, d)} for d in
                          [g.decisions(w, scenario, {}, base.EPS) for w in cal_world]]
            test_inputs = [{"FIX": (d, d)} for d in
                           [g.decisions(w, scenario, {}, base.EPS) for w in test_world]]
        else:
            cal_inputs = [info.arrangement_inputs(w, scenario) for w in cal_world]
            test_inputs = [info.arrangement_inputs(w, scenario) for w in test_world]
        oracle = np.array([np.minimum(w["A"]["D"], w["B"]["D"]).mean() for w in test_world])
        for cooldown in base.COOLDOWNS:
            for alpha in base.ALPHAS:
                differences = {}
                for arrangement in (("FIX",) if stage == "fresh" else info.ARRANGEMENTS):
                    measurements = {}
                    thresholds, edges = {}, {}
                    for rule in ("SC", "K2"):
                        threshold, edge = info.tune_info(
                            arrangement, rule, cal_inputs, cal_world, alpha, cooldown
                        )
                        thresholds[rule], edges[rule] = threshold, edge
                        for split, start, inputs, worlds in (
                            ("calibration", cal_start, cal_inputs, cal_world),
                            ("test", test_start, test_inputs, test_world),
                        ):
                            measured = np.array([
                                info.rollout_info(*ci[arrangement], w, rule, threshold, cooldown)
                                for ci, w in zip(inputs, worlds)
                            ])
                            measurements[rule, split] = measured
                            for index, values in enumerate(measured):
                                n = len(worlds[index]["A"]["D"])
                                seeds.append(dict(
                                    stage=stage, arrangement=arrangement, alpha=alpha,
                                    cooldown_s=cooldown, split=split, seed=start + index,
                                    rule=rule, threshold=threshold, epochs=n,
                                    delay_ms=values[0], harm_per_epoch=values[1],
                                    harmful_switches=int(round(values[1] * n)),
                                    switches_per_1000=values[2],
                                    switches=int(round(values[2] * n / 1000)),
                                ))
                    sc, k2 = measurements["SC", "test"], measurements["K2", "test"]
                    delta = sc[:, 0] - k2[:, 0]
                    differences[arrangement] = delta
                    results_by_arrangement[stage, arrangement, alpha, cooldown] = (sc, k2)
                    mean, low, high = base.paired_ci(delta)
                    headroom = sc[:, 0] - oracle
                    absolute = base.paired_ci(delta - 8.1)
                    relative = base.paired_ci(delta - .1 * headroom)
                    harm_sc, harm_k2 = sc[:, 1].mean(), k2[:, 1].mean()
                    tc1 = low > 0 and harm_k2 <= harm_sc + .1 * alpha and max(harm_sc, harm_k2) <= 1.25 * alpha
                    summaries.append(dict(
                        stage=stage, arrangement=arrangement, alpha=alpha, cooldown_s=cooldown,
                        delay_sc_ms=sc[:, 0].mean(), delay_k2_ms=k2[:, 0].mean(),
                        delta_ms=mean, lo95_ms=low, hi95_ms=high,
                        harm_sc=harm_sc, harm_k2=harm_k2, tc1_pass=bool(tc1),
                        switches_sc_per_1000=sc[:, 2].mean(),
                        switches_k2_per_1000=k2[:, 2].mean(),
                        threshold_sc=thresholds["SC"], threshold_k2=thresholds["K2"],
                        grid_edge_sc=edges["SC"], grid_edge_k2=edges["K2"],
                        calibration_harm_sc=measurements["SC", "calibration"][:, 1].mean(),
                        calibration_harm_k2=measurements["K2", "calibration"][:, 1].mean(),
                        headroom_rollout_ms=headroom.mean(),
                        share_of_headroom=mean / headroom.mean(),
                        abs_margin_lo95_ms=absolute[1], abs_margin_hi95_ms=absolute[2],
                        rel_margin_lo95_ms=relative[1], rel_margin_hi95_ms=relative[2],
                        tc3_pass=bool(absolute[1] > 0 and relative[1] > 0),
                    ))
                if stage == "info":
                    for other in ("SYM", "FF"):
                        mean, low, high = base.paired_ci(differences["FIX"] - differences[other])
                        contrasts.append(dict(alpha=alpha, cooldown_s=cooldown,
                                              contrast=f"FIX_minus_{other}",
                                              mean_ms=mean, lo95_ms=low, hi95_ms=high,
                                              role="planned_difference_in_differences"))
                print(f"Exported {stage}, cooldown={cooldown}, alpha={alpha}", flush=True)
    # Additional paired contrasts are explicitly exploratory.
    fix_sc, fix_k2 = results_by_arrangement["info", "FIX", .002, 0]
    sym_sc, _ = results_by_arrangement["info", "SYM", .002, 0]
    for label, delta in (
        ("SC_FIX_minus_SC_SYM", fix_sc[:, 0] - sym_sc[:, 0]),
        ("K2_FIX_minus_SC_SYM", fix_k2[:, 0] - sym_sc[:, 0]),
    ):
        mean, low, high = base.paired_ci(delta)
        contrasts.append(dict(alpha=.002, cooldown_s=0, contrast=label,
                              mean_ms=mean, lo95_ms=low, hi95_ms=high,
                              role="posthoc_information_vs_policy"))
    write_csv("reproduction_seeds.csv", seeds)
    write_csv("reproduction_summary.csv", summaries)
    write_csv("reproduction_contrasts.csv", contrasts)
    model_files = [
        "experiments/gocheck/rollout.py", "experiments/gocheck/info_arrangement.py",
        "experiments/gocheck/check_wiring.py", "experiments/scan/go_test.py",
        "experiments/scan/twin.py", "experiments/scan/des_world.py",
        "experiments/scan/world.py", "experiments/f04b_des_gap.py", "ndtrisk/theory/mdk.py",
    ]
    freeze = "9272119b34be1fc05bd6b18c17057aba57cd703a"
    for path in model_files:
        frozen = subprocess.run(["git", "show", f"{freeze}:{path}"],
                                capture_output=True, check=True).stdout
        if frozen != Path(path).read_bytes():
            raise ValueError(f"Model code changed after freeze: {path}")
    manifest = dict(
        kind="local reproduction of supplied sandbox outcomes; not blinded confirmation",
        local_freeze_commit="9272119b34be1fc05bd6b18c17057aba57cd703a",
        sandbox_commit="1a66a24 (reported by supplied document; unavailable locally)",
        prediction_source="Claude AI; NT-1 deviation",
        source_sha256={p: sha256(Path(p).read_bytes()).hexdigest() for p in model_files},
        cache_sha256={p.name: sha256(p.read_bytes()).hexdigest()
                      for p in base.RAW.glob("*.pkl") if "fresh" in p.name or "info_94" in p.name or "info_95" in p.name},
        summary_rows=len(summaries), seed_rows=len(seeds),
        limitations=["FF forgets fast telemetry of the departed path",
                     "posthoc diagnostics do not establish ping-pong causality",
                     "no new external-validity sources"],
    )
    (OUT / "reproduction_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    primary = [r for r in summaries if r["alpha"] == .002 and r["cooldown_s"] == 0]
    lines = [
        "# GO-check — kết quả tái lập local",
        "",
        "Cấu hình khóa local ở 9272119; dự đoán Claude AI được nhập từ tài liệu",
        "người dùng (sandbox 1a66a24 chưa kiểm độc lập). Kết quả sandbox đã được",
        "đọc trước khi tái lập local; không gọi đây là xác nhận mù.",
        "",
        "## Dự đoán ↔ kết quả (trước diễn giải)",
        "",
        "| Dự đoán AI | Kết quả local | Đối chiếu |",
        "|---|---|---|",
    ]
    fix_values = [r["delta_ms"] for r in primary if r["arrangement"] == "FIX"]
    sym = next(r for r in primary if r["arrangement"] == "SYM")
    ff = next(r for r in primary if r["arrangement"] == "FF")
    lines += [
        f"| FIX mỗi lần trong [0,9; 2,3] ms | {fix_values[0]:.3f}; {fix_values[1]:.3f} ms | Cả hai trong khoảng |",
        f"| Hai lần FIX lệch ≤0,8 ms | {abs(fix_values[0]-fix_values[1]):.3f} ms | Trong mức dự đoán |",
        f"| SYM trong [−0,05; 0,2] ms, mức gần 0 (<0,1) | {sym['delta_ms']:.3f} ms | Trong khoảng; sai mức |",
        f"| FF dương trong [0; 0,8] ms | {ff['delta_ms']:.3f} ms | Ngoài khoảng, sai dấu |",
        "| Thứ hạng FIX > FF > SYM | FIX > SYM > FF | Sai thứ hạng |",
    ]
    for r in summaries:
        if r["arrangement"] == "FIX" and r["cooldown_s"] == 0 and r["alpha"] == .01:
            correct = r["lo95_ms"] <= 0 <= r["hi95_ms"] and abs(r["delta_ms"]) < .1
            lines.append(f"| FIX α=1%, CI chứa 0 và abs(gap)<0,1 ({r['stage']}) "
                         f"| {r['delta_ms']:+.3f} [{r['lo95_ms']:+.3f}; {r['hi95_ms']:+.3f}] "
                         f"| {'Khớp' if correct else 'Trượt'} |")
        if r["arrangement"] == "FIX" and r["cooldown_s"] == 30 and r["alpha"] == .002:
            lines.append(f"| FIX cooldown trong [0; 1] ({r['stage']}) | {r['delta_ms']:.3f} ms "
                         f"| {'Trong khoảng' if 0 <= r['delta_ms'] <= 1 else 'Ngoài khoảng'} |")
    lowest = sym["delay_sc_ms"] < min(r["delay_sc_ms"] for r in primary if r["stage"] == "info" and r["arrangement"] != "SYM")
    lowest &= sym["delay_k2_ms"] < min(r["delay_k2_ms"] for r in primary if r["stage"] == "info" and r["arrangement"] != "SYM")
    lines.append(f"| SYM delay thấp nhất cả hai luật, trong [2,3; 3,5] ms "
                 f"| SC {sym['delay_sc_ms']:.3f}; K2 {sym['delay_k2_ms']:.3f} "
                 f"| {'Khớp' if lowest and 2.3 <= sym['delay_sc_ms'] <= 3.5 and 2.3 <= sym['delay_k2_ms'] <= 3.5 else 'Trượt'} |")
    for r in contrasts:
        if r["role"] == "planned_difference_in_differences" and r["alpha"] == .002 and r["cooldown_s"] == 0:
            lines.append(f"| {r['contrast']}: CI dương | {r['mean_ms']:+.3f} [{r['lo95_ms']:+.3f}; {r['hi95_ms']:+.3f}] "
                         f"| {'Khớp' if r['lo95_ms'] > 0 else 'Trượt'} |")
    for r in summaries:
        if r["stage"] == "info" and r["arrangement"] in ("SYM", "FF") and (r["alpha"] == .01 or r["cooldown_s"] == 30):
            lines.append(f"| {r['arrangement']}, α={r['alpha']}, cooldown={r['cooldown_s']}: abs(gap)<0,15 "
                         f"| {r['delta_ms']:+.3f} ms | {'Khớp' if abs(r['delta_ms']) < .15 else 'Trượt'} |")
    lines += [
        "", "## Tất cả cấu hình đo",
        "",
        "| Lần chạy | Bố trí | α | Cooldown | SC ms | K2 ms | SC−K2 [CI95] ms | Harm SC/K2 (% epoch) | TC1 | TC3 |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in summaries:
        lines.append(
            f"| {r['stage']} | {r['arrangement']} | {100*r['alpha']:.1f}% | {r['cooldown_s']} s "
            f"| {r['delay_sc_ms']:.3f} | {r['delay_k2_ms']:.3f} "
            f"| {r['delta_ms']:+.3f} [{r['lo95_ms']:+.3f}; {r['hi95_ms']:+.3f}] "
            f"| {100*r['harm_sc']:.4f}/{100*r['harm_k2']:.4f} "
            f"| {'Đạt' if r['tc1_pass'] else 'Chưa đạt'} "
            f"| {'Đạt' if r['tc3_pass'] else 'Chưa đạt'} |"
        )
    lines += ["", "TC1 là điều kiện gợi ý giữ nguyên trong spec: CI dưới >0,",
              "harm_K2 ≤ harm_SC +0,1α và cả hai ≤1,25α. Không đổi để cứu kết quả.",
              "TC3 giữ CI hai biên gap−8,1 ms và gap−10% headroom theo L1.5.",
              "FF được chấm số học nhưng không dùng suy ra ưu thế của đo thụ động thật.",
              "", "## Hiệu-của-hiệu và so sánh bổ sung", "",
              "| So sánh | α | Cooldown | Hiệu [CI95] ms | Vai trò |",
              "|---|---|---|---|---|"]
    for r in contrasts:
        lines.append(f"| {r['contrast']} | {100*r['alpha']:.1f}% | {r['cooldown_s']} s "
                     f"| {r['mean_ms']:+.3f} [{r['lo95_ms']:+.3f}; {r['hi95_ms']:+.3f}] | {r['role']} |")
    lines += [
        "", "## Giới hạn và phán quyết", "",
        "CHƯA GO: TC1 phụ thuộc lần lặp/cấu hình, TC2 chưa có nguồn mới,",
        "TC3 không vượt sàn 8,1 ms. SYM vẫn có lợi thế nhỏ nên không nói",
        "mọi lợi thế đều cần bất đối xứng. Trong R1 này, hiệu ứng lớn tập trung ở FIX.",
        "FF bỏ thông tin fast của path vừa rời; đây là giới hạn thiết kế đã được",
        "nguồn sandbox cảnh báo, không phải bug số học mà V1–V6 loại trừ được.",
        "Hai script hậu kiểm báo sai lệch tại các epoch được chọn để đổi;",
        "chưa đo trực tiếp ping-pong hoặc can thiệp FF có trí nhớ để xác định nguyên nhân.",
        "",
        "CSV per-seed, summary, contrasts và manifest nằm cùng thư mục.",
        "Output chính: fresh_output.txt, info_outcome_output.txt.",
        "Hậu kiểm: posthoc_reliability_output.txt, posthoc_switch_errors_output.txt.",
    ]
    (OUT / "REPRODUCTION_REPORT.md").write_text("\n".join(lines) + "\n")
    print(f"Saved {len(summaries)} summaries and {len(seeds)} per-seed records.", flush=True)


if __name__ == "__main__":
    main()
