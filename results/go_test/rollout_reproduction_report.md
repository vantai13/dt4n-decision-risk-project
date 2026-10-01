# Closed-loop v2–v4: tái lập POST HOC

7,080 dòng seed; 29 cấu hình; 20 seed calibration + 20 seed test mỗi cấu hình.
Bảng v4 khớp số làm tròn trong attachment: 8/9.

Dương = delay baseline − delay K2 > 0, nghĩa là K2 tốt hơn. CI t ghép cặp 95% qua seed.

| Thế giới | Baseline | Δ ms [CI 95%] | Giảm delay |
|---|---|---:|---:|
| R1_dualISP | S0dir | -0.189 [-0.665; +0.288] | -4.12% |
| R1_dualISP | SCtab | -0.144 [-0.584; +0.295] | -3.12% |
| R1_dualISP | SCtab24 | -0.222 [-0.671; +0.227] | -4.88% |
| R3_outage | S0dir | +1.060 [+0.724; +1.397] | +21.47% |
| R3_outage | SCtab | +0.602 [+0.271; +0.933] | +13.44% |
| R3_outage | SCtab24 | +0.121 [-0.069; +0.312] | +3.04% |
| R3_outageB | S0dir | +0.598 [+0.365; +0.832] | +13.83% |
| R3_outageB | SCtab | +0.338 [+0.172; +0.504] | +8.32% |
| R3_outageB | SCtab24 | +0.148 [-0.086; +0.383] | +3.82% |

Đối chiếu attachment: chênh lệch trung bình của cả 9 dòng khớp ở độ chính xác 0,01 ms.
Riêng R3_outageB/S0dir: CI thực [0.364524; 0.832087] so với [0.37; 0.83] trong attachment; sai khác tối đa 0.005476 ms. Không thay dấu hay kết luận CI loại 0.

## Calibration → test (v4)

| Thế giới | Luật | Calibration ms | Test ms | Harm cal/test (% epoch) |
|---|---|---:|---:|---:|
| R1_dualISP | SCtab | 4.333 | 4.624 | 0.1350/0.1258 |
| R1_dualISP | SCtab24 | 4.176 | 4.547 | 0.1250/0.1217 |
| R1_dualISP | K2 | 4.699 | 4.768 | 0.0542/0.0417 |
| R3_outage | SCtab | 4.325 | 4.479 | 0.0283/0.0142 |
| R3_outage | SCtab24 | 3.709 | 3.999 | 0.0133/0.0117 |
| R3_outage | K2 | 3.949 | 3.877 | 0.0075/0.0017 |
| R3_outageB | SCtab | 3.784 | 4.067 | 0.0550/0.0425 |
| R3_outageB | SCtab24 | 3.502 | 3.877 | 0.0092/0.0100 |
| R3_outageB | K2 | 3.598 | 3.729 | 0.0042/0.0033 |

## Đọc kết quả

- R1: không chứng minh K2 hơn baseline theo chiều/tuổi/tải khi horizon khớp hold-down.
- R3/R3B: so bảng 8 ngưỡng, CI lợi thế K2 loại 0; so bảng 24, CI chứa 0.
  Chưa chứng minh hơn hoặc tương đương bảng 24; chưa kiểm hiệu quả dữ liệu hay dịch chế độ.
- Gap calibration/test chỉ là dấu hiệu mô tả; không tự chứng minh overfit.
- Cả ba dải seed đã được Claude chạy trước trong sandbox; R3 được thiết kế sau kết quả R1.
  Các CI mang tính khám phá, không hiệu chỉnh đa so sánh; không phải xác nhận độc lập.
- Mục tiêu mới không thay thế phán quyết và SESOI VoIP đã đăng ký.

## Công thức / giới hạn

Delay luật = (1/N) Σ D_{đường luật chọn sau hành động}(t).
Harm = số lần đổi có D_hiện_tại − D_đích < −1 ms / N epoch.
K2 đổi khi Ī > μ và (Ī − μ)/p₋ > θ, nếu hết hold-down.
v4 tách nhịp quyết định 1 s khỏi hold-down và horizon twin 30 s.
Nhãn delay vẫn là trung bình probe từng giây, không phải delay từng gói của ứng dụng thực.
Tải nền/hàng đợi được sinh trước, không đổi theo luật; không mô hình chi phí chuyển đường.
Harm đo theo nhãn một giây, KHÔNG phải harm tích lũy suốt 30 s cam kết.
SCtab24 tune không ràng buộc harm theo code nguồn; số harm hậu nghiệm được báo trong CSV.
Coordinate descent là heuristic, không bảo đảm tìm cực tiểu toàn cục cho bảng 8/24.

## Tệp

- `rollout_v{2,3,4}_output.txt`: log đầy đủ.
- `rollout_v{2,3,4}_seeds.csv`: từng seed, cả hai split, μ và ngưỡng đã tune.
- `rollout_summary.csv`: delay, harm, tần suất chuyển theo cấu hình/luật/split.
- `rollout_comparisons.csv`: chênh lệch và CI của mọi baseline, đánh dấu baseline chọn trên calibration.
- `rollout_manifest.json`: seed, môi trường, provenance.
