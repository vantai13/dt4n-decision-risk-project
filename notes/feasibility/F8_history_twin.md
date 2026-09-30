# F8 — Twin có lịch sử (Kalman)

## §1 Kalman AR(1) so với hiệp phương sai chính xác; kiểm thao tác (validity, TRƯỚC outcome)

> Nguồn: `experiments/results/f08_validity_output.txt`. Provenance: Claude (AI) soạn; tác giả kiểm từng số với output.
> Nhãn [F] fact · [I] suy luận · [H] giả thuyết.

**Bộ lọc.** τ = 10 s: φ = 0,951; R/V(W) = 6,49; K = 0,080; a = φ(1 − K) = 0,875 — nhớ ~8 cửa sổ (4 s). P2: φ = 0,779;
R/V(W) = 0,62; K = 0,480; a = 0,405 — nhớ ~1,7 cửa sổ.

**Lệch AR(1) so với t06 (yêu cầu của §2B).** [F] AR(1) đoán sai tương quan lag-1 của trung bình cửa sổ (0,951 so với
0,967 thật ở τ = 10 s; 0,779 so với 0,849 ở P2), nhưng R² dưới hiệp phương sai chính xác gần như không mất: 0,408 so với
dự báo tuyến tính tốt nhất 0,408 (τ = 10 s); 0,322 so với 0,322, mất 0,0005 (P2). [I] Cực đại phẳng (cùng nguyên lý T4
§3). Hệ số dự báo e^(−g/τ) lệch tối ưu ×0,958 và ×0,822: làm MSE tệ đi (P2: 0,307) nhưng KHÔNG ảnh hưởng oracle bin
(bất biến với phép co chung — `test_oracle_invariant_to_common_rescaling_of_centers`); chỉ vào S0 qua độ cong của T.
Chuỗi OU dài (seed 11941) khớp giải tích: 0,401 ± 0,007 và 0,318 ± 0,003.

**Kiểm thao tác trên cal (báo, không cổng).** [F] Spearman²(tâm, D): τ = 10 s 0,132 → 0,293; P2 0,430 → 0,573.
Pearson² trên Ĉ tăng mạnh hơn nhiều (0,143 → 0,628; 0,388 → 0,619). [I] Phần chênh là sửa tâm, không phải thông tin:
plug-in méo qua T lồi sát knee — S0_F1 phải đặt ngưỡng 256 ms (τ = 10 s) và 259 ms (P2), S0_FH chỉ 6,3 ms (abs, τ =
10 s). Vì vậy J(S0_F1) − J(S0_FH) chỉ báo kèm, không đăng ký.

**Phát hiện trước outcome: bộ nhớ hàng đợi.** [F] Quét độ nhớ a của bộ làm trơn mũ trên cal: a tốt nhất cho D là 0,80
(τ = 10 s; Kalman 0,875; 0,305 so với 0,293) và 0,60 (P2; Kalman 0,405; 0,625 so với 0,573). [I] Ở P2, delay nhớ tải lâu
hơn tải tự nhớ — backlog tích luỹ — nên lịch sử có giá trị cho D mà mô hình tải t06/t07 (không bộ nhớ hàng đợi) không
thấy. [H] Đối chứng P2 có thể không "âm" trong DES: Δ_P2 > 0 và M8(ii) không đạt KHÔNG tự động nghĩa là artefact. Không đổi
phép kiểm; chỉ đổi cách đọc (§2C). Ứng viên Phase 2: twin ước lượng backlog (nối T5 §5).

**Mối đe doạ đã biết.** (1) Quỹ đạo tham chiếu khác nhau giữa F1 (S0 gần như không đổi đường) và FH ⇒ Δ lẫn hiệu ứng
chọn lọc quỹ đạo; P2 kiểm một phần; kiểm sạch cần f08b POST HOC (hai oracle trên cùng quỹ đạo). (2) Twin biết (ρ̄, σ, τ).
(3) Kalman tối ưu cho tải, không cho delay. (4) P2 khác τ = 10 s ở cả σ, τ và R/V ⇒ (ii) là "thế giới lý thuyết dự đoán
ít lợi", không phải OFAT theo τ.

## §2B Tiền đăng ký (chốt với GVHD 2026-09-30; khoá cùng commit với F7 §2 v2; CHỈ chạy sau khi outcome F7 đã commit,
## trước trưa 17/10; nếu không kịp: chuyển Phase 2, khoá vẫn giữ hiệu lực)

- **Câu hỏi:** Khi MỌI luật và oracle dùng lịch sử số đo (Kalman từng path), κ̂ có tăng ở τ = 10 s như T5/t07 dự đoán,
  gần như không đổi ở τ = 2 s, và khoảng thông tin có thu hẹp không?
