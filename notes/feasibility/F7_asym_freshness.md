# F7 — Độ tươi bất đối xứng

> §1 soạn ở L1.6 (2026-09-29); §2 (tiền đăng ký) ở L1.7; §3–4 (kết quả, quyết định) ở L1.8.

## §1 Hiệu chỉnh từ dữ liệu cũ (POST HOC)

> KHÁM PHÁ trên seed cũ của f05, định nghĩa D1–D11 khoá trong log trước khi tính (AI ghi 01:14Z, trước khi chạy).
> Không đổi F6. Provenance: Claude (AI) soạn `f05c` và diễn giải; tác giả chạy lại, kiểm. Mọi phân tích đã thử đều ở
> `experiments/results/f05c_kappa_des_output.txt` (không có phân tích bị bỏ).

- **Đối chứng:** tái lập chính xác f05 F20x2 (thuần, λ, H) ở P2 và K100/0,95/0,03/10, A0 và A1; thế giới A0 = f04b.
- **κ thật:** κ̂_pure = P1 0,036; P2 0,165; K100/0,85 0,271; K100/0,95/0,03/10 0,151 (A1 ≈ A0); sàn ≤ 0,037. `t07` (không
  DES) đoán 0,131 / 0,273 / 0,166 → nguyên lý mức tải × độ cong (T5 §4) sống sót qua DES ở đối chứng (±26%).
- **Luật bậc hai:** dự đoán 0,000–0,060 ms nằm trong CI quan sát ở 6/6 chế độ → không mâu thuẫn; không phân giải
  (CI ±0,11–0,14 ms ở 8 seed; cần ~82–89 seed để CI ±0,03 ms).
- **Cơ chế:** biên t₀ ở ~phân vị 95 của Ī trên quỹ đạo tham chiếu (P(Ī > t₀) = 4,9%; P2: sd Ī 76 ms, trung vị −64 ms) ⇒
  f₀ = 0,001–0,007/ms (toy 0,198), bù một phần bởi λ = 51–151 (β lớn). Dải biên 3–14 ô oracle ⇒ a′, β chỉ là bậc độ lớn.
- **Đường (ii):** a′ < 1 ở 3/5 ô λ > 0; u TB không đơn điệu ở P2 (5 lần giảm) — nhưng nhiễu p− × λ (~2 ms) đủ giải thích.
  Chưa kết luận.
- **Tâm vs quy trình:** K100/0,85: tâm f05 0,076 = sạch 0,008 + quy trình 0,068 ± 0,053; P2/A1: 0,558 là tâm sạch.
- **Dùng cho §2:** κ_pred lấy từ `t07`; đăng ký chiều giảm của κ̂ theo T_probe; không đăng ký chiều gap thuần (f₀ có thể
  tăng khi alt cũ); tỉ lệ dự đoán dạng khoảng; S0age báo hai bản (tune như SC, và theo J); power cho gap thuần.

## §2 Tiền đăng ký (BẢN NHÁP — chưa khoá; khoá sau buổi 13/10 theo biên bản)

> Soạn 2026-09-29 (L1.7), trước mọi code và output của f07. Provenance: Claude (AI) soạn từ T4–T5, t07, t08 và hiệu
> chỉnh DES/t07 = 0,91–1,26 của f05c; tác giả và GVHD duyệt. Phán quyết VoIP của F6 giữ nguyên, báo kèm.

### 2.0 Cơ chế (GVHD chọn ngày 13/10)
- **F7b (đề xuất chính):** hai path cùng delay TB, khác rủi ro — đúng câu hỏi 2 của F6; t08 dự đoán κ lớn nhất đã thấy.
- **F7a (phụ, thu gọn):** độ tươi bất đối xứng — t07 dự đoán κ GIẢM; phép thử chiều của T5 §4.

### 2.1 Câu hỏi
F7b: Khi hai path cùng delay TB nhưng khác rủi ro, κ có lớn như t08 dự đoán, và luật dùng độ rộng vượt ngưỡng tĩnh —
kể cả ngưỡng theo chiều — bao nhiêu? F7a: Khi path thay thế được đo thưa hơn, κ̂ có giảm như T5 §4 dự đoán không?

