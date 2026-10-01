# GO test v0 — khóa trước chạy, 2026-10-01

## Ba dự đoán

- R1_dualISP: dự đoán GO CÓ ĐIỀU KIỆN, có khả năng ở α=0,2%; sai rho trung bình dễ làm mất GO hơn sai tau.
- R2_bb_LTE: dự đoán GO CÓ ĐIỀU KIỆN; bất đối xứng capacity/buffer tạo headroom nhưng sai rho/sigma có thể làm lệch thứ hạng rủi ro.
- Quét biên: TB=1 s và buffer=50 ms dễ mất hiệu ứng; TB=300 s không nhất thiết tốt hơn TB=60 s; không dùng các ô này để quyết định.

## Khóa thiết kế

Giữ các kịch bản R1/R2, 8 ô biên, 6 sai số twin và mọi ngưỡng của hướng dẫn. Calibration 80001–80020, test 81001–81020; chưa chạy các seed này trước commit. Bootstrap theo seed 100 lần, RNG 54321. Alpha 1% và 0,2%; epsilon chính 1 ms. Epsilon 8,1 ms chỉ báo cáo. Tổng cộng 38 dòng đánh giá.

Đạt một dòng khi: oos_lo>0; frontier/headroom≥3% và fr_lo>0; harm cần của K2 để đạt gain SC / harm SC thực dùng ≤0,7; harm ngoài mẫu của SC và K2 ≤1,5alpha.

GO ở một alpha cần đúng cả 7 trạng thái twin (đúng + 6 sai số) đạt. Có ít nhất một alpha GO thì kịch bản GO; nếu không, đúng twin đạt ở một alpha thì GO CÓ ĐIỀU KIỆN; còn lại NO-GO. Tổng GO nếu có một kịch bản GO; nếu không có GO nhưng có điều kiện thì tổng có điều kiện; nếu cả hai NO-GO thì tổng NO-GO. Quét biên không tham gia.

## Sửa lỗi đo lường/tổng hợp trước chạy

1. strict_frontier.matched trả harm_ratio theo mẫu số alpha. Hướng dẫn diễn giải theo harm SC thực dùng; go_test chuyển sang mẫu số đó trước GO_RULE, giữ cả harm_ratio_budget và harm_ratio trong CSV. SC không dùng harm thì không chứng minh được giảm 30% harm; ratio là inf.
2. verdict duyệt đủ hai alpha, ưu tiên GO thay vì dừng ở GO CÓ ĐIỀU KIỆN đầu tiên. Kiểm đủ 7 trạng thái để tránh GO từ kết quả thiếu.
3. Lưu CSV sau từng kịch bản, thêm cận trên CI frontier, các số harm và manifest để kiểm toán; không đổi simulator, seed hoặc ngưỡng.

14 test theo hướng dẫn và 3 test bổ sung cho hai sửa lỗi trên phải xanh trước chạy. Không chạy pilot hoặc xem outcome GO trước commit này.

## Phạm vi kết luận

Nhãn GO/NO-GO áp dụng cho cổng mô phỏng và hai cấu hình đã khóa. Các nhãn [nguồn] trong tài liệu cung cấp là động cơ chọn kịch bản, chưa được kiểm chứng nguồn độc lập ở bước chạy này. Tốc độ, tải, flow, tau và nhịp quyết định vẫn là giả định. NO-GO ở hai ô không chứng minh mọi cấu hình thực tế đều không có hiệu ứng. GO cũng chưa xác nhận triển khai thật hay đạt SESOI VoIP.
