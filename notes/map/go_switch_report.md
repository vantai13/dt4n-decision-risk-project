# GO switch v1 — 2026-10-01

Code, thiết kế và dự đoán khóa ở commit 2693695 trước lần chạy v1. Đã kiểm 120 dòng, 2400 dòng per-seed, đủ tổ hợp; GO_SWITCH khớp mọi cờ, mọi policy calibration giữ cả hai ngân sách.

## Quyết định chính: trần trung bình 1 lần/30 s

| Kịch bản | α | Δ ròng ngoài mẫu [CI 95%], ms | Gain SC/K2 ms | Harm SC/K2 | Tỉ lệ hành động SC/K2 | Kết quả |
|---|---:|---|---|---|---|---|
| R1_dualISP | 0.2% | +0.077540 [+0.006660; +0.148421] | 0.753847/0.831387 | 0.1367%/0.1358% | 1.619%/1.946% | Đạt |
| R1_dualISP | 1% | +0.012526 [-0.048843; +0.073895] | 0.522414/0.534940 | 0.7692%/0.5050% | 2.222%/2.766% | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R2_bb_LTE | 0.2% | +0.112209 [+0.025978; +0.198440] | 0.053023/0.165232 | 0.1533%/0.1142% | 0.506%/2.941% | Đạt |
| R2_bb_LTE | 1% | +0.002981 [-0.016176; +0.022137] | 0.091881/0.094862 | 0.8225%/0.6508% | 2.872%/2.542% | CI chứa 0 hoặc âm; Δ <10% gain SC |

**R1_dualISP: GO** tại alpha=[0.002]

**R2_bb_LTE: GO** tại alpha=[0.002]

## So dự đoán và ý nghĩa quy mô

Dự đoán R1 NO-GO bị dữ liệu bác bỏ theo chính tiêu chí đã khóa: Δ/gain SC=10.2860%, cận dưới CI=0.006660 ms. Đây là GO sát ngưỡng tương đối 10%, không phải hiệu ứng thực tế lớn.
Ở alpha=0,2%, giới hạn 30 s làm width R1 từ 2.515126 xuống 0.077540 ms, giảm 96.92%. Do đó nhận định lợi thế giảm mạnh được hỗ trợ; nhận định biến mất hoàn toàn tại 30 s không đúng trong lần đánh giá này.
Số trong tài liệu người dùng là tối ưu trên test; lượt v1 là ngưỡng học calibration nên không đòi khớp các số đó. Dự đoán ô cùng nhịp và buffer nhỏ mất hiệu ứng cũng không đúng đồng loạt; xem bảng ô biên. Không thay tiêu chí sau khi thấy GO.
SESOI VoIP 8,1 ms không đạt ở kết quả chính. Toàn bộ suite kiểm: 98 passed in 5.64s.

## Ranh giới cost/tần suất R1 và R2

| Kịch bản | α | Thiết lập | Δ ròng [CI 95%], ms | μ K2 | Điều kiện thiếu |
|---|---:|---|---|---:|---|
| R1_dualISP | 0.2% | không giới hạn | +2.5151 [+1.9136; +3.1166] | 1 | Đạt |
| R1_dualISP | 0.2% | 1 lần/30 s | +0.0775 [+0.0067; +0.1484] | 22 | Đạt |
| R1_dualISP | 0.2% | 1 lần/60 s | +0.0113 [-0.0014; +0.0240] | 29 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_dualISP | 0.2% | 1 lần/120 s | +0.0129 [-0.0319; +0.0577] | 32 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_dualISP | 0.2% | chi phí 5 ms/lần | +1.3658 [+0.7587; +1.9729] | 3 | Đạt |
| R1_dualISP | 0.2% | chi phí 10 ms/lần | +1.0377 [+0.5746; +1.5007] | 10 | Đạt |
| R1_dualISP | 1% | không giới hạn | +0.3120 [+0.1241; +0.4999] | 0 | Đạt |
| R1_dualISP | 1% | 1 lần/30 s | +0.0125 [-0.0488; +0.0739] | 8 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_dualISP | 1% | 1 lần/60 s | +0.0124 [-0.0010; +0.0257] | 13 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_dualISP | 1% | 1 lần/120 s | +0.0021 [-0.0032; +0.0074] | 16 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_dualISP | 1% | chi phí 5 ms/lần | +0.0288 [-0.1017; +0.1593] | 4 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_dualISP | 1% | chi phí 10 ms/lần | -0.0127 [-0.0265; +0.0010] | 15 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R2_bb_LTE | 0.2% | không giới hạn | +0.1832 [+0.0949; +0.2715] | 1 | Đạt |
| R2_bb_LTE | 0.2% | 1 lần/30 s | +0.1122 [+0.0260; +0.1984] | 3 | Đạt |
| R2_bb_LTE | 0.2% | 1 lần/60 s | +0.0726 [+0.0050; +0.1402] | 5 | Đạt |
| R2_bb_LTE | 0.2% | 1 lần/120 s | +0.0017 [-0.0022; +0.0057] | 9 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R2_bb_LTE | 0.2% | chi phí 5 ms/lần | +0.0318 [-0.0374; +0.1009] | 5 | CI chứa 0 hoặc âm |
| R2_bb_LTE | 0.2% | chi phí 10 ms/lần | -0.0064 [-0.0161; +0.0033] | 10 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R2_bb_LTE | 1% | không giới hạn | +0.0422 [+0.0110; +0.0734] | 0 | Đạt |
| R2_bb_LTE | 1% | 1 lần/30 s | +0.0030 [-0.0162; +0.0221] | 3 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R2_bb_LTE | 1% | 1 lần/60 s | +0.0082 [+0.0039; +0.0124] | 5 | Đạt |
| R2_bb_LTE | 1% | 1 lần/120 s | +0.0149 [-0.0072; +0.0370] | 5 | CI chứa 0 hoặc âm |
| R2_bb_LTE | 1% | chi phí 5 ms/lần | +0.0073 [-0.0143; +0.0289] | 5 | CI chứa 0 hoặc âm |
| R2_bb_LTE | 1% | chi phí 10 ms/lần | -0.0009 [-0.0078; +0.0060] | 12 | CI chứa 0 hoặc âm; Δ <10% gain SC |