### 2.2 Thế giới (DES, 4 Mb/s, telemetry như f04b A0)
F7b: W0 đối chứng A = B = K100/0,95/0,10/2 (= P2); W1 A = K100/0,85/0,10/2, B = K100/0,931/0,03/10 (E[T] khớp
30,6 ms theo t08); W2 A = K100/0,95/0,10/2, B = K100/0,979/0,03/10 (E[T] khớp 98,9 ms). Báo delay TB thật trong DES.
F7a: P2 × T_probe ∈ {0,5 đồng pha (= f04b), 4τ}; mở rộng 3 ô × {0,5 đồng pha, 0,5 ngẫu nhiên, τ, 4τ} nếu kịp.

### 2.3 Luật (cùng F, cùng α = 1%, tune trên seed calibration)
S0 (abs/rel, tune theo J) · S0dir (ngưỡng theo chiều, tune theo J) · SC (Ī > H, harm dự đoán) · SCdir (ngưỡng trên Ī
theo chiều, tune như SC) · K2(α) · K2(∞). Oracle bin (ρ̂_cur, ρ̂_alt, chiều) 20×20×2. F7a: chiều → tuổi alt (20×20×5),
S0 → S0age (tâm theo tuổi, hai bản: tune như SC và theo J).

### 2.4 Estimand
Chính (cơ chế): κ̂_pure theo seed (định nghĩa D4 của L1.6) và κ̂_dir (trong từng chiều), kèm CI.
Phụ: gap thuần (ms) K2 − SC và K2 − SCdir; tâm theo chiều SCdir − SC; share_pure; share_adapt = (K2 − S0dir)/headroom.
Báo kèm, không quyết định: phán quyết VoIP (m = 8,1 ms, r = 10%), share_info, share_safety, delay TB từng path.

### 2.5 Dự đoán (t08 × [0,9; 1,3])
κ̂_pure: W0 0,13–0,19 · W1 0,32–0,46 · W2 0,13–0,19. κ̂_dir: W1 0,20–0,28 · W2 0,09–0,13. Thứ tự W1 > W0 ≈ W2.
share_pure < 5% ở mọi thế giới; K2 − SCdir < K2 − SC ở W1. Kết cục nhiều khả năng nhất: ô (ii) của 2.7.
F7a (t07): κ̂ giảm theo T_probe; P2 0,131 → 0,068 ở 4τ (×[0,9; 1,3]).

### 2.6 Phép kiểm
- **M (cơ chế, chính):** F7b — κ̂(W1) − κ̂(W0) > 0 và κ̂(W1) − κ̂_dir(W1) > 0, CI95 theo seed không chứa 0.
  F7a — hiệu ghép cặp κ̂(0,5 đồng pha) − κ̂(4τ) > 0.
- **L (luật bậc hai, MÔ TẢ):** báo dự đoán f₀β²κ_b²/(2a′) (D7 của L1.6) và quan sát (ms); không có tiêu chí đạt/rớt vì
  ≤ 3 thế giới và độ phân giải ±0,1 ms ở 8 seed — trừ khi GVHD duyệt mở rộng power (2.8).
- **V (thực dụng):** cận dưới CI95 của share_adapt ≥ 10% ở ít nhất một thế giới.
- **Validity (trước outcome):** W0 chạy bằng seed cũ f04b tái lập f05 P2/A0 F20x2 (thuần, λ, H); oracle − S0dir ≥ −2SE;
  harm ≤ α trên calibration; policy không đọc nhãn, probe, tải thật; tỉ lệ ô thưa < 1%.

### 2.7 Bảng diễn giải (viết trước để mọi kết cục đã có nghĩa)
| | share_adapt ≥ 10% | share_adapt < 10% |
|---|---|---|
| **M đạt** | (i) Rủi ro bất đối xứng tạo giá trị → GO bản đồ cơ chế | (ii) κ lớn, giá trị nhỏ → bậc hai + biên đuôi chi phối; kết quả âm vững ở cơ chế thuận lợi nhất |
| **M không đạt** | (iv) Mâu thuẫn → tìm bug, không kết luận | (iii) t08/T5 sai trong DES (bộ nhớ hàng đợi?) → phát hiện lý thuyết, so PSA ↔ DES |

### 2.8 Seed
Calibration 11001–11008 · test 11011–11018 · oracle 11101–11697 (×3 dữ liệu vì thêm một chiều bin) · validity: seed cũ
f04b. Mở rộng power (cần GVHD duyệt): test 11011–11100 (90 seed; L1.6: 82–89 seed cho CI ±0,03 ms).

### 2.9 Khi chưa kết luận
Chỉ thêm seed test theo power trong 11019–11100; không đổi thế giới, luật, estimand hay tiêu chí.
