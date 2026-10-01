# Frontier spec v0 — khóa trước khi chạy (2026-10-01)

## Câu hỏi

K2 còn lợi thế gain so với SC khi dùng cùng ngân sách harm thực tế trên DES không, đặc biệt ở m069 và m071? Để đạt gain SC, K2 cần bao nhiêu harm?

## Thiết kế khóa

Giữ nguyên mã frontier.py trong hướng dẫn. Chạy đối chứng âm NEG_P2_cu và 9 ô đạt C: m069, m071, m085, m070, m087, m084, m086, m080, m083.
Seed calibration 30001–30020, test 20001–20020; thế giới DES ghép cặp và quỹ đạo S0 tune realized như bậc C.
300 bootstrap theo seed; RNG 12345 dùng liên tiếp theo thứ tự ô trên. CI percentile 95%.
So gain cực đại của các tiền tố xếp hạng với harm không vượt α; tính harm tối thiểu K2 cần để đạt gain SC tại ngân sách α.

## Dự đoán trước chạy

- m069: Δ cùng harm vẫn dương, CI dưới > 0; dự đoán Δ khoảng 0,5–0,9 ms và harm ratio khoảng 0,5–0,8.
- m071: Δ vẫn dương, nhưng nhỏ hơn m069; dự đoán Δ khoảng 0,1–0,3 ms, CI dưới > 0 và harm ratio khoảng 0,6–0,9.
- Dự đoán 7/9 ô có CI dưới của Δ > 0. Không đặt lại tiêu chí xác nhận C cho frontier.
- Nhóm cùng nhịp m080/m083 có thể có harm ratio thấp nhưng Δ tuyệt đối vẫn nhỏ (<0,2 ms).
- Đối chứng âm: CI chứa 0 và harm ratio gần 1.

Dự đoán dùng kết quả confirm và ví dụ đối chứng/m082 được cung cấp; chưa chạy frontier trên ứng viên trước commit.

## Cách diễn giải và quyết định

CI dưới Δ > 0 tại m069/m071 hỗ trợ lợi thế xếp hạng ở cùng ngân sách harm. CI chứa 0 nghĩa là chưa phân biệt được lợi thế đó ở dữ liệu này; không tự nó chứng minh mọi width trước đây đều do chênh harm.
Điểm vận hành được tối ưu trên chính test, không phải đánh giá ngoài mẫu của ngưỡng đã học. Hai luật cùng được tối ưu dưới trần harm α, không bảo đảm số lần harm sử dụng chính xác bằng nhau.
SESOI VoIP 8,1 ms giữ nguyên; không đổi metric hay SESOI theo kết quả. Nghiên cứu nguồn, novelty và lựa chọn metric ứng dụng là bước tiếp theo, chưa chạy thêm kịch bản trong lần này.
