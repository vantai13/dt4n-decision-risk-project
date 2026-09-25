# Evaluation protocol — v1 (2026-09-25)

> Bản nháp do Claude (AI) soạn theo yêu cầu tác giả (L0.5); tác giả kiểm. Trả lời TRƯỚC khi có số liệu chính:
> so trên tập quyết định nào, ai thấy gì, ai biết gì, trong thực tế nào, bằng baseline nào, với seed nào.
> Thuật ngữ: `06_definitions.md` v2. Quyết định: K5, K6, K10, K13, K14, K16, K18, K19, K20 (`02_decision_log.md`).
> Bản v1 cũ của hướng trust gate: `notes/archive/v1_trust_gate/05_experiment_design.md`.

## 1. Bốn tầng công bằng

| Tầng | Yêu cầu | Cách đảm bảo |
|---|---|---|
| Cùng dữ liệu | Mọi luật chạy trên cùng quỹ đạo traffic | CRN: cùng seed traffic cho mọi luật trong một run; so sánh paired theo seed |
| Cùng ngân sách tune | Cùng seed calibration, cùng tiêu chí K2 (missed + κ·đổi, harm ≤ α), cùng κ | Một hàm hiệu chỉnh chung cho mọi luật |
| Cùng tập quyết định | Mọi luật đối mặt cùng đường hiện tại ở mỗi epoch | Decision-level với quỹ đạo tham chiếu (mục 2) |
| Cùng tri thức | Không luật nào được biết cấu trúc mà luật khác không được biết | Bảng knowledge parity (mục 4) |

## 2. Hai tầng đánh giá (K16)

- **Decision-level (CHÍNH).** Quỹ đạo tham chiếu = quỹ đạo của luật tĩnh đã tune (hiện trạng vận hành) trên cùng traffic.
  Ở mỗi epoch, mọi luật quyết định một bước từ đúng trạng thái đó. Hiệu chỉnh (λ, H, r, q) và đánh giá dùng CÙNG loại
  tham chiếu (seed calibration cho hiệu chỉnh, seed test cho đánh giá). Mọi metric chính (J, missed, harm, gap, G,
  harm_excess_shift, chỉ số H2) ở tầng này. Oracle là cận trên ở tầng này, theo kỳ vọng.
- **Độ nhạy:** lặp decision-level với tham chiếu ngẫu nhiên (đường hiện tại tung đồng xu) và tham chiếu = quỹ đạo oracle.
- **Trajectory-level (PHỤ).** Mỗi luật tự đi quỹ đạo riêng: switch_rate, flap_rate, delay_mean_ms, delay_p95_ms, loss_rate.
- **Nếu thứ hạng khác nhau giữa hai tầng:** báo cáo như một phát hiện; không chọn tầng cho số đẹp.
- Bằng chứng thiết kế (P04, exploratory, 10 seed): với tham chiếu ngẫu nhiên, luật tốt nhất ở decision-level (10/10)
  lại tệ nhất khi chạy thật (thắng 0/10); với tham chiếu thực tế, thứ hạng giữ sang tầng chạy thật (7/10 về J, 8/10 về delay).

## 3. Tập thông tin

| Luật | Thấy | KHÔNG thấy |
|---|---|---|
| Ngưỡng tĩnh (tuyệt đối H, tương đối r) | F chính → Î, Ĉ_cur | probe, tải thật, hàng đợi, nhãn |
| Twin posterior-odds | F chính + tri thức tĩnh (mục 4) | như trên |
| Lai đóng băng / lai ACI | F chính → Î, s_twin; ACI: nhãn của epoch ĐÃ kết thúc | nhãn chưa kết thúc |
| Data-driven (history đóng băng / ACI) | F chính + nhãn của epoch đã kết thúc | như trên |
| Oracle | F chính + đúng mô hình sinh dữ liệu (M0) | trạng thái ẩn, nhiễu tương lai |

- F chính, F mở rộng: K6. Nhãn của epoch e chỉ có từ thời điểm t_e + a + H_hold.
- **Điều kiện:** F_oracle ⊇ F của mọi luật. Thí nghiệm với F mở rộng phải có oracle riêng dùng F mở rộng.
  (P04: luật dùng 2 cửa sổ thắng oracle 1 cửa sổ ở 10/10 seed.)
- **Phép thử tự động:** luật nào có J thấp hơn oracle quá 2 sai số chuẩn Monte Carlo → dừng, tìm rò rỉ thông tin hoặc bug.

## 4. Knowledge parity (K18)

| Cặp chế độ (calibrate → test) | Twin được báo? | Data-driven được báo? | Lý do vận hành |
|---|---|---|---|
| Đổi buffer K | Có: cập nhật K | Có: biết thời điểm đổi; hiệu chỉnh lại sau N epoch (báo thời gian hồi phục) | Cấu hình là thông tin quản trị |
| Poisson → H2 | Không (trừ khi twin ước lượng C_a² online; nếu không thì là M2) | Không | Burstiness không có trong cấu hình |
| Đổi mức tải ρ̄ | Có, qua telemetry | Có, qua telemetry | Cả hai quan sát |
| Đổi τ, σ | Không: tham số OU theo đoạn calibration | Không | Chỉ lộ ra qua dữ liệu |

