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

## §3 Kết quả (outcome 423546f; code fffbe67; tiền đăng ký tag prereg-f7; §1, §2C commit 1cc9390 trước outcome)

> Provenance: Claude (AI) soạn diễn giải từ output đã commit; tác giả kiểm từng số. [F] fact · [I] suy luận · [H] giả thuyết.

**Hợp lệ.** Anchor tái lập f05c ở cả hai ô; validity đạt. Cổng lúc outcome: T10/F1, P2/F1, P2/FH đạt mọi cổng; **T10/FH
không đạt K2 − S0 ≥ −2SE** (−0,059 ± 0,037 ms, −3,1 SE; harm cal và ô thưa đạt). Theo cài đặt (5) commit trước khi chạy,
estimand dựa trên oracle của T10/FH không được diễn giải. M8 (i), M8 (ii), phép kiểm phụ và V đều dùng oracle T10/FH ⇒
**F8 không có kết luận xác nhận.** Script in "ĐẠT/KHÔNG ĐẠT" theo công thức; nhãn đúng theo quy tắc khoá là dưới đây.

| | Số in ra | Theo quy tắc khoá |
|---|---|---|
| M8 (i) Δ₁₀ | −0,004 ± 0,002 | không diễn giải (cổng T10/FH) |
| Δ_P2 (báo) | +0,020 ± 0,001 | hợp lệ (P2 đạt mọi cổng) |
| M8 (ii) Δ₁₀ − Δ_P2 | −0,024 ± 0,002 | không diễn giải |
| Phụ share_info FH − F1 (T10) | −8,84 ± 1,44 điểm % | không diễn giải |
| V (FH, T10) | −0,867 ± 0,039 ms | không diễn giải |

**Hợp lệ không cần oracle.** [F] Luật thấu thị trên quỹ đạo S0_FH ở T10 hơn S0_FH tối đa 6,84 ± 0,15 ms < m = 8,1 ms ⇒
VoIP tuyệt đối KHÔNG ĐÁNG KỂ ở T10/FH, không phụ thuộc oracle. [F] Báo kèm, không đăng ký: J(S0_F1) − J(S0_FH) = +2,60 ±
0,30 ms (T10), +2,74 ± 0,29 ms (P2) — lẫn thông tin với sửa tâm (§1). [F] P2: κ̂ 0,161 → 0,180, cùng chiều tham chiếu
(0,144 → 0,154), gấp đôi mức.

**Khám phá POST HOC (f08b; kế hoạch ghi trước khi chạy; danh sách phân tích đầy đủ trong log).**
1. [F] Cổng T10 nhạy với đặc tả oracle: qua bốn cách chia ô hợp lý, K2 − S0 ở T10/FH từ −0,120 đến +0,032 ms; cách cứu
   T10/FH lại phá T10/F1 và P2/FH. [I] Ở T10, oracle bin không có lợi thế hệ thống so với S0 khi twin có lịch sử; −3,1 SE
   chỉ phản ánh nhiễu theo seed, không phản ánh nhiễu đặc tả. Cơ chế "ô vuông trộn biên" không được ủng hộ.
2. [F] κ̂ bền qua năm cách dựng oracle (E0–E4): Δ₁₀ ∈ [−0,004; +0,007]; Δ_P2 ≈ +0,02 ⇒ nhất quán với ô (D) của §2C, dưới
   nhãn khám phá.
3. [F] Quỹ đạo chung (E4): share_info T10 82,5% → 58,0% (−24,5 ± 1,6 điểm %). [I] Lịch sử mang nhiều thông tin; trên quỹ
   đạo riêng, S0_FH đã thu hoạch một phần (headroom 10,67 → 8,08 ms) nên −8,8 điểm % đánh giá thấp lợi ích.
4. [F] Biết hoàn hảo tải khoảng giữ chỉ cho ρ_s²(G, D) = 0,270 (T10), 0,484 (P2), thấp hơn tâm Kalman từ lịch sử (0,293;
   0,573). [I] Delay DES phụ thuộc trạng thái thừa kế (backlog), không chỉ tải khoảng giữ. [H] t06/t07 dự báo sai biến
   trạng thái, nên dự đoán thay đổi κ không chuyển sang DES ở σ nhỏ (cùng mẫu với F7: path B mô hình 0,217, DES 0,14).

**Giới hạn.** Hai thế giới; một điểm vận hành; oracle bin (chính là thứ hỏng); twin biết (ρ̄, σ, τ); Kalman tối ưu cho
tải, không cho delay; share_info so trên hai quỹ đạo khác nhau (thiết kế tiền đăng ký).

## §4 So với dự đoán; đề xuất cho DP0/DP1 (GVHD quyết 20/10)

**Đối chiếu (số in ra; nhãn khám phá ở T10).** (a) Tham chiếu t07: T10 κ 0,171 → 0,297 — sai trong DES (0,147 → 0,143);
P2 0,144 → 0,154 — đúng chiều. (b) Tác giả: "κ tăng rõ ở τ = 10 s" sai; "tăng rất ít ở P2" gần đúng; "Δ₁₀ > Δ_P2" sai;
"share_info giảm ở τ = 10 s" đúng chiều (mạnh hơn trên quỹ đạo chung); "V chưa đạt" đúng.

**Đề xuất.**
- Báo F8 là "không kết luận xác nhận do công cụ oracle hỏng ở ô chính"; không nâng số khám phá thành xác nhận.
- Claim âm được củng cố ở mức khám phá: lịch sử tăng mạnh thông tin (share_info −24,5 điểm % trên quỹ đạo chung; J(S0)
  −2,6 ms) nhưng không tăng κ̂ và không tạo phần thuần (T10/FH thuần −0,017 ± 0,015). Giá trị đi qua tâm và thông tin,
  không qua độ rộng — cùng thông điệp F7 §4.
- Phương pháp: oracle bin chỉ là cận trên cho luật đo được theo phân hoạch của nó. Đây là lần thứ ba (v1: P1, FZ10x5; F8:
  T10/FH) ⇒ Phase 2 bắt buộc kiểm K2 − S0 trên seed oracle GIỮ RIÊNG trong validity, trước outcome, và báo độ nhạy theo
  đặc tả oracle.
- Giả thuyết Phase 2 (từ f08b F): trạng thái đúng của twin là (backlog, tải); nối T5 §5 và oracle Q của f05. Cần tiền
  đăng ký mới trên seed mới.