- **Thế giới** (DES f04b, A0): K100/0,95/0,03/10 (= ô f04b K100_r0.95_s03t10) và P2 (τ = 2 s, đối chứng âm). Hai điều
  kiện telemetry trên CÙNG quỹ đạo DES: F1 = một cửa sổ (= f04b) · FH = Kalman trên chuỗi cửa sổ 0,5 s.
- **Kalman:** AR(1) cho trung bình cửa sổ với φ = e^(−W/τ), nhiễu đo R = ρ̄S/W, trạng thái dừng; dự báo tới khoảng giữ
  bằng hệ số e^(−g/τ). Là xấp xỉ (trung bình cửa sổ của OU là ARMA(1,1)); lệch so với hiệp phương sai chính xác của t06
  ghi vào F8 §1 trước outcome.
- **Luật và oracle:** S0 trên T(m̂_cur) − T(m̂_alt), tune theo J; SC; K2(α), K2(∞); oracle bin (m̂_cur, m̂_alt) 20 × 20,
  597 seed. Knowledge parity: FH cho MỌI luật, không chỉ cho oracle.
- **Estimand:** κ̂ (D4; theo seed và gộp); phân rã năm bậc; share_info; share_pure.
- **Dự đoán tham chiếu** (t07 Bảng 3, mô hình): κ 0,171 → 0,297 ở τ = 10 s; 0,144 → 0,154 ở P2.
  **Dự đoán của tác giả:** Tôi dự đoán dùng lịch sử/Kalman sẽ làm κ tăng rõ ở thế giới τ = 10 s, nhưng chỉ tăng rất ít
  ở P2 với τ = 2 s, vì khi tải biến đổi chậm thì các cửa sổ quá khứ còn mang nhiều thông tin, còn khi τ ngắn thì thông tin
  cũ nhanh mất giá trị. Tôi kỳ vọng Δ₁₀ > Δ_P2 và share_info giảm ở τ = 10 s. Tôi chưa kỳ vọng chắc rằng V sẽ đạt 10%,
  vì κ tăng chưa đủ; f₀ và mức phạt harm vẫn có thể giữ giá trị thích nghi nhỏ.
- **Phép kiểm M8 (chính):** (i) cận dưới CI của Δ₁₀ = κ̂(FH) − κ̂(F1) ở τ = 10 s > 0; (ii) tương tác: cận dưới CI của
  Δ₁₀ − Δ_P2 > 0 (hiệu theo seed, ghép theo chỉ số seed). Phụ: share_info(FH) < share_info(F1) ở τ = 10 s.
  V giữ r = 10% trên (K2 − S0)/headroom.
- **Seed:** calibration 11001–11008, test 11011–11100, oracle 11101–11697, khoá luồng 730. Neo: F1 trên seed f04b khoá 713
  tái lập f05c K100_r0.95_s03t10/A0 (và khoá 711 cho P2) đến chữ số in ra.

## §2C Bảng diễn giải (bổ sung sau validity, TRƯỚC outcome; không đổi câu hỏi, estimand, phép kiểm, tiêu chí, seed của §2B)

> Provenance: Claude (AI) soạn sau khi thấy validity (chỉ calibration + oracle); tác giả duyệt. Không chứa dự đoán mới —
> dự đoán của tác giả vẫn là dòng trong §2B.

| | M8(ii) đạt | M8(ii) không đạt |
|---|---|---|
| **M8(i) đạt** | (A) Lịch sử tăng bất định trực giao, đặc hiệu cho thế giới nhiễu lớn / nhớ dài ⇒ T5 §4(iii) xác nhận trên DES | (B) κ tăng ở cả hai thế giới; nếu Δ_P2 > 0 rõ: cơ chế có nhưng không đặc hiệu — ứng viên bộ nhớ hàng đợi (§1); không gọi artefact khi chưa có f08b |
| **M8(i) không đạt** | (C) Chỉ xảy ra khi Δ_P2 < 0 rõ ⇒ kiểm sàn D6 và quỹ đạo trước khi đọc | (D) Lịch sử không tăng κ trong DES ⇒ T5 §4(iii) sai ở DES; sửa T5 |

Cắt ngang: V đạt ⇒ độ rộng có giá trị thực dụng khi twin có lịch sử — đổi khuyến nghị DP0. V không đạt ⇒ claim âm (độ
rộng bậc hai, nhỏ) đứng vững cả khi twin có lịch sử. Phụ đạt (share_info giảm) ⇒ lịch sử là nơi có giá trị.
