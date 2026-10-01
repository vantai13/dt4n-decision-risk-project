# GO check v1 — bản đặc tả trước khi chạy seed fresh

Ngày tạo: 2026-10-01. Trạng thái: locked.
Loại lần chạy: tái lập kết quả sandbox đã được cung cấp, không xác nhận mù local.

## Câu hỏi

Khi mỗi luật tự đi quỹ đạo của nó (rollout), K2 có giảm delay trung bình của
luồng so với SC được tune công bằng, ở ngân sách harm tương đương, trong R1
không?

## Estimand chính

Delay trung bình luồng phải chịu (ms), rollout, trên test 93001–93020; ngưỡng
tune trên 92001–92020 (rollout), harm ≤ α (mẫu số là mọi epoch).

## TC1 — cùng harm

Đạt nếu cận dưới CI95 của `delay(SC) − delay(K2)` > 0, `harm_K2 ≤ harm_SC +
0,1α`, và cả hai ≤ 1,25α. Đây là ngưỡng gợi ý trong hướng dẫn; tác giả/GVHD
cần xác nhận trước khi khóa.

## TC2 — tính thực tế

Đánh giá bằng bảng nguồn về: bất đối xứng độ tươi telemetry, phân bố utilization,
ý nghĩa vận hành của `(α, ε)`, và nhịp chuyển đường.

## TC3 — giữ quy tắc SESOI đã khóa 26/09

Ứng dụng VoIP; brief §6 và experiment log L1.5. Đạt nếu
`delay(SC) − delay(K2) ≥ 8,1 ms` VÀ ≥ 10% headroom_rollout, với
`headroom_rollout = delay(SC) − delay(oracle nhìn trước)`.
Oracle là cận dưới nhìn trước, chỉ dùng làm thang đo.
Giữ cách kết luận theo CI đã khóa tại L1.5: tính theo seed
`D_abs = gap − 8,1` và `D_rel = gap − 0,1 × headroom_rollout`;
đạt khi cả hai cận dưới CI95 > 0; không đáng kể nếu ít nhất một cận trên < 0;
còn lại chưa kết luận. Bản dịch estimand được ghi decision log ngày 2026-10-01.

## Nguồn dự đoán và lệch NT-1

Dự đoán là của Claude (AI), giữ nguyên tại PREDICTIONS_claude.md theo yêu cầu
người dùng ở lượt này. Không gán thành dự đoán tác giả. Tài liệu sandbox nói
đã khóa tại 1a66a24 trước outcome; commit này chưa kiểm được trong repo local.
Tại local, các kết quả sandbox đã được đọc trước lần chạy: đây là tái lập.
Giữ TC1 gợi ý nêu trên và TC3 như đã viết; không sửa ngưỡng sau kết quả.

## Quy tắc khóa

Cấu hình và bản dự đoán AI nhập từ sandbox được commit trước lần tái lập
local trên 92001/93001. Đây không phải tiền đăng ký hồi tố; dải này đã được
xem qua báo cáo sandbox. Rollout v6 90001/91001 vẫn để dành.
