# Veeravalli & Kelly 1997 — Luật handoff "locally optimal" so với hysteresis

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | A Locally Optimal Handoff Algorithm for Cellular Communications |
| Tác giả | Venugopal V. Veeravalli; Owen E. Kelly |
| Nguồn | IEEE Trans. Veh. Technol. 46(3):603–609, 08/1997 — PDF trên trang tác giả (vvv.ece.illinois.edu) |
| Trạng thái | peer-reviewed; bản sớm ở PIMRC 1995 |
| Lượt đã đọc | 2 — toàn văn §I–VI + Phụ lục (chứng minh Thm 1). Ký hiệu công thức bị mất khi trích xuất PDF; đọc theo lời văn |
| Ngày đọc | 2026-09-30 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | CAO cho "so luật dùng xác suất với luật tĩnh đã tune, cùng dự báo, cùng ngân sách" và cho H3 cũ. THẤP–TB cho tách kênh độ rộng khi κ > 0 |

Nhãn: [F] · [I] · [?]. Thư mục: nguồn thứ cấp ghi trang 351–356 là SAI; header PDF ghi trang 603.

## 0. Five Cs
- Category: lý thuyết (DP) + thuật toán + mô phỏng.
- Context: handoff theo cường độ tín hiệu; hysteresis ad hoc; hysteresis + ngưỡng tuyệt đối (Zhang–Holtzman, VTC 1994) (§I).
- Correctness: shadow fading log-normal, tương quan không gian AR(1) (Gudmundson); tín hiệu đã lọc thông thấp; hai trạm (§II).
- Contributions (§I, §VI): tiêu chí chất lượng nhị phân (service failure); tương đương biến phân–Bayes (Thm 1); DP làm
  mốc; luật LO một ngưỡng; so sánh kiểu ROC.
- Quyết định: lượt 2 đủ; lượt 3 §IV–V khi viết Related Work.

## 1. Một câu
Cân bằng số lần tín hiệu rơi dưới ngưỡng phục vụ với số lần handoff; DP cho mốc tối ưu; luật LO so xác suất rơi dưới
ngưỡng của hai trạm, ngang luật hysteresis + ngưỡng hai tham số tốt nhất, và tự thích nghi khi môi trường đổi.

## 2. Problem · Assumptions
- Problem [F §II, eq. 2–3]: min E[failure] s.t. E[handoff] ≤ ngân sách ⇔ min E[failure] + c·E[handoff].
- A1 [F §II]: tín hiệu (dB) = path loss + shadow fading Gauss, AR(1) theo không gian.
- A2 [F §II]: hai trạm; mỗi chu kỳ lấy mẫu quyết định dựa trên mọi số đo tới lúc đó.
- A3 [F §IV]: phương sai có điều kiện không phụ thuộc thông tin vị trí ⇒ [I] bất định đồng đều giữa các quyết định (κ = 0).

## 3. Method
DP hữu hạn bước (§III): tối ưu nhưng không dừng và cần biết trước quỹ đạo ⇒ chỉ làm đường cong mốc. LO (§IV): nhìn một
bước; đổi khi chênh xác suất rơi dưới ngưỡng giữa hai trạm vượt c; với Gauss, xác suất do trung bình và phương sai có
điều kiện quyết định (eq. 11–12); dùng ước lượng thay tham số thật (eq. 13). So bằng đường cong (E[handoff], E[failure]).

## 4. Evaluation
| Setup | Baseline | Metric | Kết quả chính | § |
|---|---|---|---|---|
| 2 trạm; 50.000 lần/cấu hình; bước mẫu 2/5/10 m (14,4/36/72 km/h); CÙNG bộ dự báo cho mọi luật | hysteresis; hysteresis-threshold; DP | đường E[handoff]–E[failure] | LO và hysteresis-threshold ít failure hơn hysteresis ở cùng số handoff; LO ≈ hysteresis-threshold tốt nhất | §V, Fig. 3 |
| như trên, đổi tốc độ, c cố định | hysteresis | điểm vận hành | LO đi "knee tới knee"; hysteresis không khai thác được dự báo tốt hơn ở tốc độ chậm | §V, Fig. 4–5 |

## 5. Claim ↔ Evidence
| # | Claim | Loại | Phủ tới đâu | Khe hở? | § |
|---|---|---|---|---|---|
| 1 | Nghiệm biến phân là nghiệm Bayes với c thích hợp | định lý | mô hình đã nêu | Không | Thm 1 |
| 2 | LO tốt hơn hysteresis, nhất là khi dự báo chính xác | mô phỏng | một cặp trạm, 3 tốc độ | Không CI | §V |
| 3 | Lợi thế chính của LO là tự thích nghi | mô phỏng + lập luận | Fig. 4–5 | Không CI | §V–VI |

## 6. Limitation
- Tác giả [F]: DP không thực dụng; không xét chi phí mạng của trễ handoff (§I).
- Tôi thấy [I]: phương sai hằng ⇒ không đo được giá trị của độ rộng biến thiên; mốc DP biết quỹ đạo (nhiều thông tin hơn
  luật); không phân rã.

## 7. So với đề tài
- Trùng: ràng buộc ↔ Lagrange (Thm 1 ↔ λ của K2); luật dựa phân phối vs họ tĩnh đã tune, cùng thông tin, cùng ngân sách
  (Fig. 3 ↔ f04b/f05/F7); hysteresis + ngưỡng tuyệt đối ↔ họ abs/rel (K22); "tĩnh gần đủ" ↔ PIVOT của F6.
- [I] Lợi thế LO so với hysteresis thuần đến từ phụ thuộc MỨC tín hiệu (Z loại (a), T4 §1) — đúng Mệnh đề 2 đường (i)(a).
- Khác, ĐÃ KIỂM: κ = 0 theo cấu trúc (§IV) — đề tài có κ̂ = 0,15–0,27 và tách K2 − SC; mốc DP biết quỹ đạo, không phải
  oracle một bước cùng thông tin; cường độ tín hiệu ≠ delay hàng đợi dưới telemetry cũ và nhiễu.
- Dùng được: Related Work (tiền lệ gần nhất); cách so bằng đường cong đánh đổi; tiền lệ cho H3 cũ nếu Phase 2 mở lại.

## 8. Câu định vị
"Veeravalli–Kelly cho thấy trong handoff, luật so xác suất chỉ ngang luật hysteresis + ngưỡng hai tham số tốt nhất khi so
trên cùng bộ dự báo (§V, Fig. 3); vì phương sai có điều kiện trong mô hình của họ không đổi (§IV), phép so không thể tách
giá trị của độ rộng biến thiên. Đề tài tách đúng phần đó khi κ > 0, trong hệ hàng đợi với telemetry cũ và nhiễu."

## 9. Câu hỏi mở
- Prakash–Veeravalli 2000 (JSAC, PDF trên trang tác giả): có so dưới môi trường đổi với tham số đóng băng không?
- Rezaiifar–Makowski–Kumar 1995: chính sách tối ưu có cấu trúc ngưỡng không? [?]
