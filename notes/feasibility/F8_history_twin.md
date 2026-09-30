# F8 — Twin có lịch sử (Kalman)

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
  **Dự đoán của tác giả:** [em viết trước commit khoá].
- **Phép kiểm M8 (chính):** (i) cận dưới CI của Δ₁₀ = κ̂(FH) − κ̂(F1) ở τ = 10 s > 0; (ii) tương tác: cận dưới CI của
  Δ₁₀ − Δ_P2 > 0 (hiệu theo seed, ghép theo chỉ số seed). Phụ: share_info(FH) < share_info(F1) ở τ = 10 s.
  V giữ r = 10% trên (K2 − S0)/headroom.
- **Seed:** calibration 11001–11008, test 11011–11100, oracle 11101–11697, khoá luồng 730. Neo: F1 trên seed f04b khoá 713
  tái lập f05c K100_r0.95_s03t10/A0 (và khoá 711 cho P2) đến chữ số in ra.
