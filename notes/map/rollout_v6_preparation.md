# V6 — đã chuẩn bị code/protocol, CHƯA KHOÁ/CHƯA CHẠY

Ngày 2026-10-01. Nền `8f0c899`. Reviewer chấp thuận bộ ước lượng; các con số
DES calibration cũ trong attachment là kết quả reviewer, không ghi như lần
chạy mới của Codex. Không chỉnh estimator sau khi xem sai lệch so tham số thật.

## Ba sửa đổi đã thực hiện

1. Test 60 seed, 91001–91060; calibration vẫn 20 seed, 90001–90020.
2. Chọn phương án (a): SCtab24 chỉ mô tả. Không TOST, không chọn δ,
   không gọi tương đương khi CI chứa 0. Phép so chính là SClin−K2.
3. `twin_config` thay ba tham số bằng fit cal, không đổi cấu hình thế giới.
   Test toàn tuyến từ telemetry calibration → fits → Ī,p₋ giữ nguyên từng bit
   khi rho/sigma/tau thật bị thay bằng NaN/999/−1. Có test loại nhãn delay/future
   khỏi thông tin twin và loại padding telemetry khỏi dữ liệu ước lượng.

Pipeline `experiments/scan/rollout_v6.py` đã viết. Cửa sổ harm đủ 30 s kể cả
epoch cuối nhờ 29 epoch nhãn padding; không rút ngắn như v5. Fit và policy
được freeze trước khi mở test; không fallback tham số thật. Mọi trạng thái
CI (dương, âm, chứa 0) và cách đọc harm được xác định trước.

Estimator giữ nguyên SHA-256 từ `8f0c899`:
`1b8d7092d9260bad889f03a53263af3924e494f9c7a75708f07d5c2bb6a6abca`.
Không thay lags, trọng số, bounds hoặc cửa sổ lọc bản tin.

## Power tính lại — chỉ từ CSV v5 đã dùng

SClin−K2 có trung bình 0,451258 ms, sd giữa seed 0,776273 ms.
Power t hai phía α=0,05, giả định sd giữ nguyên và seed độc lập:

| Hiệu ứng giả định | n=20 | n=40 | n=60 |
|---|---:|---:|---:|
| 0,451258 ms | 0,694 | 0,948 | 0,993 |
| 0,225629 ms | 0,235 | 0,434 | 0,601 |

SCtab24−K2 mean 0,082412 ms, sd 0,417052 ms: power n=60 chỉ 0,325.
Đây là tính power điều kiện theo dữ liệu khám phá, không bảo đảm power thật.
Winner's curse và thay đổi sd có thể khiến hiệu ứng/power thật khác đi.

## Kiểm đã chạy

138/138 test đạt (126 cũ + 12 trường hợp mới). Chỉ dữ liệu tổng hợp/mock và
CSV v5. Test generator dùng mock engine, seed 123, không sinh DES mới.
Guard draft được kiểm: `main()` dừng TRƯỚC gọi simulator. Guard thực tế
yêu cầu prediction tác giả, protocol locked, SHA code khớp và tag commit
`prereg-rollout-v6`; nhánh/commit chuẩn bị này không phải commit khóa.

## Còn thiếu duy nhất trước khoá

Dự đoán của tác giả (người dùng) chưa nhận. Không chuyển dự đoán trợ lý
§6 thành lời tác giả. Trường `author_prediction` trong JSON vẫn null;
`status` vẫn `draft_awaiting_author_prediction`; chưa tạo tag tiền đăng ký.

Sau khi nhận dự đoán: ghi vào protocol → commit/tag khóa → chạy calibration
90001–90020 → freeze fit/policy → chạy test 91001–91060. Nếu cal validity
không đạt, dừng trước test, không tune estimator bằng tham số thật.

V6 chỉ kiểm việc bỏ quyền biết tham số trong họ OU+Poisson đúng. Không tự
chứng minh sai họ mô hình, tiết kiệm dữ liệu, novelty hoặc ứng dụng VoIP.
