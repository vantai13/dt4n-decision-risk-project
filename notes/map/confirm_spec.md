# Confirm spec v0 — viết và commit TRƯỚC khi chạy confirm (ngày: 2026-10-01)

## Câu hỏi

21 ứng viên của map v0 có còn đứng khi (A) đổi seed, (B) ép ngân sách harm bằng hại thật,
(C) sự thật là hàng đợi gói (DES)?

## Thiết kế (chép từ confirm.py)

Thế giới DES ghép cặp · seed hiệu chỉnh 30001–30020 · seed kiểm tra 20001–20020 · 21 ô + đối chứng âm.

Danh sách khóa: m053, m069, m068, m071, m075, m085, m070, m037, m087, m084,
m036, m093, m065, m067, m086, m032, m033, m041, m081, m080, m083.

A: tune expected / PSA. B: tune realized / PSA. C: tune realized / DES.
Mỗi ô dùng cùng telemetry và đầu ra twin cho cả ba bậc; quỹ đạo tham chiếu được tune lại ở mỗi bậc theo code được cung cấp.

## Tiêu chí xác nhận (KHÓA)

cận dưới CI width > 0 · width ≥ 2% headroom · width ≥ 20% gain SC ·
cận dưới CI (K2 − baseline tốt nhất) > 0 · harm thật của K2 và SC ≤ 1,5·α

## Dự đoán (viết trước khi chạy)

- Số ô đạt ở bậc A / B / C: 10 / 14 / 6. A có thể mất nhiều ô do điều kiện harm bổ sung; B có thể phục hồi ô khi tune bằng sự thật; C có thể giảm hiệu ứng do trí nhớ hàng đợi.
- Nhóm probe_B = 30 s: dự đoán 5 ô đạt C; bất đối xứng độ tươi còn tạo khả năng xếp hạng rủi ro, đặc biệt với A đo 0,5 s và tải thô.
- Nhóm cùng nhịp, τ = 60 s: dự đoán có 1 ô đạt C; không loại trước vì p₋ có thể xếp hạng tốt dù xác suất tuyệt đối lệch. Quy mô ms có thể nhỏ.
- Ô tôi tin nhất sẽ đứng ở bậc C: m069, vì width map lớn và tài liệu cung cấp báo p₋ ít lệch ở ô này.
- Đối chứng âm: dự đoán không đạt cả A/B/C và width C gần 0.

Các dự đoán có sử dụng kết quả map v0 và thông tin đối chứng/m082 trong hướng dẫn; chưa chạy bất kỳ ứng viên xác nhận nào trước commit này.

## Kiểm trước chạy

- 7 test đạt, gồm DES/MDK và ngân sách realized.
- Chạy lại map sau refactor: SHA256 75b912a9186e3442bdcf7e13a9061501ab6fd05b44197f78e1d693547ffa1595; CSV không thay đổi.

## Quyết định

≥ 1 ô đạt bậc C → kiểm tính thực tế + quy mô tuyệt đối + novelty, rồi họp thầy chốt SESOI.

0 ô đạt bậc C → ghi rõ hiệu ứng chết ở bậc nào, mang lên thầy để NARROW/PIVOT.
