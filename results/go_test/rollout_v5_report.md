# Rollout v5 — tái lập POST HOC

Một ô R3_outage, 20 seed calibration + 20 seed test, 640 bản ghi seed/luật.
Hold-down 30 s; horizon twin 30 s; α=0,002 và ∞.
Chính sách α hữu hạn và ∞ giống nhau ở 8/8 họ (so mọi tham số).

Dương = delay baseline − delay K2, tốt cho K2; CI t ghép cặp qua 20 seed.

| Luật | Delay cal → test ms | Luật − K2 ms [CI 95%] | Giảm delay | Harm_W test (% epoch) |
|---|---:|---:|---:|---:|
| S0 | 4.918 → 4.928 | +1.050 [+0.717; +1.384] | +21.31% | 0.0675% |
| SC | 4.558 → 4.490 | +0.613 [+0.294; +0.931] | +13.65% | 0.0458% |
| S0dir | 4.847 → 5.016 | +1.138 [+0.762; +1.514] | +22.69% | 0.0617% |
| SCdir | 4.544 → 4.477 | +0.600 [+0.280; +0.919] | +13.39% | 0.0408% |
| SCtab8 | 4.299 → 4.564 | +0.687 [+0.249; +1.124] | +15.04% | 0.0442% |
| SCtab24 | 3.625 → 3.960 | +0.082 [-0.113; +0.278] | +2.08% | 0.0558% |
| SClin | 4.520 → 4.329 | +0.451 [+0.088; +0.815] | +10.43% | 0.1208% |
| K2 | 3.949 → 3.877 | +0.000 [+0.000; +0.000] | +0.00% | 0.0308% |

## Diễn giải

- K2 hơn SClin hai tham số ở ô đã dùng: +0,451 ms, CI loại 0.
  Đây chưa phải xác nhận mới, chưa loại mọi hàm ngưỡng hai tham số khác.
- So SCtab24 có ràng buộc và ba khởi đầu: +0,082 ms, CI chứa 0;
  chưa chứng minh hơn, cũng chưa chứng minh tương đương.
- α hữu hạn/∞ chọn cùng chính sách: ràng buộc không cắn cho ô và lưới này,
  không phải định lý cho các chế độ/twin khác.
- Twin 30 s, p₋ trong [0,001; 0,01), Ī>0: p₋ TB 0.004472,
  harm_W thật 0.014229, gấp 3.18 lần. p₋ chưa hiệu chỉnh xác suất.
  Tune harm bằng nhãn thật, không thay nó bằng p₋ dự đoán.
- Các luật SC* dùng cùng tâm của cùng twin biết đúng ρ̄, σ, τ;
  lợi thế ở đây chưa nói được độ bền khi twin phải tự ước lượng.

## Provenance / giới hạn

Claude đã chạy trước trong sandbox. SClin/harm_W được thiết kế sau v4.
Calibration 86001–86020, test 89001–89020 đã dùng; không phải holdout mới.
29 epoch cuối dùng cửa sổ ngắn dần theo code nguồn; không phải mọi harm_W đều đủ 30 s.
Harm chia cho tất cả epoch; không phải tỷ lệ hại trong các lần đổi.
CI mang tính khám phá, không hiệu chỉnh đa so sánh.
Horizon khớp hold-down không bảo đảm mô hình delay đúng do phi tuyến và bộ nhớ hàng đợi.
Không đổi phán quyết/SESOI VoIP cũ; không khẳng định uncertainty chỉ có giá trị trong outage.

## Bộ ước lượng chuẩn bị để review

`experiments/scan/telemetry_fit.py`: chỉ đọc telemetry tươi/timestamp và T,S;
ước lượng ρ̄ bằng trung bình, σ và τ bằng covariance off-diagonal giữ khoảng trống outage.
Đã kiểm bằng OU-box/Poisson tổng hợp, không dùng tham số DES thật.
Chưa chạy DES seed 90001–90020/91001–91020; chưa đo K2 với twin ước lượng.

## Tệp

- `rollout_v5_output.txt`: log đầy đủ.
- `rollout_v5_seeds.csv`: calibration/test, harm_W, harm_1s, chuyển đường, mọi tham số.
- `rollout_v5_diagnostics.csv`: bias và hiệu chỉnh rủi ro cho horizon 1/30 s.
- `rollout_v5_policies.json`: chính sách và kiểm α hữu hạn/∞.
- `rollout_v5_summary.csv`, `rollout_v5_comparisons.csv`: tổng hợp và CI.
- `telemetry_fit_synthetic.{csv,json}`, `telemetry_fit_synthetic_output.txt`: kiểm tổng hợp.
- `notes/map/telemetry_fit_review.md`: công thức, giả định và protocol dự thảo chờ review.
