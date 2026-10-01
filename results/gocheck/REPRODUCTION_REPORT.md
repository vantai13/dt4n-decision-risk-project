# GO-check — kết quả tái lập local

Cấu hình khóa local ở 9272119; dự đoán Claude AI được nhập từ tài liệu
người dùng (sandbox 1a66a24 chưa kiểm độc lập). Kết quả sandbox đã được
đọc trước khi tái lập local; không gọi đây là xác nhận mù.

## Dự đoán ↔ kết quả (trước diễn giải)

| Dự đoán AI | Kết quả local | Đối chiếu |
|---|---|---|
| FIX mỗi lần trong [0,9; 2,3] ms | 1.506; 1.746 ms | Cả hai trong khoảng |
| Hai lần FIX lệch ≤0,8 ms | 0.240 ms | Trong mức dự đoán |
| SYM trong [−0,05; 0,2] ms, mức gần 0 (<0,1) | 0.153 ms | Trong khoảng; sai mức |
| FF dương trong [0; 0,8] ms | -0.193 ms | Ngoài khoảng, sai dấu |
| Thứ hạng FIX > FF > SYM | FIX > SYM > FF | Sai thứ hạng |
| FIX α=1%, CI chứa 0 và abs(gap)<0,1 (fresh) | +0.118 [+0.020; +0.216] | Trượt |
| FIX cooldown trong [0; 1] (fresh) | 0.681 ms | Trong khoảng |
| FIX α=1%, CI chứa 0 và abs(gap)<0,1 (info) | -0.013 [-0.049; +0.022] | Khớp |
| FIX cooldown trong [0; 1] (info) | 0.641 ms | Trong khoảng |
| SYM delay thấp nhất cả hai luật, trong [2,3; 3,5] ms | SC 2.785; K2 2.632 | Khớp |
| FIX_minus_SYM: CI dương | +1.593 [+1.273; +1.913] | Khớp |
| FIX_minus_FF: CI dương | +1.940 [+1.582; +2.297] | Khớp |
| SYM, α=0.01, cooldown=0: abs(gap)<0,15 | +0.033 ms | Khớp |
| FF, α=0.01, cooldown=0: abs(gap)<0,15 | -0.010 ms | Khớp |
| SYM, α=0.002, cooldown=30: abs(gap)<0,15 | +0.155 ms | Trượt |
| FF, α=0.002, cooldown=30: abs(gap)<0,15 | -0.151 ms | Trượt |
| SYM, α=0.01, cooldown=30: abs(gap)<0,15 | +0.155 ms | Trượt |
| FF, α=0.01, cooldown=30: abs(gap)<0,15 | -0.151 ms | Trượt |

## Tất cả cấu hình đo

| Lần chạy | Bố trí | α | Cooldown | SC ms | K2 ms | SC−K2 [CI95] ms | Harm SC/K2 (% epoch) | TC1 | TC3 |
|---|---|---|---|---|---|---|---|---|---|
| fresh | FIX | 0.2% | 0 s | 5.675 | 4.168 | +1.506 [+1.229; +1.784] | 0.1842/0.2133 | Chưa đạt | Chưa đạt |
| fresh | FIX | 1.0% | 0 s | 3.922 | 3.805 | +0.118 [+0.020; +0.216] | 1.0192/0.9783 | Đạt | Chưa đạt |
| fresh | FIX | 0.2% | 30 s | 5.519 | 4.839 | +0.681 [+0.411; +0.950] | 0.1775/0.0717 | Đạt | Chưa đạt |
| fresh | FIX | 1.0% | 30 s | 5.519 | 4.839 | +0.681 [+0.411; +0.950] | 0.1775/0.0717 | Đạt | Chưa đạt |
| info | FIX | 0.2% | 0 s | 5.770 | 4.024 | +1.746 [+1.427; +2.066] | 0.2200/0.1992 | Đạt | Chưa đạt |
| info | SYM | 0.2% | 0 s | 2.785 | 2.632 | +0.153 [+0.139; +0.167] | 0.2425/0.1517 | Đạt | Chưa đạt |
| info | FF | 0.2% | 0 s | 3.289 | 3.483 | -0.193 [-0.291; -0.095] | 0.2067/0.2108 | Chưa đạt | Chưa đạt |
| info | FIX | 1.0% | 0 s | 3.624 | 3.637 | -0.013 [-0.049; +0.022] | 1.0375/1.1092 | Chưa đạt | Chưa đạt |
| info | SYM | 1.0% | 0 s | 2.665 | 2.632 | +0.033 [+0.015; +0.051] | 0.7808/0.1517 | Đạt | Chưa đạt |
| info | FF | 1.0% | 0 s | 3.215 | 3.225 | -0.010 [-0.054; +0.035] | 0.4967/0.5650 | Chưa đạt | Chưa đạt |
| info | FIX | 0.2% | 30 s | 5.372 | 4.731 | +0.641 [+0.218; +1.065] | 0.2017/0.0517 | Đạt | Chưa đạt |
| info | SYM | 0.2% | 30 s | 3.586 | 3.432 | +0.155 [-0.048; +0.358] | 0.0308/0.0033 | Chưa đạt | Chưa đạt |
| info | FF | 0.2% | 30 s | 4.143 | 4.294 | -0.151 [-0.308; +0.006] | 0.0442/0.0508 | Chưa đạt | Chưa đạt |
| info | FIX | 1.0% | 30 s | 5.372 | 4.731 | +0.641 [+0.218; +1.065] | 0.2017/0.0517 | Đạt | Chưa đạt |
| info | SYM | 1.0% | 30 s | 3.586 | 3.432 | +0.155 [-0.048; +0.358] | 0.0308/0.0033 | Chưa đạt | Chưa đạt |
| info | FF | 1.0% | 30 s | 4.143 | 4.294 | -0.151 [-0.308; +0.006] | 0.0442/0.0508 | Chưa đạt | Chưa đạt |

