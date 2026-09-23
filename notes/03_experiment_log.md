# Experiment log

Mẫu cho mỗi thí nghiệm (copy khối dưới):

## eNN — tên
- **RQ / hypothesis:**
- **Dự đoán (viết TRƯỚC khi chạy):**
- **Config + seed:** experiments/configs/...
- **Kết quả:** results/eNN/...
- **Diễn giải:** (khớp / không khớp dự đoán — vì sao?)
- **Bước tiếp theo:**

## 2026-09-23 — Exposure và chuẩn bị L0.3/L0.4

- Agent được người dùng yêu cầu tự kiểm tra và điền choices/brief/design.
- Đã xem đáp án VD2–VD6; lời giải được ghi là tham khảo, không phải tự làm mù.
- Đã chạy Monte Carlo exact/naive ở lượt trước, seed 0, n=2.000.000.
  z/tau=0,3: 56.030 mẫu trong bin, observed=0,023219703730144564,
  exact=0,023223298670823258, naive=0,006115615880504457.
- Đã đọc pilot do người viết lesson cung cấp: W hữu hạn làm calibration dao động;
  D0 phi tuyến có thể gây underprediction lớn. Các số pilot này chưa được agent
  tái chạy bằng wsim.py/nl.py. Không gán chúng cho artifact của đồ án.
- Lượt hiện tại chỉ kiểm data summary, ví dụ số và existing tests; chưa chạy e01–e12.
- Dự đoán thiết kế nằm trong brief/design v1; trước confirmatory phải bổ sung
  config, seed list, contrast và family Holm cụ thể. Hướng đã thấy ở pilot không
  được gọi là phát hiện mù; e03 nhắm ranh giới calibration và hành vi D1.

## 2026-09-23 — Sanity check D12 trước khi sửa W_ref

- Review ngoài chỉ ra W_ref v1 có κ≈2,256 và H2 suy biến; đây là exposure trước test.
- Agent chọn trước κ_ref=0,5 vì còn path ưu thế nhẹ nhưng always-trust không tự đạt
  harmful budget trong cell tham chiếu ở tuổi trung bình.
- Chạy NumPy seed 20260923, n=4.000.000, Gaussian OU exact, σ_D=2,437490,
  z/tau=0,3: pair flip=0,2054485; harmful@2ms=0,03101175;
  mean regret=0,22203761 ms.
- Mục đích chỉ là kiểm câu hỏi có khả năng phân biệt phương pháp; không dùng batch
  này làm confirmatory evidence và không tune κ tiếp theo kết quả phương pháp.
