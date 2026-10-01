# Kết quả xác nhận v0 — 2026-10-01

## Kết quả chính

Đã chạy đủ 22 ô × 3 bậc = 66 dòng trong 392 giây. Trong 21 ứng viên, A đạt 13, B đạt 17, C đạt 9. Đối chứng âm không đạt cả ba bậc, khớp số mẫu trong hướng dẫn.

Code và dự đoán khóa trước chạy: commit 7946bb2. 7 test đạt (2,95 giây). Chạy lại bản đồ sau refactor có SHA256 không đổi: 75b912a9186e3442bdcf7e13a9061501ab6fd05b44197f78e1d693547ffa1595.

## Các ô đạt DES (bậc C)

Width = gain K2 − gain SC; ± là nửa độ rộng CI 95% paired theo 20 test seed. Gain và headroom là trung bình trên mọi quyết định.

| Ô | τ (s) | probe B | ρ B | α | Width ± CI (ms) | % headroom | % SC | Headroom (ms) | Center (ms) | harm K2/α | harm SC/α |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| m069 | 10 | 30.0 | 0.95 | 0.002 | 0.928 ± 0.259 | 5.16 | 79.9 | 17.989 | 0.948 | 0.994 | 0.700 |
| m071 | 10 | 30.0 | 0.85 | 0.002 | 0.310 ± 0.106 | 3.19 | 33.4 | 9.733 | 0.862 | 1.000 | 0.744 |
| m085 | 60 | 30.0 | 0.95 | 0.002 | 0.788 ± 0.177 | 8.27 | 84.8 | 9.531 | 0.812 | 1.127 | 1.035 |
| m070 | 10 | 30.0 | 0.85 | 0.01 | 0.390 ± 0.117 | 4.66 | 28.2 | 8.376 | 1.172 | 1.049 | 0.965 |
| m087 | 60 | 30.0 | 0.85 | 0.002 | 0.546 ± 0.243 | 7.97 | 54.1 | 6.846 | 0.922 | 1.085 | 1.148 |
| m084 | 60 | 30.0 | 0.95 | 0.01 | 0.481 ± 0.177 | 6.23 | 28.1 | 7.714 | 1.552 | 0.959 | 0.981 |
| m086 | 60 | 30.0 | 0.85 | 0.01 | 0.291 ± 0.103 | 5.72 | 22.8 | 5.082 | 1.150 | 1.002 | 1.056 |
| m080 | 60 | same | 0.95 | 0.01 | 0.090 ± 0.017 | 7.52 | 26.6 | 1.192 | 0.080 | 0.941 | 0.913 |
| m083 | 60 | same | 0.85 | 0.002 | 0.053 ± 0.020 | 5.38 | 22.6 | 0.993 | 0.032 | 0.996 | 1.035 |

Cả 9 ô đều có r_f=300k b/s, T_tel_A=0,5 s. Có 7 ô probe B=30 s và 2 ô cùng nhịp. Hai ô cùng nhịp đạt C nhưng lợi ích tuyệt đối nhỏ: m080 khoảng 0,090 ms và m083 khoảng 0,053 ms. m069 có width lớn nhất, khoảng 0,928 ms, headroom 17,989 ms.

## Từng ứng viên qua A/B/C

Các lý do dưới đây dựa vào số đầy đủ trong CSV, không dùng số làm tròn trên màn hình.

| Ô | A | B | C | Điều kiện thiếu ở C |
|---|---|---|---|---|
| m053 | Không | Không | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m069 | Đạt | Đạt | Đạt | Đạt |
| m068 | Đạt | Đạt | Không | 20% SC |
| m071 | Đạt | Đạt | Đạt | Đạt |
| m075 | Không | Không | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m085 | Đạt | Đạt | Đạt | Đạt |
| m070 | Đạt | Đạt | Đạt | Đạt |
| m037 | Đạt | Đạt | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m087 | Đạt | Đạt | Đạt | Đạt |
| m084 | Đạt | Đạt | Đạt | Đạt |
| m036 | Đạt | Đạt | Không | 2% headroom, 20% SC |
| m093 | Đạt | Không | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m065 | Đạt | Đạt | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m067 | Không | Đạt | Không | 20% SC |
| m086 | Đạt | Đạt | Đạt | Đạt |
| m032 | Không | Đạt | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m033 | Không | Không | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m041 | Đạt | Đạt | Không | CI width, 2% headroom, 20% SC, CI vs best |
| m081 | Không | Đạt | Không | 20% SC |
| m080 | Không | Đạt | Đạt | Đạt |
| m083 | Không | Đạt | Đạt | Đạt |

A → B: m093 mất xác nhận do width/headroom dưới 2%; B phục hồi m067, m032, m081, m080, m083. B → C: 8 ô mất xác nhận (m068, m037, m036, m065, m067, m032, m041, m081). Không đạt mức hiệu ứng tối thiểu không đồng nghĩa hiệu ứng bằng 0: m068, m067, m081 vẫn có CI width dương nhưng thiếu 20% SC.

## Đối chiếu dự đoán

Dự đoán A/B/C = 10/14/6; đo được 13/17/9. Dự đoán 5 ô probe thưa và 1 ô cùng nhịp τ=60 s đạt C; đo được 7 và 2. m069 đúng là đạt C. Dự đoán thận trọng hơn kết quả; sự phục hồi ở B phù hợp với khả năng p₋ vẫn xếp hạng hữu ích khi xác suất tuyệt đối lệch, nhưng chưa đủ để chứng minh cơ chế này.

## Diễn giải và giới hạn

- Cả 9 ô đạt C tuân thủ điều kiện đã khóa: harm SC và K2 ≤ 1,5α. Điều này không bảo đảm harm test bằng nhau hoặc ≤ α. Ví dụ m069: harm K2=0,19875%, SC=0,14000%, α=0,2%. Vì vậy chưa thể coi toàn bộ chênh gain là ưu thế tại harm test khớp hoàn toàn.
- Center=SC−S0, width=K2−SC. Ở đa số ô probe thưa, center lớn hơn width; sửa tâm và dùng bất định đều đóng góp.
- Bậc A dùng seed mới và telemetry đếm gói trong thế giới DES, khác bộ sinh telemetry của map gốc; A thất bại không tự nó chứng minh map chỉ may mắn seed. Điều kiện xác nhận cũng chặt hơn map.
- B/C tune lại gain thật, harm thật, baseline tốt nhất và quỹ đạo tham chiếu. Đây là xác nhận theo protocol được cung cấp; không phải chỉ thay xác suất harm trong một policy cố định.
- CI theo seed là CI từng ô, chưa hiệu chỉnh cho nhiều phép kiểm. Twin vẫn một cửa sổ, tải OU độc lập, mô phỏng vòng hở. Kết quả là xác nhận trong mô phỏng theo tiêu chí khóa, chưa xác nhận hệ thống thật.

## Quyết định và file

Có 9 ô đạt C: tiếp tục kiểm tính thực tế có nguồn, quy mô tuyệt đối và novelty; sau đó họp thầy chốt SESOI. Kiểm twin có lịch sử là bước tiếp theo sau xác nhận này.

- results/scan/confirm_v0.csv: toàn bộ 66 dòng, gồm số đo 5 luật.
- results/scan/confirm_output.txt: toàn bộ log và thời gian.
- notes/map/confirm_spec.md: tiền đăng ký.
- experiments/scan/confirm.py và des_world.py: mã chạy.

Chưa thực hiện nghiên cứu nguồn/novelty, chưa đổi twin sang bộ lọc lịch sử trong lần chạy này.
