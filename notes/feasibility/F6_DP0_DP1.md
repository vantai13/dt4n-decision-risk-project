# F6 — DP0 + DP1: đề xuất quyết định (BẢN NHÁP gửi GVHD)

> Ngày soạn 2026-09-27; gửi GVHD trước họp ≥ 24 giờ; họp 20/10/2026. Provenance: Claude (AI) soạn; tác giả kiểm.
> Mọi quyết định trỏ tới luật đã khoá trước kết quả: f04b `cdcea06` (luật 3), f05 `9056ac1` (luật 1), brief §10, D18.

## 1. Quyết định đề xuất

**DP0 = PIVOT "ngưỡng tĩnh đủ, và vì sao".** Không ô nào — ở surrogate lẫn DES, tuổi cố định lẫn dao động, 4 độ mịn
oracle — có khoảng cách tới oracle cùng thông tin đạt SESOI (m = 8,1 ms, r = 10% headroom). Tiêu chí GO của brief §10
không đạt ở điều kiện 1 (không ô nào có ý nghĩa) và điều kiện 4 (DP1 không PASS).
**DP1 = NARROW (D18):** characterization còn khác biệt problem/method với mọi bài gần nhất; RQ2 (luật lai/gate) trùng
một phần OpenTwin, LEC, CERT, Almohammedi.
**Hệ quả:** đóng góp của đồ án = một kết quả âm có phạm vi, có cơ chế, và một giao thức đánh giá.

## 2. Claim có phạm vi và cơ chế

**Claim.** Với một luồng nhỏ trên tải nền ngoại sinh (OU-Poisson), hàng đợi M/D/1/K FIFO, hai path đối xứng, telemetry
đếm gói có tuổi (cố định hoặc dao động T_poll = 0,5 s) và nhiễu, 4 Mb/s, K ∈ {11, 100}, α = 1%: ngưỡng tĩnh được tune thua
oracle cùng thông tin ít hơn SESOI hơn 50 lần ở mọi ô đã kiểm; phần do dùng độ rộng từng quyết định ≤ 0,16 ms.
**Vì sao (ba tầng).**
1. *Cận trên:* |I_D| ≤ (K−1)S; ở 4 Mb/s, K = 11, headroom < m kể cả khi biết trước tương lai (18/24 ô/biến thể, f02b).
2. *Phân rã:* ở ô có headroom lớn nhất (P2, DES), 14,6 ms headroom = thông tin 9,4 + an toàn 1,3 + thích nghi 0,15 ms (f04b).
3. *Cơ chế:* luật tối ưu K2 và ngưỡng tĩnh trên tâm tốt (SC) bất đồng ở ≤ 0,98% quyết định (f05b) — bất định hầu như
   không đảo thứ tự quyết định (H1, T3 §5 gần đúng). Khi twin thấy hàng đợi (Q), gap tăng lên ~4 ms nhưng gần như toàn
   bộ nằm ở tâm (phần thuần 0,018 ± 0,054 ms): giá trị của twin nằm ở dự báo điểm tốt hơn, không ở độ rộng.
**Phát hiện phương pháp.** PSA (surrogate dừng) lệch DES có hệ thống (corr 0,61; +19/+13/−77 ms theo mức) và thổi phồng
cả ba khoảng ở P2, kể cả khoảng thích nghi (DES − PSA = −1,00 ± 0,68 ms).

## 3. Mối đe doạ (xếp theo mức nguy hiểm cho kết luận)

1. **Hai path đối xứng** — kịch bản các lựa chọn khác nhau về rủi ro chưa thử; đây là nơi độ rộng có đường vào quyết định.
2. **Mục tiêu trung bình** — với mục tiêu SLO (xác suất D > τ), σ đi thẳng vào hàm mục tiêu (Liyanage 2026).
3. **Một luồng nhỏ** — nhiều luồng dùng cùng luật trên cùng telemetry sẽ dồn đàn (Fischer–Vöcking; Seshadri–Katz).
4. **Oracle** — chỉ họ bin trong DES; bin thô không phải cận trên (FZ10x5 thua luật tĩnh ~8 SE); nested MC chỉ kiểm ở surrogate.
5. **Mô hình tải** — chỉ OU một thang thời gian; chưa burst on-off/đuôi nặng, chưa tương quan giữa hai path.

## 4. Câu hỏi cho GVHD

1. Chấp nhận DP0 = PIVOT và DP1 = NARROW? Đầu ra (K15) cho một kết quả âm có cơ chế: báo cáo NCKH, bài hội thảo, hay cả hai?
2. Có chạy **một** spike tiền đăng ký "path bất đối xứng" (đe doạ 1) trước khi chốt, hay ghi thành giới hạn?
   Nếu chạy: họ tĩnh phải cho phép ngưỡng theo chiều để baseline công bằng.
3. Mục tiêu SLO (đe doạ 2): mở rộng Phase 2 hay giới hạn?
4. K10: có cần đối chiếu nested MC trong DES (≈ 1 CPU-giờ/ô cho kernel, F4) hay chấp nhận đối chiếu ở surrogate + độ mịn bin?

---
## Phụ lục A — Rủi ro → spike → kết quả → quyết định

