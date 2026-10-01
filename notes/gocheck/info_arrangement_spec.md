# Info-arrangement v1 — dự thảo trước outcome

Ngày 2026-10-01. Trạng thái: locked.
Loại lần chạy: tái lập kết quả sandbox đã được cung cấp, không xác nhận mù local.

## Câu hỏi

Lợi thế rollout K2 so với SC trong R1 có phụ thuộc bố trí telemetry
FIX / SYM / FF không?

## Thiết kế

Cùng thế giới DES, cal 94001–94020, test 95001–95020; chỉ đổi thông tin twin.
Phải đạt validity V1–V6 trước outcome. Chính: SC−K2 (delay TB rollout, ms)
ở α = 0,2%, cooldown 0; hiệu-của-hiệu FIX−SYM và FIX−FF ghép cặp theo seed.
FIX là lần lặp độc lập thứ hai của Bước 1. Phụ: α = 1%, cooldown 30 s.
Tune riêng trên calibration cho từng bố trí và luật; mẫu số harm là mọi epoch.
GRID/EPS giữ như Bước 1; telemetry bổ sung dùng RNG [seed, 424242].

## Nguồn dự đoán và lệch NT-1

Dự đoán A/B/C/D là của Claude (AI), giữ nguyên tại PREDICTIONS_claude.md.
Không thay bằng dự đoán tác giả. Commit sandbox 1a66a24 và giờ khóa do nguồn
người dùng cung cấp, chưa kiểm độc lập tại local. Kết quả sandbox đã được
đọc trước khi tái lập; khóa local là khóa cấu hình, không tiền đăng ký mù.

## Diễn giải dự kiến — khóa cùng dự đoán

| Kết quả chính | Nghĩa là | Việc tiếp theo TC2 |
|---|---|---|
| Chỉ FIX có cận dưới CI > 0, cả hai hiệu-của-hiệu có cận dưới > 0 | Bằng chứng trong R1 cho vai trò bất đối xứng cố định | Tìm hệ thống thật có bố trí FIX |
| SYM có cận dưới CI > 0 | Hiệu ứng tồn tại cả khi đo đối xứng trong R1 | Kiểm tính thực tế của telemetry và TC3 |
| FF có cận dưới > 0, SYM không | Hiệu ứng tồn tại với mô hình đo theo luồng | Tìm nguồn đo thụ động và quyết định cỡ giây |
| FIX có CI chứa 0 trên seed mới | Chưa tái lập được độ phân giải của go0 | Báo GVHD; CI chứa 0 không chứng minh hiệu ứng bằng 0 |
| FIX có cận trên < 0 | Dấu hiệu đảo chiều | Dừng kết luận ưu thế K2, báo GVHD |

Nếu các CI hiệu-của-hiệu chứa 0, chưa xác định sự khác nhau giữa bố trí.
Không suy “cần thiết” chỉ từ một bố trí có ý nghĩa và một bố trí không có.

## Giới hạn

FF có ngay số đo 1 s khi chuyển sang path mới, không có warm-up. Mô hình
không dựng quá trình đo thụ động thật. Twin vẫn biết tham số OU; outcome cơ chế
không tự xác nhận TC2 ngoài đời. Oracle nhìn trước chỉ là thang đo.
Nếu ngưỡng chạm biên GRID: ghi cảnh báo; mọi mở rộng phải ghi decision log và
tái chạy cả hai bước, không âm thầm chọn lại theo test.

## Khóa

Commit spec cùng code và dự đoán AI được nhập trước tái lập 94001/95001.
FF giữ nguyên để tái lập; không thêm trí nhớ trong lần chạy này. Kết quả FF
chỉ áp dụng cho bố trí không nhớ telemetry vừa rời, không đại diện đo thụ động thật.