TC1 là điều kiện gợi ý giữ nguyên trong spec: CI dưới >0,
harm_K2 ≤ harm_SC +0,1α và cả hai ≤1,25α. Không đổi để cứu kết quả.
TC3 giữ CI hai biên gap−8,1 ms và gap−10% headroom theo L1.5.
FF được chấm số học nhưng không dùng suy ra ưu thế của đo thụ động thật.

## Hiệu-của-hiệu và so sánh bổ sung

| So sánh | α | Cooldown | Hiệu [CI95] ms | Vai trò |
|---|---|---|---|---|
| FIX_minus_SYM | 0.2% | 0 s | +1.593 [+1.273; +1.913] | planned_difference_in_differences |
| FIX_minus_FF | 0.2% | 0 s | +1.940 [+1.582; +2.297] | planned_difference_in_differences |
| FIX_minus_SYM | 1.0% | 0 s | -0.046 [-0.087; -0.006] | planned_difference_in_differences |
| FIX_minus_FF | 1.0% | 0 s | -0.004 [-0.057; +0.050] | planned_difference_in_differences |
| FIX_minus_SYM | 0.2% | 30 s | +0.486 [+0.065; +0.908] | planned_difference_in_differences |
| FIX_minus_FF | 0.2% | 30 s | +0.792 [+0.350; +1.234] | planned_difference_in_differences |
| FIX_minus_SYM | 1.0% | 30 s | +0.486 [+0.065; +0.908] | planned_difference_in_differences |
| FIX_minus_FF | 1.0% | 30 s | +0.792 [+0.350; +1.234] | planned_difference_in_differences |
| SC_FIX_minus_SC_SYM | 0.2% | 0 s | +2.986 [+2.496; +3.475] | posthoc_information_vs_policy |
| K2_FIX_minus_SC_SYM | 0.2% | 0 s | +1.239 [+0.910; +1.569] | posthoc_information_vs_policy |

## Giới hạn và phán quyết

CHƯA GO: TC1 phụ thuộc lần lặp/cấu hình, TC2 chưa có nguồn mới,
TC3 không vượt sàn 8,1 ms. SYM vẫn có lợi thế nhỏ nên không nói
mọi lợi thế đều cần bất đối xứng. Trong R1 này, hiệu ứng lớn tập trung ở FIX.
FF bỏ thông tin fast của path vừa rời; đây là giới hạn thiết kế đã được
nguồn sandbox cảnh báo, không phải bug số học mà V1–V6 loại trừ được.
Hai script hậu kiểm báo sai lệch tại các epoch được chọn để đổi;
chưa đo trực tiếp ping-pong hoặc can thiệp FF có trí nhớ để xác định nguyên nhân.

CSV per-seed, summary, contrasts và manifest nằm cùng thư mục.
Output chính: fresh_output.txt, info_outcome_output.txt.
Hậu kiểm: posthoc_reliability_output.txt, posthoc_switch_errors_output.txt.