| Rủi ro | Spike | Kết quả (số) | Quyết định |
|---|---|---|---|
| Điểm neo có phi vật lý không | F1 | Π tại neo; σ² = ρ̄ r_f/C nên σ và nhiễu đếm không độc lập | K7–K9 như Phụ lục B |
| "Có ý nghĩa" là bao nhiêu | L1.5 | m = 8,1 ms (độ dốc cực đại E-model 0,1231 R/ms), r = 10% | Khoá trước F2 |
| Khoảng cách có tồn tại không | F2 (surrogate, 16 ô) | Mọi ô không đáng kể; P2 gap +0,358 ± 0,751 ms | Định hướng |
| Phép thử có lực không | f02b | 18/24 ô/biến thể có trần chặt < m; 1/24 kiểm được | Chỉ kiểm SESOI ở ô có trần ≥ m |
| Surrogate có đúng không | f04 (DES 1 link) | corr(DES, PSA) 0,607; R²(D ∣ ρ̂) DES 0,445 vs PSA 0,236 | PSA không làm bằng chứng gần bão hoà |
| Kết luận có sống qua DES không | f04b (4 ô, ghép cặp) | 8/8 không đáng kể; P2 DES gap +0,149 ± 0,400 ms | Luật 3 → PIVOT |
| Đủ seed không | F3 | 3 seed đủ cho ±m/2; 7 seed cho 100 sự kiện harm ở α = 1% | 8 seed test giữ nguyên |
| Chạy nổi không | F4 | 123 triệu gói/s; lưới 16 ô ≈ 0,07 CPU-giờ mô phỏng | GO về chi phí |
| Oracle có yếu không; tuổi dao động | f05 | max ∣Δgap∣ theo độ mịn 0,315 / 0,183 ms; mọi oracle đếm không đáng kể; A1 không đổi kết luận | Luật 1 → PIVOT vững trong phạm vi |
| Cơ chế | f05b (khám phá) | K2 ≠ SC ở 0,00–0,98% quyết định | "Vì sao" = H1 gần đúng |
| Gap literature | L1.9 (9 bài bắt buộc) | Không bài nào đo bất định vs ngưỡng tune với oracle | DP1 = NARROW |

## Phụ lục B — ADR đề xuất (ghi SAU họp, theo K23)

| ID | Đề xuất | Căn cứ |
|---|---|---|
| SESOI | Giữ m = 8,1 ms, r = 10% | L1.5; không đổi sau kết quả |
| K7 | 4 Mb/s, S = 3,024 ms; báo buffer theo K·S (ms), kèm thành phần luồng | F1; f02b (trần phụ thuộc K·S) |
| K8 | W = 0,5 s, H = 0,5 s, a = 0,05 s, lag TB 0,37 s; tuổi dao động (A1) làm chế độ chính, A0 là sensitivity | F1 đề xuất neo không đồng bộ; f05 |
| K9 | Lưới OU τ ∈ {2, 10} s, σ ∈ {0,03; 0,10} cho Phase 1; mở rộng sinh σ từ (C, r_f) nếu tiếp tục | F1 |
| K10 | Oracle chính: bin dọc quỹ đạo tham chiếu tĩnh, ≥ 20 bin, dữ liệu ×2; nested MC chỉ ở surrogate | F2 check; f05 |
| K11 | Engine: DES đầy đủ (Numba); PSA chỉ là surrogate định hướng | f04, f04b, F4 |
| K12 | 8 seed test × 1500 epoch cho phán quyết SESOI; ~300 seed nếu cần phân giải ±0,1 ms | F3 |
| K17 | Không chọn `self_gap_twin` (bị quy mô chi phối); dùng tỉ lệ bất đồng K2 ≠ SC + phần thuần làm thước đo cơ chế | F2 đính chính; f05b |
| K20 | Không có trace tải thật; X2 hoãn | F1 |
| K15 | Hỏi GVHD | — |
| DP0 / DP1 | PIVOT / NARROW | Mục 1 |

## Phụ lục C — Gate Phase 1 (trạng thái trung thực)

| Validity | Trạng thái |
|---|---|
| T1–T3 do tác giả viết; vấn đáp giữa kỳ có biên bản | Vấn đáp 13/10 — **chưa diễn ra** |
| mdk.py qua test | Đạt (64 passed) |
| Kiểm OU khớp Monte Carlo | Đạt (t02) |
| t03 khớp đáp án | Đạt; provenance ghi có hỗ trợ AI |
| SESOI khoá trước F2 | Đạt (504677e trước e2de7aa) |
| Mỗi spike có prereg trước outcome | Đạt từ F2; dự đoán f04b/f05 do AI soạn theo uỷ quyền (ghi trong log) |
| Surrogate qua đối chứng "không tuổi, không nhiễu → 0" | Đạt (F2 control) |
| Benchmark đúng máy; sai lệch PSA đo trên ≥ 1 ô | Đạt (F4; f04, f04b) |
| Hai cách tính oracle đối chiếu ≥ 1 cấu hình | Đạt ở surrogate (F2 check); DES chỉ đối chiếu độ mịn (câu hỏi 4) |
| Full text danh sách DP1-v2; forward citation | Full text đủ 9/9; forward citation **đang chạy** (openalex_l19) |