## Ô biên tại trần chính (không quyết định GO)

| Ô | α | Δ ngoài mẫu ms | CI dưới ms | Kết quả |
|---|---:|---:|---:|---|
| R1_TB1 | 0.2% | +0.057494 | +0.047699 | Đạt |
| R1_TB1 | 1% | +0.010247 | +0.000593 | Đạt |
| R1_TB10 | 0.2% | +0.032641 | +0.018942 | vượt trần harm test |
| R1_TB10 | 1% | -0.015230 | -0.027526 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_TB30 | 0.2% | +0.272921 | +0.164050 | Đạt |
| R1_TB30 | 1% | +0.021908 | -0.002110 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_TB300 | 0.2% | +0.193572 | -0.115069 | CI chứa 0 hoặc âm |
| R1_TB300 | 1% | -0.010831 | -0.173657 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_quietB | 0.2% | -0.005786 | -0.013268 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_quietB | 1% | -0.006001 | -0.011571 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_tau15 | 0.2% | +0.111087 | +0.033654 | Đạt |
| R1_tau15 | 1% | +0.004029 | -0.090290 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_buf50 | 0.2% | +0.142247 | +0.094814 | Đạt |
| R1_buf50 | 1% | -0.045333 | -0.077033 | CI chứa 0 hoặc âm; Δ <10% gain SC |
| R1_buf500 | 0.2% | +0.470497 | +0.196872 | Đạt |
| R1_buf500 | 1% | +0.065910 | -0.143832 | CI chứa 0 hoặc âm; Δ <10% gain SC |

## Phạm vi diễn giải

- Quyết định v0 GO vẫn đúng theo tiêu chí miễn phí đã khóa. V1 thêm điều kiện nên không sửa ngược số liệu v0. Không tự suy từ không đạt thống kê ra SC tối ưu tuyệt đối hay mọi ứng dụng đều NO-GO.
- Những sw trong bảng là tỉ lệ đề nghị đổi trên quỹ đạo S0 tham chiếu, không phải tần suất của quỹ đạo triển khai riêng từng luật. Nghịch đảo H/sw chỉ là khoảng cách trung bình tương đương. Code không áp cooldown từng lần, có thể chọn nhiều hành động liền nhau. Muốn kết luận về đổi đường liên tục thực tế cần rollout riêng và mô hình jitter/reordering.
- Dùng lại seed test 81001–81020 của v0 theo hướng dẫn; protocol v1 đã chịu ảnh hưởng bởi phân tích trên test. Tham số policy học riêng trên calibration nhưng đây không phải xác nhận độc lập trên test mới.
- Cost 5/10 ms là chi phí tuyến tính mỗi hành động trong gain ròng. Harm vẫn định nghĩa I<−1 ms trước cost; period và cost thử riêng, không đồng thời. Không khẳng định chi phí này là jitter thực tế đã đo.
- K2 chọn μ từ 0..80 ms và threshold ratio trên calibration, nhiều bậc tự do hơn SC. Không sửa lưới sau khi xem test; độ phủ/overfit của lưới vẫn là giới hạn.
- Với μ=0 và λ≈0, chính sách được ràng Ibar>0; với μ>0 ràng Ibar>μ. Quỹ đạo tham chiếu S0 vẫn tune harm như v0, không tune cost/cap; giữ cố định để so có cùng trạng thái tham chiếu.
- Chỉ twin đúng; chưa thêm 6 sai số v0. CI paired t trên 20 seed, không hiệu chỉnh nhiều phép kiểm. Các kịch bản vẫn có tham số giả định và telemetry bộ đếm gói.
- Claim “bất định chỉ có ích khi ba điều kiện cùng xảy ra” mạnh hơn dữ liệu: trước đây một số ô cùng nhịp vẫn đạt với hiệu ứng nhỏ. Báo cáo ranh giới trong các cấu hình đã thử, không khẳng định điều kiện cần toàn cục.

## Artifact và tái lập

- results/go_test/go_switch_v1.csv: đủ 120 kết quả, ngưỡng và kiểm ngân sách calibration.
- results/go_test/go_switch_seeds.csv: 2400 dòng per-seed.
- results/go_test/go_switch_manifest.json: kịch bản/seed/lưới/thiết lập khóa.
- results/go_test/go_switch_output.txt: log đầy đủ.
- results/go_test/go_switch_boundary.png/.pdf: đồ thị hiệu ứng ngoài mẫu.
- notes/map/go_switch_spec.md: dự đoán trước chạy.
- Chạy lại: .venv/bin/python -m experiments.scan.go_switch; dựng báo cáo: .venv/bin/python -m experiments.scan.report_go_switch.
