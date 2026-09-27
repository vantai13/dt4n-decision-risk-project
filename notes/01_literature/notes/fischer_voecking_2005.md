# Fischer & Vöcking 2005/2009 — Định tuyến thích nghi với thông tin cũ

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | Adaptive Routing with Stale Information |
| Tác giả (đúng thứ tự của PHIÊN BẢN đang đọc) | Simon Fischer; Berthold Vöcking (RWTH Aachen) |
| Nguồn | Technical report AIB-2005-06 (04/2005); PODC 2005, tr. 276–283; Theoretical Computer Science 410(36):3357–3371, 2009, doi:10.1016/j.tcs.2008.01.055 |
| Trạng thái | peer-reviewed (PODC 2005; TCS 2009). **Bản đã đọc: TR 2005** — chưa đối chiếu bản TCS 2009 |
| Lượt đã đọc | 2 — §1–4 của TR; chứng minh Lemma 1, Thm 1, Thm 3 đọc lướt |
| Ngày đọc | 2026-09-27 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | thấp cho RQ1 (khác chế độ); cao cho mọi claim "thông tin cũ làm luật tham lam hỏng/dao động" — không được claim |

Nhãn: [F] paper nói trực tiếp (có §/tr.) · [I] suy ra (ghi suy từ đâu) · [?] chưa kiểm

## 0. Five Cs (sau lượt 1)

- Category: lý thuyết (hệ động lực, lý thuyết trò chơi tiến hoá).
- Context: cân bằng Wardrop, hàm thế Rosenthal, mô hình bảng tin của Mitzenmacher (§1, §2).
- Correctness: fluid limit, vô số agent vô cùng nhỏ, hàm latency không giảm có đạo hàm bị chặn (§1.1).
- Contributions (theo tác giả, §1.4): best/better response dao động với mọi chu kỳ cập nhật; luật α-smooth hội tụ nếu
  T ≤ 1/(4Lαβ); điều kiện gần chặt; cận tốc độ hội tụ.
- Clarity: tốt.
- Quyết định: lượt 2 đủ cho RQ1.

## 1. Một câu: paper làm gì?

Trong mô hình nhiều agent với bảng tin cập nhật mỗi T, luật "đổi sang đường tốt hơn" dao động với mọi T, còn luật đổi
mềm (xác suất đổi ≤ α × chênh latency) hội tụ về cân bằng Wardrop nếu T đủ nhỏ so với 1/(Lαβ).

## 2. Problem · Assumptions

- Problem [F §1.1]: đồ thị với hàm latency trên cạnh; traffic chia cho vô số agent; mục tiêu là hội tụ về cân bằng.
- A1 [F §1.1]: hàm latency liên tục, không giảm, đạo hàm bị chặn bởi β.
- A2 [F §1.2]: agent xét lại đường theo Poisson; lấy mẫu đường q với xác suất σ_pq, đổi với xác suất μ(ℓ_p, ℓ_q).
- A3 [F §1.3]: thông tin cũ = bảng tin cập nhật mỗi T; agent không biết tuổi thông tin (§1.5).

## 3. Method

Dùng hàm thế Rosenthal làm hàm Lyapunov. Lemma 1: nếu T ≤ 1/(4Lαβ), mức giảm thế thật trong một pha ít nhất bằng một
nửa mức giảm "nhìn thấy" từ thông tin cũ — sai số do thông tin cũ không đủ để đảo chiều tiến bộ. Thm 1 suy ra hội tụ.
Thm 3 dựng một mạng hai đường mà luật α-smooth dao động khi T > 8/(αβL).

## 4. Evaluation

| Setup (topology/testbed/data) | Baseline | Metric | Kết quả chính (có số) | §/tr. |
|---|---|---|---|---|
| Lý thuyết; ví dụ hai link ℓ₁ = c, ℓ₂ = x^d | best/better response | hội tụ / dao động | best response dao động với mọi T | §2 |
| Mạng tổng quát | luật α-smooth | hội tụ về Wardrop | hội tụ nếu T ≤ 1/(4Lαβ) | Lemma 1, Thm 1 |
| Mạng hai đường dựng riêng | luật α-smooth | dao động | dao động nếu T > 8/(αβL) | Thm 3 |

## 5. Claim ↔ Evidence

| # | Claim của tác giả | Loại evidence | Evidence thật sự phủ tới đâu | Khe hở? | §/tr. |
|---|---|---|---|---|---|
| 1 | Best/better response dao động với mọi T | ví dụ + chứng minh | Mạng hai link | Không | §1.4, §2 |
| 2 | Luật α-smooth hội tụ nếu T đủ nhỏ | định lý | Mọi mạng thoả A1–A3 | Không | Lemma 1, Thm 1 |
| 3 | Tính trơn là điều kiện cốt yếu | định lý | Một mạng dựng riêng | Không | Thm 3 |
| 4 | Cận số pha chưa cân bằng | chứng minh phác | Hai biến thể lấy mẫu | Chứng minh phác | Thm 4–5 |

## 6. Limitation

- Tác giả tự nêu [F]: mô hình thuần lý thuyết, cố ý đơn giản (§1.3); agent không biết tuổi thông tin (§1.5).
- Tôi thấy [I]: tải nội sinh (tập thể); không nhiễu đo; không phân tích hysteresis dạng ngưỡng có vùng chết.

## 7. So với đề tài của tôi

- Trùng: thông tin cũ; quyết định đổi; better response = "đổi khi Î > 0".
- Khác, ĐÃ KIỂM (§/tr.): tải nội sinh tập thể (§1.1–1.2), mục tiêu hội tụ về cân bằng; đề tài: một luồng nhỏ, tải ngoại
  sinh (brief §9), mục tiêu gain delay của một luồng.
- Khác, CHƯA KIỂM / suy luận: hysteresis ngưỡng H > 0 là hàm bậc thang — không α-smooth theo §1.2, nên lý thuyết này
  không trực tiếp nói gì về nó [I]. Nếu nhiều luồng cùng dùng một luật trên cùng telemetry, hiệu ứng dồn đàn quay lại
  và kết luận "ngưỡng tĩnh đủ" có thể sai — giới hạn phạm vi phải ghi [I].
- Dùng được: câu Related Work cho giới hạn phạm vi; lý do đề tài không xét dao động tập thể; nguồn về mô hình bảng tin.

## 8. Câu định vị

"Fischer–Vöcking chứng minh rằng trong định tuyến tập thể với thông tin cũ, hình thức của luật đổi quyết định hội tụ
hay dao động (Thm 1, Thm 3); đề tài xét chế độ bổ sung — một luồng nhỏ trên tải ngoại sinh, không có phản hồi tập thể —
và cho thấy ở đó hình thức luật (ngưỡng tĩnh hay dùng bất định) gần như không đổi kết quả trong miền đã thử, còn chất
lượng thông tin thì có."

## 9. Câu hỏi còn mở

- Đối chiếu bản TCS 2009 xem định lý có đổi so với TR không.
- Forward citation (L1.9 phần 2): tìm bài xét hysteresis có vùng chết dưới thông tin cũ.
