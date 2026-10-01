# GO switch v1 — khóa trước chạy, 2026-10-01

## Hai dự đoán

- R1 ở trần trung bình 1 lần/30 s: dự đoán NO-GO ở cả hai alpha; CI chênh lợi ích ròng có thể chứa 0. R2 dự đoán tương tự hoặc hiệu ứng tuyệt đối rất nhỏ.
- Ô biên buffer 500 ms có khả năng còn đạt khi hạn chế tần suất; các ô cùng nhịp hoặc buffer 50 ms dễ mất hiệu ứng. Chi phí 5/10 ms có thể vẫn để lại lợi thế ở alpha=0,2%.

## Thiết kế khóa

Dùng đúng thuật toán go_switch.py được cung cấp: 10 kịch bản, alpha 0,2% và 1%, 6 thiết lập; tổng 120 dòng. PRIMARY là 1 lần/30 s. GO cần CI dưới >0, chênh gain ròng >=10% gain SC, harm mỗi luật <=1,5alpha, tần suất trung bình mỗi luật <=1,2H/period. Chỉ R1/R2 quyết định; các ô biên, cost và period khác chỉ mô tả ranh giới.

MUS gồm 0 và các số nguyên 1..80 ms. Ngưỡng SC và cặp mu/lambda K2 học trên calibration. Epsilon harm vẫn 1 ms, harm định nghĩa I<-epsilon, không trừ cost; gain ròng trừ cost mỗi hành động. World/twin đúng theo GO v0, không thử misspecification ở v1.

Calibration 80001–80020, test 81001–81020, giữ nguyên theo yêu cầu. Các seed test đã dùng và đã xem ở GO v0; thông tin phân tích của người cung cấp đã dùng để thiết kế v1. Vì vậy khóa này là trước lần chạy v1, không phải trước mọi tiếp xúc test; không gọi là xác nhận độc lập trên holdout mới.

Trần số hành động là tổng số trung bình, không phải cooldown theo thời gian từng lần. Đánh giá mọi luật trên cùng quỹ đạo tham chiếu S0: sw là tỉ lệ đề nghị đổi tại các trạng thái tham chiếu, chưa phải tần suất từ quỹ đạo triển khai riêng của K2/SC. Giữ phương pháp để đối chiếu với hướng dẫn; diễn giải đúng giới hạn này trong báo cáo.

Chỉ bổ sung lưu manifest, tham số ngưỡng, số đo calibration và per-seed, CSV tiến độ; không đổi logic fit/act, ngưỡng GO hoặc chọn seed sau khi xem kết quả.
