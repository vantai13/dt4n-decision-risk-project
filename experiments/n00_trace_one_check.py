"""n00 — Lần theo MỘT lần kiểm qua twin cũ (chỉ đọc code cũ, không thêm logic mới).

Mục đích (L1.1): nhìn tận mắt 4 đối tượng khác nhau — dự báo, phán quyết, hành động, kết quả —
trên cùng một quyết định, và thấy mẫu số đổi thì tỉ lệ đổi.
Đơn giản hoá CHỈ để minh hoạ: luôn coi đường hiện tại là A (không chạy quỹ đạo S0);
bộ sinh đề xuất = "số đo thô nói B tốt hơn" (Iplug > 0); phán quyết = "duyệt nếu Ī > 0".
Ô: POS_probeB (grid.controls). Seed 9101 thuộc dải pilot 9000–9999 → không chạm seed test.
"""
import csv
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import scipy

from experiments.scan.cell import get_curve, twin_inputs
from experiments.scan.grid import controls
from experiments.scan.world import simulate_world
from experiments.scan.twin import GH_W, GH_X, posterior
from experiments.scan.world import PKT_BITS

started = time.perf_counter()
SEED = 9101
_, cell = controls()                                   # ô đối chứng dương POS_probeB
curve, s_ms = get_curve(cell)                          # đường cong delay M/D/1/K của twin
eps = cell["eps_over_s"] * s_ms                        # vùng thờ ơ ε = 0,5·S (ms)

w = simulate_world(SEED, cell)                         # "mạng thật": tải OU + telemetry cũ/nhiễu
tw = twin_inputs(w, cell, curve, eps)                  # twin: Iplug (ngây thơ), Ibar, p_dn
I = curve(w["A"]["G_true"]) - curve(w["B"]["G_true"])  # kết quả thật trên khoảng giữ (sự thật PSA)

proposal = tw["Iplug_A"] > 0                           # ai đó ĐỀ XUẤT chuyển A → B
approve = proposal & (tw["Ibar_A"] > 0)                # twin DUYỆT
harm, good = I < -eps, I > eps

for k in (99, 23):
    print(f"--- epoch {k}")
    for p in "AB":
        print(f"  {p}: rho_hat={w[p]['rhohat'][k]:.3f}  tuổi={w[p]['age'][k]:5.2f} s"
              f"  |  tải thật khoảng giữ={w[p]['G_true'][k]:.3f}")
    print(f"  DỰ BÁO   : Iplug={tw['Iplug_A'][k]:+.2f} ms   Ibar={tw['Ibar_A'][k]:+.2f} ms   p_dn={tw['pdn_A'][k]:.3f}")
    print(f"  PHÁN QUYẾT: {'DUYỆT' if approve[k] else 'TỪ CHỐI'}  (đề xuất: {bool(proposal[k])})")
    print(f"  KẾT QUẢ  : I={I[k]:+.2f} ms  ->  {'có lợi' if good[k] else 'có hại' if harm[k] else 'thờ ơ'}")

n_bad = int((approve & harm).sum())                   # cùng MỘT tử số...
print(f"\nSố lần 'duyệt mà hại' = {n_bad}; chia cho các mẫu số khác nhau:")
for name, m in [("mọi epoch", np.ones_like(I, bool)), ("mọi đề xuất", proposal),
                ("mọi lần duyệt", approve), ("mọi đề xuất có hại", proposal & harm)]:
    print(f"  / {name:20s} ({int(m.sum()):4d}) = {n_bad / m.sum():6.1%}")

# Bổ sung của Codex: xuất dữ liệu và kiểm các số lesson đã công bố.
# Không đổi seed, mô hình, bộ sinh đề xuất hay luật duyệt ở trên.
outdir = Path(__file__).resolve().parent / "results"
outdir.mkdir(parents=True, exist_ok=True)
details = {}
for p in "AB":
    path, obs = cell[p], w[p]
    R = path["rho_bar"] * (PKT_BITS / (cell["mbps"] * 1e6)) / path["T_tel"]
    mean, var = posterior(obs["rhohat"], obs["age"] + cell["a"], path["T_tel"],
                          cell["H"], path["rho_bar"], path["sigma"], path["tau"], R)
    expected = curve(mean[:, None] + np.sqrt(2 * var)[:, None] * GH_X) @ GH_W
    details[p] = dict(mean=mean, sd=np.sqrt(var), expected=expected,
                      plug=curve(obs["rhohat"]), truth=curve(obs["G_true"]))

