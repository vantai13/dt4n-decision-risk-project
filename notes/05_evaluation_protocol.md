# Evaluation protocol — v1.1 (2026-09-25)

> Soạn với hỗ trợ của công cụ AI; tác giả kiểm và chịu trách nhiệm nội dung. v1.1 theo nhận xét GVHD 2026-09-25:
> tiêu chí K2 bằng ms, phạm vi theo tầng, X1′ và X2, Mininet là mục cắt đầu tiên. Đóng băng tới DP0.
> Thuật ngữ: `06_definitions.md`. Bản v1 cũ của hướng trust gate: `notes/archive/v1_trust_gate/05_experiment_design.md`.

## 1. Bốn tầng công bằng

| Tầng | Yêu cầu | Cách đảm bảo |
|---|---|---|
| Cùng dữ liệu | Mọi luật chạy trên cùng quỹ đạo traffic | CRN: cùng seed traffic cho mọi luật trong một run; so sánh paired theo seed |
| Cùng ngân sách tune | Cùng seed calibration, cùng tiêu chí K2 (gain với ngân sách harm), cùng c | Một hàm hiệu chỉnh chung cho mọi luật |
| Cùng tập quyết định | Mọi luật đối mặt cùng đường hiện tại ở mỗi epoch | Decision-level với quỹ đạo tham chiếu (mục 2) |
| Cùng tri thức | Không luật nào được biết cấu trúc mà luật khác không được biết | Bảng knowledge parity (mục 4) |

## 2. Hai tầng đánh giá (K16)

- **Decision-level (CHÍNH).** Quỹ đạo tham chiếu = quỹ đạo của luật tĩnh đã tune (hiện trạng vận hành) trên cùng traffic.
  Ở mỗi epoch, mọi luật quyết định một bước từ đúng trạng thái đó. Hiệu chỉnh (λ, H, r, q) và đánh giá dùng CÙNG loại
  tham chiếu (seed calibration cho hiệu chỉnh, seed test cho đánh giá). Mọi metric chính (gain, harm, gap, G,
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
| Luật K2 của twin | F chính + tri thức tĩnh (mục 4) | như trên |
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

| Mã | Thực tế | Loại | Tầng | Dùng ở |
|---|---|---|---|---|
| M0 | Twin cùng họ mô hình sinh dữ liệu, tham số ước lượng | verification | 1–2 | e03, e05 |
| M1 | Twin sai K | sai trong họ | 2 | e07 |
| X1′ | Token bucket kiểu HTB trong DES (burst 1600 B, bfifo), khớp truth_table (P05) | sai ngoài họ: hàng đợi | 2 | e08 |
| X2 | Tải dựng từ trace thật — chỉ khi F1 tìm được chuỗi thời gian | sai ngoài họ: traffic (kiểm giả định OU) | 2–3 | e08 |
| M2 | Twin giả Poisson khi thật là H2 | sai trong họ | 3 | e07 |
| X1 | Mininet | xác nhận thứ tự và dấu, ≤ 2 cấu hình; mục cắt đầu tiên | 3 | e08 |

## 6. Baseline và giải thích thay thế nó loại trừ

| Baseline | Tầng | Loại trừ giải thích |
|---|---|---|
| Luôn đổi; không bao giờ đổi | 1 | Cận hiển nhiên; kiểm pipeline |
| Tĩnh tốt nhất tuyệt đối + tương đối, tune từng ô (K22) | 1 | "Chỉ cần chỉnh ngưỡng theo cấu hình / theo độ lớn" |
| Forecast-to-now + ngưỡng tĩnh | 1 | "Sửa tâm là đủ" |
| Delta method | 1 | "Độ rộng bậc nhất là đủ" |
| Oracle (F chính) | 1 | Cận trên ở decision-level |
| Luật K2 của twin (Ī − λ·p− > c) | 2 | — (phương pháp) |
| Lai đóng băng (Î/s_twin > q) | 2 | "Lợi ích chỉ do hình dạng bất định, không do thang đo tuyệt đối" |
| History đóng băng | 2 | "Dữ liệu gần đây tự học được thang đo" |
| History + ACI; lai + ACI | 3 | Hiệu chỉnh online dưới dịch chuyển |
| Tĩnh toàn cục; chỉ theo tuổi; μ + k·s kiểu Liyanage/Burbano; hold-down; MIMD | 3 (nếu kịp) | Như bảng v1 |

## 7. Seed (K13)

| Nhóm | Dải | Ghi chú |
|---|---|---|
| Pilot / spike | 9000–9999 | Đã dùng: 9001–9003 (P01), 9101–9103 (P02), 9104 (P03), 9105–9114 (P04); seed cũ 1, 42 (diagnostic) |
| Ước lượng oracle | 30000–39999 | Dữ liệu dựng bảng bin p± |
| Calibration | 10000–19999 | Tune λ, H, r, q; ước lượng tham số OU của twin |
| Test | 20000–29999 | Chỉ mở khi pre-registration tương ứng đã khoá |

Không dải nào được dùng cho mục đích khác. Test tự động kiểm giao nhau rỗng khi có file config (Phase 3–4).

## 8. Bảng thí nghiệm

| Mã | Nội dung | Tầng đánh giá | Thực tế | Vai trò | Tầng phạm vi | RQ / H |
|---|---|---|---|---|---|---|
| e00 | DES khớp nghiệm M/D/1/K (lát cắt) và P–K; step test | — | — | verification | 1 | — |
| e01 | H1 qua pipeline thật | decision | tuyến tính–Gauss | verification | 1 | H1 |
| e02 | Độ tin cậy của p± oracle | decision | M0 | verification | 1 | — |
| e03 | Bản đồ gap_fixed_oracle_ms | decision | M0 | confirmatory | 1 | RQ1, H2a–c |
| e04 | OFAT cơ chế (có biến thể "chỉ nhiễu đếm") | decision | M0 | một phần confirmatory | 1 | RQ1 |
| e05 | RQ2 cùng chế độ + ablation | cả hai | M0 | verification | 2 | H3 (M0) |
| e07 | Twin sai mô hình | cả hai | M1 (tầng 2); M2 (tầng 3) | confirmatory | 2–3 | H3 |
| e08 | Thực tế ngoài họ | cả hai | X1′, X2 (tầng 2); Mininet (tầng 3) | confirmatory | 2–3 | H3 |
| e06 | Dịch chuyển chế độ, tham số đóng băng | cả hai | M0 | confirmatory | 3 | H3′ |

Claim confirmatory cho NCKH (tầng 1–2): H2a, H2b, H2c, H3. Tầng 3: H3′.

## 9. Ngoài scope

Vòng kín và hiệu ứng bầy đàn; nhiều luồng lớn; tối ưu TE toàn mạng; tối ưu chuỗi quyết định nhiều bước
(oracle chỉ một bước; flap đo ở tầng trajectory).
