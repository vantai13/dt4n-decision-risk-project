# Closed-loop rollout v2–v4 — tái lập POST HOC

## Phạm vi ghi trước lần tái lập tại repo

Ngày 2026-10-01, nền `main` = `7c60c76`. Chạy lần lượt ba script
người dùng cung cấp: `rollout_v2`, `rollout_v3`, `rollout_v4`.
Không chạy thêm nghiên cứu dịch chế độ / số seed calibration trong đợt này.

Đây KHÔNG phải tiền đăng ký hay test xác nhận mới:

- Claude đã chạy các script trong sandbox, và kết quả đã được đưa trong attachment.
- R3 được thiết kế sau khi thấy kết quả R1.
- Seed calibration 86001–86020, test v2/v3 87001–87020,
  test v4 89001–89020 đều đã dùng trong sandbox. `TEST_NEW` chỉ là tên biến
  của code gốc, không hàm ý chưa từng xem kết quả.

## Giữ nguyên thuật toán

Nhịp quyết định 1 s; mỗi luật tự lái đường A/B; delay tính sau hành động.
Hold-down là thời gian từ lần đổi thực tế gần nhất. v2 dùng horizon twin 1 s;
v3 đổi horizon trên cùng thế giới; v4 dùng horizon = hold-down = 30 s.
K2 chọn μ và θ, các baseline 1/2/8 ngưỡng tune trên calibration.
SCtab24 dùng 24 ngưỡng và coordinate descent bốn vòng từ SCtab, đúng code gửi.
CI là t ghép cặp qua 20 seed, không điều chỉnh đa so sánh.

“2 so với 24 tham số” ở đây chỉ đếm ngưỡng/μ được tune, không phải tổng
độ phức tạp của controller. Cả hai dùng chung twin với các tham số tải thật
của thế giới; chưa kiểm lợi thế khi phải học hoặc đoán sai mô hình này.

Các thay đổi phục vụ kiểm toán, không đổi lựa chọn chính sách:

- Sửa lời mô tả “seed mới/chưa từng dùng” thành “tái lập”.
- Xuất CSV calibration/test từng seed và ngưỡng đã tune.
- Đếm harm thật cho SCtab24 và in thêm calibration K2.
  SCtab24 trong code gốc tối ưu delay mà KHÔNG áp điều kiện harm;
  sẽ kiểm hậu nghiệm, không giả định sẵn harm luôn không cắn.
- Kiểm đơn vị own-path, hold-down, chiều xác suất K2, tính tương đương
  bảng 8 và bảng 24 khi nhân ngưỡng, và tách horizon twin khỏi thế giới.
- v4 có `--world` / `--append` để chạy tiếp sau gián đoạn, có chặn trùng
  thế giới trong CSV. Lần này R1/R3 chạy xong trước gián đoạn; R3B được
  chạy tiếp bằng `--world R3_outageB --append`, log dùng `tee -a`.

Giữ nguyên phán quyết / SESOI VoIP trước đây. Thước đo delay trải qua và
phần trăm cải thiện ở đây thuộc câu hỏi post hoc mới, không thay thế tiêu chí cũ.

## Kết quả

Đã hoàn thành v2 → v3 → v4; 29 cấu hình, 7.080 dòng từng seed,
110/110 kiểm thử đạt. Log và CSV ở `results/go_test/`.

v2 tái lập R1 không hold-down: SC − K2 +1,334 ms, nhưng
S0dir − K2 chỉ +0,348 ms (khoảng 74% chênh với SC bị baseline theo chiều hấp thụ).
v3: horizon = hold-down làm R1 mất lợi thế so baseline chọn trên calibration:
−0,112 ms ở 30 s và −0,464 ms ở 60 s, cả hai CI chứa 0.

v4 (horizon = hold-down = 30 s, α = 0,2%):

| Thế giới | SCtab − K2 ms [CI 95%] | SCtab24 − K2 ms [CI 95%] |
|---|---:|---:|
| R1 | −0,144 [−0,584; +0,295] | −0,222 [−0,671; +0,227] |
| R3 | +0,602 [+0,271; +0,933] | +0,121 [−0,069; +0,312] |
| R3B | +0,338 [+0,172; +0,504] | +0,148 [−0,086; +0,383] |

So SCtab, K2 giảm delay test 13,44% (R3) và 8,32% (R3B).
So SCtab24, chỉ 3,04% và 3,82%, CI chứa 0: chưa chứng minh hơn,
cũng chưa chứng minh tương đương. Harm SCtab24 calibration/test đều dưới
α: R1 0,1250%/0,1217%; R3 0,0133%/0,0117%; R3B 0,0092%/0,0100%.

Calibration K2 đã được bổ sung: R1 4,699 → test 4,768 ms;
R3 3,949 → 3,877 ms; R3B 3,598 → 3,729 ms.
SCtab24 tương ứng 4,176 → 4,547; 3,709 → 3,999; 3,502 → 3,877 ms.
Gap lớn hơn của bảng 24 phù hợp với nghi vấn overfit, nhưng không chứng minh cơ chế.

9/9 chênh lệch trung bình v4 khớp số làm tròn trong attachment.
8/9 dòng khớp cả CI trong sai số làm tròn: R3B/S0dir cận dưới thực
0,364524 ms (làm tròn 0,36) so với 0,37 trong attachment, lệch 0,005476 ms.
Không sửa code hoặc chọn lại seed để ép số khớp.

Báo cáo đầy đủ: `results/go_test/rollout_reproduction_report.md`.
Chưa chạy bước dịch chế độ / calibration {2,5,20}; cần tiền đăng ký mới và
dải seed chưa dùng nếu triển khai kiểm định xác nhận. Không đổi phán quyết VoIP cũ.
