# T5 — Nguồn bất định trực giao trong mạng và giá trị của lịch sử

> Ngày 2026-09-29 (P1v2/L1.5). Provenance: Claude (AI) soạn phép dẫn, `t06`, `t07` và diễn giải; tác giả chạy lại, kiểm,
> chịu trách nhiệm. Mô hình tải → đường sojourn dừng (không bộ nhớ hàng đợi): chỉ báo bậc độ lớn và CHIỀU, không phải
> bằng chứng DES. Không đổi F6 hay tiền đăng ký nào. κ theo nghĩa κ_Ī detrend của T4 §2.

## 1. Hậu nghiệm một path theo tuổi (mở rộng T2 §6)

G = tải TB khoảng giữ; y = số đo cửa sổ (nhiễu R = ρ̄S/W); g = cuối cửa sổ → đầu khoảng giữ = lag + tuổi thêm + a.
c(g) = σ²A(W)A(H)e^(−g/τ); E[G|y] = μ + b(y − μ), b = c/(V(W) + R); Var(G|y) = V(H)(1 − q), q = c²/(V(H)(V(W) + R)).
Tuổi thêm Δ: q(Δ) = q_fresh·e^(−2Δ/τ). q một cửa sổ: P1 0,126; K100/0,95/0,03/10 0,115; P2 0,292 (tắt nhiễu: 0,86;
0,86; 0,47). R/V(W) = 5,8; 6,5; 0,62. Tuổi chỉ dịch Var trong [V(H)(1 − q_fresh), V(H)].

## 2. Lịch sử và Kalman (`t06`)

R² theo số cửa sổ 1/2/5/10/20: P1 0,126/0,211/0,340/0,405/0,423; K100/0,95/0,03/10 0,115/…/0,406; P2 0,292/…/0,322
(lưới và công thức đóng khớp, lệch đáp án ≤ 0,0004). τ = 10 s: trung bình nhiều cửa sổ triệt nhiễu đếm (×3,4); τ = 2 s:
cửa sổ cũ đã bị quên. Tuyến tính–Gauss ⇒ trung bình hậu nghiệm là thống kê đủ; phương sai dừng hằng (Riccati).
Kết luận "khoảng thông tin chiếm ưu thế" (F6) phải kèm "với telemetry một cửa sổ".

## 3. Không dùng delta method gần knee

Delta method (T′ tại tâm) sai cả mức s (K100/0,85: TB 18,6 ms so với 69,9 ms) lẫn κ. Cách chính: cầu phương
Gauss–Hermite 40 nút cho Ī = E T(G_cur) − E T(G_alt), s² = Var T(G_cur) + Var T(G_alt). Đối chứng với sd_log_s_cond của
F2 (surrogate): cầu phương/F2 = 1,21; 1,18; 1,22 — delta/F2 = 4,31; 1,76; 1,80.

## 4. Nguyên lý: κ = độ cong × độ giàu thông tin trên hai chiều

Cùng Ī, cặp (m_cur, m_alt) có thể ở vùng tải vừa (đường cong thoải, s nhỏ) hoặc sát knee (dốc, s lớn) ⇒ s khác nhau ở
cùng Ī: κ loại (a) của T4 §1, là nguồn chính. Cần: hai chiều có thông tin; độ cong; tâm hậu nghiệm trải rộng (q lớn).
Hệ quả: (i) alt đo thưa ⇒ niềm tin về alt co về μ ở mọi epoch ⇒ sụp một chiều ⇒ κ giảm; alt cũ vô hạn ⇒ s là hàm của
m_cur ⇒ κ → 0 (T4 Mệnh đề 1). (ii) Phân tán tuổi thêm một chiều (+) nhưng nhỏ hơn (i). (iii) Thêm thông tin (lịch sử,
ít nhiễu) ⇒ κ tăng.

| Ô (κ_lin, nhiễu bật) | 0,5 s | τ | 4τ | ∞ | phân tán (4τ) | sụp chiều (4τ) |
|---|---:|---:|---:|---:|---:|---:|
| P2 | 0,131 | 0,110 | 0,068 | 0,001 | +0,043 | −0,106 |
| K100/0,85/0,10/2 | 0,273 | 0,238 | 0,155 | 0,002 | +0,088 | −0,206 |
| K100/0,95/0,03/10 | 0,166 | 0,134 | 0,081 | 0,000 | +0,046 | −0,131 |

κ theo q (đối chứng): K100/0,95/0,03/10 từ 0,171 (1 cửa sổ) lên 0,297 (20 cửa sổ) và 0,401 (tắt nhiễu); P2 0,144 →
0,154 → 0,198. Refresh sau lần đổi nâng κ ở 4τ thêm 0,015–0,034. Giả thuyết cho paper: probe path thay thế càng thưa,
bất định quyết định càng đồng đều, ngưỡng tĩnh càng đủ; giá trị của probe dày nằm ở thông tin (tâm), không ở độ rộng.

## 5. Dự đoán định tính (Phase 2, giả thuyết)

Stall chung pipeline: hai chiều cùng sụp, epoch stall xa biên ⇒ κ thấp; tác hại ở tâm của luật cắm số. Path khác loại:
danh tính path là Z rời rạc ⇒ κ cao so với một ngưỡng, bị ngưỡng theo chiều hấp thụ. Tải chuyển chế độ: vấn đề sai mô
hình (RQ2), rủi ro harm > α. Telemetry hàng đợi: q cao nhưng f05 cho thuần 0,018 ± 0,054 ms — nguyên lý không chuyển
sang Q; câu hỏi mở.

## 6. Đối chiếu dự đoán ghi trước `t07`

Đúng: nguồn chính ở đối chứng là mức tải; tắt nhiễu nâng κ mạnh nhất ở ô σ 0,03. Sai: "trần ½log(1/(1 − q))" cho phần
tuổi (bỏ kênh tâm co về μ); bỏ sót kênh sụp chiều (chi phối). Dự đoán của plan "ở 4τ, σ 0,10 > σ 0,03" sai với P2.

## 7. Đề xuất cho L1.7 (chưa hiệu lực, cần GVHD)

κ_pred tính bằng cầu phương, bin theo tâm, detrend. F7: (A) giữ, đăng ký chiều "κ̂ và K2 − SC giảm theo T_probe";
(B) nâng F8 lên ưu tiên (cơ chế duy nhất dự đoán κ tăng); (C) tuỳ chọn nhánh tắt nhiễu đếm. Sửa phép kiểm M: bỏ điều
kiện "σ 0,10 > σ 0,03 ở 4τ"; thay bằng thứ tự do κ_pred cầu phương cho.

## Đính chính 2026-09-29 (t08, trước mọi output F7)

§5 "path khác loại" sai một nửa. Khi delay TB hai path khác xa (Ī tách theo chiều, ±87 ms), κ chỉ 0,015–0,029: path ổn
định góp gần hằng ⇒ sụp chiều như §4(i). Khi delay TB khớp nhưng khác độ biến động (khác rủi ro thật), κ so với một
ngưỡng là 0,351 (K100/0,85/0,10/2 ↔ K100/0,931/0,03/10) và 0,142 (sát knee); ngưỡng theo chiều còn 0,219 và 0,100.
Nguyên lý §4 giữ nguyên, làm rõ: κ cần hai chiều thông tin CẠNH TRANH nhau quanh biên.