- Tham số OU của twin ước lượng trên đoạn calibration; luật data-driven được dùng CÙNG đoạn đó.
- Luật tĩnh và oracle cũng đóng băng tham số khi dịch chuyển (e06).

## 5. Các thực tế đánh giá (K20)

| Mã | Thực tế | Loại | Dùng ở |
|---|---|---|---|
| M0 | Twin cùng họ mô hình sinh dữ liệu, tham số ước lượng | verification | e05 |
| M1 | Twin sai K | sai trong họ | e07 |
| M2 | Twin giả Poisson khi thật là H2 | sai trong họ | e07 |
| X1 | Mininet: HTB token bucket (burst 1600 B) + bfifo | sai ngoài họ | e08 |
| X2 | Tải dựng từ trace thật (phụ thuộc dài hạn) | sai ngoài họ, dự phòng nếu X1 không khả thi | e08 |

## 6. Baseline và giải thích thay thế nó loại trừ

| Baseline | Bắt buộc? | Loại trừ giải thích |
|---|---|---|
| Luôn đổi; không bao giờ đổi | có | Cận dưới/trên hiển nhiên; kiểm pipeline |
| Tĩnh tốt nhất của họ tuyệt đối + tương đối, tune từng ô (K22) | có | "Chỉ cần chỉnh ngưỡng theo cấu hình / theo độ lớn" (Seshadri–Katz; RON) |
| Forecast-to-now + ngưỡng tĩnh | có | "Sửa tâm (Jensen, dự báo tới hiện tại) là đủ" |
| Delta method (ngưỡng ∝ s bậc nhất) | có | "Độ rộng bậc nhất là đủ, không cần lan truyền đầy đủ" |
| Twin posterior-odds | có (phương pháp) | — |
| Lai đóng băng; lai ACI (K19) | có | "Lợi ích chỉ do hình dạng bất định, không do thang đo tuyệt đối" |
| History đóng băng; history + ACI | có | "Dữ liệu gần đây tự học được thang đo" |
| Oracle (F chính) | có | Cận trên ở decision-level |
| Tĩnh toàn cục (một H cho mọi ô) | nếu kịp | "Tune từng ô có cần không" |
| Chỉ theo tuổi | nếu kịp | "Chỉ tuổi dữ liệu là đủ" |
| Rủi ro μ + k·s kèm ngưỡng tĩnh (kiểu Liyanage 2026) | nếu kịp | "Thực tiễn risk-aware hiện có đã đủ" |
| Hold-down (trajectory) | nếu kịp | "Chỉ cần chống flap" |
| H động MIMD (Seshadri–Katz) | nếu kịp | "Một H động đơn giản là đủ" |

## 7. Seed (K13)

| Nhóm | Dải | Ghi chú |
|---|---|---|
| Pilot / spike | 9000–9999 | Đã dùng: 9001–9003 (P01), 9101–9103 (P02), 9104 (P03), 9105–9114 (P04); seed cũ 1, 42 (diagnostic) |
| Ước lượng oracle | 30000–39999 | Dữ liệu dựng bảng bin p± |
| Calibration | 10000–19999 | Tune λ, H, r, q; ước lượng tham số OU của twin |
| Test | 20000–29999 | Chỉ mở khi pre-registration tương ứng đã khoá |

Không dải nào được dùng cho mục đích khác. Test tự động kiểm giao nhau rỗng khi có file config (Phase 3–4).

## 8. Bảng thí nghiệm

| Mã | Nội dung | Tầng | Thực tế | Vai trò | RQ / H |
|---|---|---|---|---|---|
| e00 | DES khớp nghiệm M/D/1/K, P–K; step test | — | — | verification | — |
| e01 | H1 qua pipeline thật | decision | tuyến tính–Gauss | verification | H1 |
| e02 | Độ tin cậy của p± oracle (reliability diagram) | decision | M0 | verification | — |
| e03 | Bản đồ gap_fixed_oracle | decision | M0 | confirmatory | RQ1, H2a, H2b, H2c |
| e04 | Cô lập cơ chế (OFAT) | decision | M0 | một phần confirmatory | RQ1 |
| e05 | So sánh trong cùng chế độ + ablation | cả hai | M0 | verification | RQ2 (H3a M0) |
| e06 | Dịch chuyển chế độ, tham số đóng băng | cả hai | M0 | confirmatory | RQ2, H3b |
| e07 | Twin sai mô hình | cả hai | M1, M2 | confirmatory | RQ2, H3a (M1) |
| e08 | Thực tế ngoài họ | cả hai | X1 (hoặc X2) | confirmatory | RQ2, H3b |

Số claim confirmatory: ≤ 6 (H2a, H2b, H2c, H3a-M1, H3b).

## 9. Ngoài scope

Vòng kín và hiệu ứng bầy đàn; nhiều luồng lớn; tối ưu TE toàn mạng; tối ưu chuỗi quyết định nhiều bước
(oracle chỉ một bước; flap đo ở tầng trajectory).
