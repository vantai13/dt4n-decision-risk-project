# GO/NO-GO v0 — kết quả 2026-10-01

Đã kiểm đủ 38 dòng, không thiếu/trùng tổ hợp; tính lại GO_RULE khớp toàn bộ cờ trong CSV. Code và dự đoán khóa trước chạy ở commit 104841f. 14 test theo hướng dẫn + 3 test sửa lỗi trước chạy đạt; toàn bộ suite sau chạy: 95 passed in 5.49s.

## Kết luận theo tiêu chí đã khóa

- R1_dualISP: **GO**, α=0.002, ε=1 ms; cận dưới lợi ích ngoài mẫu khi twin đúng 1.897784 ms.
- R2_bb_LTE: **GO**, α=0.002, ε=1 ms; cận dưới lợi ích ngoài mẫu khi twin đúng 0.104934 ms.

Tổng: **GO** theo cổng mô phỏng; cả hai kịch bản đạt 7/7 trạng thái twin tại α=0,2%. Chưa đạt SESOI VoIP 8,1 ms. Nhãn này không xác nhận hệ thống triển khai thật.

## Hai kịch bản, twin đúng, α=0,2%, ε=1 ms

| Kịch bản | Headroom ms | Δ ngoài mẫu [CI 95%] ms | Δ frontier [CI 95%] ms | % headroom | Harm SC/K2 ngoài mẫu | Harm ratio |
|---|---:|---|---|---:|---|---:|
| R1_dualISP | 6.496308 | 2.498301 [1.897784; 3.098818] | 2.449392 [1.915667; 3.009833] | 37.704% | 0.136667% / 0.161667% | 0.000000 |
| R2_bb_LTE | 0.834696 | 0.192354 [0.104934; 0.279774] | 0.206117 [0.148730; 0.280120] | 24.694% | 0.153333% / 0.157500% | 0.000000 |

## Độ bền theo từng alpha

| Kịch bản | α | Số trạng thái đạt | Trạng thái không đạt và lý do |
|---|---:|---:|---|
| R1_dualISP | 1% | 6/7 | τ×0.5: CI ngoài mẫu chứa 0; CI frontier chứa 0 |
| R1_dualISP | 0.2% | 7/7 | Không có |
| R2_bb_LTE | 1% | 4/7 | σ×0.7: CI ngoài mẫu chứa 0; frontier <3% headroom; CI frontier chứa 0 / τ×0.5: CI ngoài mẫu chứa 0; frontier <3% headroom; harm ratio >0,7 / ρ̄−0.05: CI ngoài mẫu chứa 0; frontier <3% headroom; CI frontier chứa 0 |
| R2_bb_LTE | 0.2% | 7/7 | Không có |

Các sai số được thử từng loại riêng và áp dụng cho cả hai path; không kiểm sai số kết hợp, sai khác từng path, drift thời gian hoặc lỗi mô hình tải.

## Quét biên (không quyết định GO)

| Ô | Δ ngoài mẫu ms | Δ frontier ms | % headroom | Kết quả/lý do |
|---|---:|---:|---:|---|
| R1_TB1 | 0.147725 | 0.151330 | 34.788% | Đạt |
| R1_TB10 | 0.077295 | 0.086874 | 11.329% | harm SC >1,5α |
| R1_TB30 | 0.795480 | 0.781676 | 30.623% | Đạt |
| R1_TB300 | 3.421138 | 3.371468 | 40.257% | Đạt |
| R1_quietB | 0.025963 | 0.021053 | 13.146% | Đạt |
| R1_tau15 | 2.095767 | 2.223357 | 28.027% | Đạt |
| R1_buf50 | 0.572325 | 0.449792 | 25.946% | Đạt |
| R1_buf500 | 7.354165 | 7.331282 | 37.251% | Đạt |

## Epsilon bổ sung (chỉ báo cáo)

- R1_dualISP, ε=8,1 ms: Δ ngoài mẫu 1.177479 [0.820916; 1.534041] ms; frontier 0.559626 ms. Không đưa vào nhãn GO.
- R2_bb_LTE, ε=8,1 ms: Δ ngoài mẫu 0.076280 [0.027072; 0.125488] ms; frontier 0.059199 ms. Không đưa vào nhãn GO.