csv_path = outdir / "n00_trace_one_check_epochs.csv"
fields = ["epoch", "proposal", "approve", "action", "Iplug_ms", "Ibar_ms", "p_dn", "I_true_ms", "label"]
fields += [f"{p}_{key}" for p in "AB" for key in
           ("rhohat", "age_s", "rho_true", "post_mean", "post_sd", "plug_ms", "expected_ms", "true_ms")]
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for k in range(len(I)):
        row = dict(epoch=k, proposal=bool(proposal[k]), approve=bool(approve[k]),
                   action="switch_B" if approve[k] else "stay_A",
                   Iplug_ms=tw["Iplug_A"][k], Ibar_ms=tw["Ibar_A"][k], p_dn=tw["pdn_A"][k],
                   I_true_ms=I[k], label="good" if good[k] else "harm" if harm[k] else "indifferent")
        for p in "AB":
            vals = [w[p]["rhohat"][k], w[p]["age"][k], w[p]["G_true"][k]]
            vals += [details[p][key][k] for key in ("mean", "sd", "plug", "expected", "truth")]
            row.update(zip([f"{p}_{key}" for key in
                            ("rhohat", "age_s", "rho_true", "post_mean", "post_sd", "plug_ms", "expected_ms", "true_ms")], vals))
        writer.writerow(row)

counts = [len(I), int(proposal.sum()), int(approve.sum()), int((proposal & harm).sum())]
checks = {
    "tử số và bốn mẫu số khớp lesson": n_bad == 292 and counts == [4000, 2552, 2012, 510],
    "epoch 99 khớp số làm tròn của lesson": bool(proposal[99] and not approve[99] and good[99])
        and bool(np.allclose([tw["Iplug_A"][99], tw["Ibar_A"][99], I[99]], [0.51, -13.58, 1.37], atol=0.01, rtol=0)),
    "epoch 23 khớp số làm tròn của lesson": bool(proposal[23] and approve[23] and good[23])
        and bool(np.allclose([tw["Ibar_A"][23], I[23]], [6.53, 70.6], atol=0.05, rtol=0)),
    "kỳ vọng từng đường khớp twin_inputs": bool(np.allclose(
        details["A"]["expected"] - details["B"]["expected"], tw["Ibar_A"], atol=1e-12, rtol=0)),
    "đầu ra hữu hạn": bool(np.isfinite(np.concatenate([I, *tw.values()])).all()),
}
print("\nChi tiết epoch 99 (ms, trừ tải và tuổi):")
for p in "AB":
    d = details[p]
    print(f"  {p}: hậu nghiệm={d['mean'][99]:.6f} ± {d['sd'][99]:.6f}; "
          f"T(ρ̂)={d['plug'][99]:.6f}; E[T]={d['expected'][99]:.6f}; T thật={d['truth'][99]:.6f}")
static = {rho: float(curve(rho)) for rho in (0.85, 0.95, 1.0)}
increments = {rho: float(curve(rho + 0.0064) - curve(rho)) for rho in (0.85, 0.95)}
print("\nPhép tính đường cong dừng — KHÔNG phải mô phỏng can thiệp:")
for rho, delay in static.items():
    print(f"  T({rho:.2f}) = {delay:.6f} ms")
for rho, delta in increments.items():
    print(f"  Δρ=0.0064 tại ρ={rho:.2f}: tăng {delta:.6f} ms; ε={eps:.6f} ms")
for name, passed in checks.items():
    print(f"  {'ĐẠT' if passed else 'TRƯỢT'}: {name}")

