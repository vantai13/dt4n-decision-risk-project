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