## Đối chiếu dự đoán

Dự đoán trước chạy là cả R1/R2 GO CÓ ĐIỀU KIỆN. Kết quả mạnh hơn dự đoán tại α=0,2%, nhưng tại α=1% vẫn có các kiểu sai twin làm mất điều kiện. Không thể suy ra độ bền với mọi sai số twin.

Dự đoán TB=1 s và buffer=50 ms dễ mất hiệu ứng bị dữ liệu bác bỏ: cả hai vẫn đạt tiêu chí tương đối. Ô cùng nhịp có Δ ngoài mẫu chỉ khoảng 0,148 ms và headroom khoảng 0,435 ms; buffer 50 ms có Δ khoảng 0,572 ms. Vì vậy không được kết luận bất định chỉ hữu ích khi hai path đo lệch nhịp. TB=300 s đạt Δ ngoài mẫu 3,421 ms, cao hơn TB=60 s trong lần chạy này.

## Cách đọc harm ratio và giới hạn

- Harm ratio chính dùng harm tối thiểu của K2 để đạt gain frontier SC chia cho harm SC thực dùng; giữ thêm harm_ratio_budget để đối chiếu mã gốc. Dòng twin đúng α=0,2% ở cả R1/R2 có numerator đúng bằng 0 trên mẫu test: một ngưỡng K2 tối ưu trên test đạt gain SC mà chưa thấy sự kiện hại. Đây không phải rủi ro quần thể bằng 0 hay một policy ngoài mẫu không bao giờ gây hại. Policy calibration vẫn có harm ngoài mẫu dương như bảng.
- Frontier tối ưu ngay trên test, CI bootstrap 100 lần theo seed. Ngoài mẫu dùng ngưỡng học trên calibration, CI paired t trên 20 test seed. Không hiệu chỉnh nhiều phép kiểm; các alpha/variant dùng cùng thế giới, không độc lập.
- Chu kỳ 1/60 s, buffer 150/500 ms là lựa chọn được tài liệu người dùng gợi ý. Lần này chưa xác minh độc lập tài liệu nguồn; capacity, rho, r_f, tau, H vẫn là giả định. “GO thực tế” chỉ nên hiểu là GO trên hai cấu hình mô phỏng có động cơ thực tế, không phải tham số đã đo từ triển khai.
- Telemetry vẫn đếm gói trong cửa sổ; không phải đo RTT trực tiếp. Từ mô tả LTE/probe tiết kiệm dữ liệu sang bộ đếm tải OU còn cần kiểm ánh xạ.
- R2 headroom chỉ khoảng 0,835 ms nên đạt tỉ lệ giảm rủi ro/width không có nghĩa delay cải thiện đáng kể cho VoIP. Không thay metric hoặc SESOI cũ để biến nhãn GO thành bằng chứng ứng dụng.
- Lần chạy chỉ xét SC và K2 trong gate; không thêm điều kiện thắng Sage hoặc kiểm twin lịch sử. Tải OU, một flow nhỏ, vòng hở và twin biết đường cong capacity/buffer vẫn là giả định.

## Thay đổi trước chạy và artifact

Sửa trước khi khóa: ratio theo harm SC thực dùng; duyệt cả hai alpha để ưu tiên GO; kiểm đủ 7 trạng thái; CSV lưu sau từng kịch bản; thêm CI trên và manifest. Không đổi ngưỡng hay kịch bản sau khi đọc kết quả.

- results/go_test/go_v0.csv: 38 dòng số đầy đủ.
- results/go_test/go_output.txt: log chạy và thời gian từng kịch bản.
- results/go_test/go_manifest.json: seed, cấu hình, sai số twin, alpha/epsilon.
- notes/map/go_spec.md: dự đoán/tiêu chí trước chạy.
- experiments/scan/go_test.py: runner; report_go.py: kiểm tính đầy đủ và dựng báo cáo này.

Quyết định: có thể đi sâu theo cổng đã chọn. Ưu tiên R1 vì lợi ích tuyệt đối lớn hơn R2; bước sau là kiểm nguồn/ánh xạ telemetry và twin ước lượng từ lịch sử. Chưa tự chạy thêm phạm vi ngoài bài GO trong lượt này.