base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=outdir, text=True).strip()
elapsed = time.perf_counter() - started
report = ["# n00 — Kết quả tái lập L1.1 (2026-10-02)", "",
          f"Base commit: `{base}`; Python {platform.python_version()}, NumPy {np.__version__}, SciPy {scipy.__version__}.", "",
          f"Ô **{cell['name']}**, seed **{SEED}** (pilot), **{len(I)} epoch**; ε={eps:.6f} ms; thời gian tính/xuất ≈ {elapsed:.3f} s.", "",
          "Lệnh: `.venv/bin/python -m experiments.n00_trace_one_check | tee experiments/results/n00_trace_one_check_output.txt`.", "",
          "Luôn ở A; đề xuất nếu Iplug > 0; duyệt nếu có đề xuất và Ibar > 0. Nhãn theo sự thật PSA.",
          "Đây là minh hoạ một seed đã thấy kết quả trong lesson, không phải thí nghiệm mù, DES hay rollout; không áp ngân sách harm.", "",
          "| Epoch (đánh số từ 0) | Iplug (ms) | Ibar (ms) | I thật (ms) | Phán quyết / hành động | Đánh giá theo kết quả thực hiện |",
          "|---|---:|---:|---:|---|---|"]
for k in (99, 23):
    report.append(f"| {k} | {tw['Iplug_A'][k]:+.6f} | {tw['Ibar_A'][k]:+.6f} | {I[k]:+.6f} | "
                  f"{'Duyệt / chuyển B' if approve[k] else 'Từ chối / giữ A'} | "
                  f"{'Duyệt đúng' if approve[k] and good[k] else 'Từ chối nhầm'} |")
report += ["", "Sai số dự báo lớn không đồng nghĩa phán quyết sai: epoch 23 vẫn duyệt đúng.", "",
           "| Mẫu số | Số lượng | Duyệt mà hại / mẫu số |", "|---|---:|---:|"]
for name, denominator in zip(("Mọi epoch", "Mọi đề xuất", "Mọi lần duyệt", "Mọi đề xuất có hại"), counts):
    report.append(f"| {name} | {denominator} | {n_bad}/{denominator} = {100*n_bad/denominator:.4f}% |")
report += ["", "Hàng cuối là tỷ lệ **bỏ lọt** đề xuất có hại, không phải tỷ lệ bắt được hại.", "",
           "Phép tính đường cong dừng (không phải can thiệp DES):", ""]
for rho, delta in increments.items():
    report.append(f"- Δρ=0,0064 tại ρ={rho}: delay tăng {delta:.6f} ms (ε={eps:.6f} ms).")
report += [f"- Ví dụ nhóm Δρ=0,1: lợi ích thật tĩnh T(0,95)−T(0,95)=0; bỏ qua tải nhóm tạo lợi ích ảo {static[0.95]-static[0.85]:.6f} ms.",
           "", "Kiểm đối chiếu số lesson (không phải bằng chứng độc lập về mô hình):", ""]
report += [f"- {'ĐẠT' if passed else 'TRƯỢT'} — {name}." for name, passed in checks.items()]
report += ["", "Các tệp kết quả:", "",
           "- [Output console](n00_trace_one_check_output.txt).",
           "- [CSV 4.000 epoch](n00_trace_one_check_epochs.csv): dự báo, phán quyết, hành động minh hoạ, kết quả, telemetry và hậu nghiệm từng đường.",
           "- [Question card N0](../../notes/novelty/N0_question_card.md).", "",
           "Nguồn script lõi: lesson do người dùng cung cấp (ghi Claude). Codex bổ sung xuất dữ liệu, kiểm đối chiếu và báo cáo; chưa xác nhận tác giả tự kiểm bài.",
           "Không thay hàm nền tảng; posterior Gauss và đường cong nội suy vẫn có xấp xỉ. Hai nhánh can thiệp Δρ>0 chưa triển khai."]
(outdir / "n00_report.md").write_text("\n".join(report) + "\n")
print(f"\nĐã lưu {csv_path.relative_to(outdir.parent.parent)} và experiments/results/n00_report.md")
print(f"Thời gian tính/xuất: {elapsed:.3f} s")
if not all(checks.values()):
    raise SystemExit("Có số liệu không khớp lesson; xem báo cáo trước khi kết luận tái lập.")
