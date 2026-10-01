# Rollout v5 — tái lập POST HOC và chuẩn bị bộ ước lượng

## Phạm vi trước lần chạy tại repo (2026-10-01)

Nền `634e133`, nhánh `rollout-v5`. Tái lập đúng một ô R3_outage bằng code
attachment: calibration 86001–86020, test 89001–89020, hold-down và horizon
twin 30 s, α=0,002 và ∞. Cả hai dải seed đã dùng; Claude đã chạy trước trong
sandbox. SClin và harm_W được thêm sau khi thấy v4. Không phải holdout mới.

Giữ nguyên thuật toán tune và kernel trong code cung cấp. Chỉ bổ sung CSV,
tham số đã tune, kiểm đồng nhất chính sách α hữu hạn/∞ và chẩn đoán twin 1 s
trên chính test đã dùng. SCtab24 nay chịu cùng ràng buộc harm_W như K2,
lưới bao gồm nửa dưới phân bố và dùng ba khởi đầu coordinate descent.

Lưu ý biên: `window_mean` trong code nguồn rút ngắn cửa sổ ở HD−1 epoch cuối.
Giữ nguyên để tái lập, nhưng không gọi mọi nhãn là đủ 30 s; lần kiểm định mới
cần sinh thêm 29 epoch tương lai cho nhãn. “Horizon khớp hold-down” không
đồng nghĩa twin dự đoán đúng delay tích luỹ (phi tuyến/Jensen, bộ nhớ hàng đợi).

## Bước ước lượng — viết để review, chưa mở test mới

Viết module ước lượng ρ̄, σ, τ chỉ từ bản tin calibration tươi và các đại lượng
vận hành biết được (T telemetry, service time từ capacity/cỡ gói).
Kiểm bằng dữ liệu tổng hợp và công thức covariance, không chạy seed DES
90001–90020 / 91001–91020 trong đợt này. Chỉ đóng băng và chạy phép so mới
sau review bộ ước lượng/protocol, theo yêu cầu trong attachment.

## Kết quả đã chạy

8/8 họ chọn cùng mọi tham số ở α=0,002 và ∞. Điều này chỉ xác nhận ràng
buộc không cắn trong một ô và lưới đã kiểm, không mở rộng thành khẳng định chung.

| Luật | Delay cal → test ms | Luật − K2 ms [CI 95%] |
|---|---:|---:|
| SC | 4,558 → 4,490 | +0,613 [+0,294; +0,931] |
| SCdir | 4,544 → 4,477 | +0,600 [+0,280; +0,919] |
| SCtab8 | 4,299 → 4,564 | +0,687 [+0,249; +1,124] |
| SCtab24 | 3,625 → 3,960 | +0,082 [−0,113; +0,278] |
| SClin | 4,520 → 4,329 | +0,451 [+0,088; +0,815] |
| K2 | 3,949 → 3,877 | — |

K2: μ=0, θ≈331,8; SClin h₀≈7,831 ms, h₁=0,5 ms/s.
Chênh với SClin 10,43%, với SCtab24 2,08%; vẫn chưa phân giải bảng 24.
p₋ TB khoảng 0,0045 nhưng harm_W thật 0,0142 trong bucket [0,001;0,01),
Ī>0, horizon 30 s. Không coi p₋ là xác suất hiệu chỉnh.

640 bản ghi seed/luật cho hai mức α và hai split. 126/126 test đạt
(110 cũ + 16 trường hợp mới). Kết quả tái lập khớp bảng v5 trong attachment.
Kiểm tổng hợp estimator: σ lệch 0,8–2,2%, τ lệch 0,9–3,5%; chưa đo kết quả
K2 với twin ước lượng trên DES. Xem `notes/map/telemetry_fit_review.md` để review.

Tệp đầy đủ ở `results/go_test/rollout_v5_report.md`, các CSV/log cùng tiền tố,
`rollout_v5_policies.json` và `rollout_v5_manifest.json`.
