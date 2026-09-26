# Research brief — v2.1 (2026-09-25)

> Soạn với hỗ trợ của công cụ AI; tác giả kiểm và chịu trách nhiệm nội dung. Cập nhật theo nhận xét GVHD 2026-09-25
> (`notes/meetings/2026-09-25_gvhd_feedback.md`): mục tiêu tính bằng ms, chi phí đổi c (ms), telemetry cũ và nhiễu,
> phạm vi theo tầng, quy tắc SESOI, DP0 gộp DP1 ngày 20/10. Lý do: `02_decision_log.md`. Thuật ngữ: `06_definitions.md`.
> Tài liệu Phase 0 đóng băng tới DP0; chỉ thêm dòng đính chính.

## 1. Problem

Một luồng nhỏ nhạy độ trễ đang đi trên đường A. Network Digital Twin nhìn mạng qua telemetry vừa cũ vừa nhiễu (đếm gói
theo cửa sổ, có tuổi và nhiễu đếm) và dự đoán đường B tốt hơn. Vận hành thường quyết định đổi/giữ bằng một ngưỡng tĩnh
(hysteresis, dampening) tune một lần; ngưỡng đó có thể quá thận trọng ở quyết định ít bất định và quá liều ở quyết định
nhiều bất định. Chưa rõ cái giá này đáng kể đến đâu, tính bằng mili giây người dùng cảm nhận được.

## 2. Gap — mức: strong candidate (chốt ở DP0 + DP1, 20/10/2026)

- Seshadri–Katz 2003: ngưỡng H phù hợp thay đổi GIỮA các cấu hình; H động kiểu MIMD; không so với oracle. [chưa đọc full text]
- Burbano et al. 2025 (arXiv 2511.10146), Liyanage et al. 2026 (arXiv 2604.21483), cùng nhóm: chọn server theo dự đoán
  latency kèm hysteresis; Burbano dự đoán delay từ đo thụ động (tốc độ đến, utilization, payload) qua một mô hình delay —
  gần nhất với chuỗi "ρ̂ → mô hình delay → ngưỡng" của đề tài. [đã kiểm trang arXiv/abstract; chưa tự đọc full text]
- OpenTwin v2, CERT: bất định hiệu chỉnh từ dữ liệu cho cổng/chứng nhận; không so với bất định lan truyền qua mô hình.
  [OpenTwin: full text, D17; CERT: §1–7, note L1.2]
- Fischer–Vöcking 2005/2009: vòng kín, hội tụ quần thể. [chưa đọc full text]
→ Chưa thấy công trình đo, bằng ms, khoảng cách giữa ngưỡng tĩnh tốt nhất và oracle cùng thông tin cho quyết định đổi/giữ
dưới telemetry cũ và nhiễu, theo cơ chế hàng đợi và telemetry.

## 3. Thesis

Twin có nên thay ngưỡng tĩnh bằng quyết định theo từng lần hay không phụ thuộc vào việc bất định có đảo thứ tự các quyết
định so với cải thiện dự đoán; mức đó do cơ chế hàng đợi và telemetry của chính mạng quyết định và ước lượng được từ đầu
ra của twin.

## 4. Mục tiêu tối ưu — CHỐT (K2, K3, K21; GVHD 2026-09-25)

max E[a·(I_D − c)] với ràng buộc E[a·1{I_D < −ε}] ≤ α (a = 1 nếu đổi; kỳ vọng trên MỌI epoch).
Luật tối ưu một bước: đổi ⇔ E[I_D | F] − λ·p− > c; λ ≥ 0 (ms) nhỏ nhất đạt ngân sách. α → ∞ cho λ = 0, tức luật delay
kỳ vọng; quét α nối hai trường hợp. Chính: α = 1%, c = 0, ε/S = 0,5. Độ nhạy: α ∈ {0,5; 2; ∞}%, c ∈ {0,25; 1}·S,
ε/S ∈ {0,25; 1; 2}. Loss: nhãn riêng, δ = 10⁻³ (ITU-T Y.1541, lớp thời gian thực; đã xác nhận bản 12/2011 còn hiệu
lực và RFC 5976 tóm tắt Class 0 có loss ratio ≤ 10⁻³). Đây là mức loss tuyệt đối; dùng làm ngưỡng chênh lệch là lựa chọn
phân tích. Nguyên tắc: mục tiêu được chọn vì đo đúng thứ người dùng cảm nhận, không vì làm phương pháp thắng.

## 5. Research questions

| RQ | Câu hỏi | Tầng | Bằng chứng |
|---|---|---|---|
| RQ1 | Ngưỡng tĩnh tốt nhất (tuyệt đối + tương đối, tune từng ô) thua oracle một bước cùng thông tin bao nhiêu ms, so với headroom; khoảng cách thay đổi thế nào theo độ sâu buffer, Π_knee, nhiễu đếm, tuổi? | 1 | Quét có kiểm soát + OFAT; decision-level; CI paired theo seed |
| RQ1-op | Một chỉ số tính từ đầu ra twin có dự báo được khoảng cách đó trước khi chạy oracle không? | 1 | Tương quan hạng chỉ số–khoảng cách qua các ô |
| RQ2 | Ở ô có khoảng cách có ý nghĩa: luật dùng bất định lan truyền qua twin thu hồi bao nhiêu khoảng cách khi twin đúng họ, sai K, và khi hàng đợi thật là token bucket (X1′)? Tầng 3: khi chế độ dịch chuyển với tham số đóng băng, luật nào giữ ngân sách? | 2–3 | Baseline tune công bằng; knowledge parity; X1′ (và X2 nếu có dữ liệu) |

## 6. Hypotheses — quy tắc chốt hôm nay; con số khoá ngày 13/10, trước khi chạy F2

**Quy tắc SESOI:** khoảng cách chỉ "có ý nghĩa" khi vượt CẢ HAI: sàn tuyệt đối m ms (lý do ứng dụng) và tỉ lệ r của
headroom E[(I_D − c)⁺]. **Ngân sách:** "vượt" khi cận dưới CI95 của harm > 1,25α; "giữ" khi cận trên ≤ 1,25α.

- **H1 (đối chứng):** họ tịnh tiến → |khoảng cách| ≤ 2 SE Monte Carlo (surrogate và e01). Vi phạm = lỗi triển khai.
- **H2 (cơ chế, tầng 1):** (a) qua ≥ 16 ô, Spearman(chỉ số chính, khoảng cách) ≥ 0,6; bác bỏ nếu cận trên CI95 < 0,3.
  (b) Ô dự đoán "ngưỡng tĩnh đủ" (K = 11, tuổi cố định, ρ̄ ≤ 0,7) không có khoảng cách có ý nghĩa.
  (c) Bản twin của chỉ số tương quan ≥ 0,8 với bản oracle; bác bỏ nếu cận trên CI95 < 0,5.
- **H3 (tầng 2, cùng chế độ):** ở ô khoảng cách có ý nghĩa: G ≥ 0,7 dưới M0 (verification); G ≥ 0,5 dưới M1; dưới X1′,
  luật lai thu hồi không kém twin thuần. Trong cùng chế độ, hiệu chỉnh trên cùng thực tế giữ ngân sách cho mọi luật;
  khác biệt nằm ở gain.
- **H3′ (tầng 3, dịch chuyển):** tham số đóng băng; luật lai giữ ngân sách ở mọi cặp chế độ đã đăng ký; twin thuần vượt
  ở ≥ 1 thực tế ngoài họ.

## 7. Candidate contributions — cần literature xác nhận ở DP0 + DP1

(a) Bản đồ khoảng cách (ms, và theo tỉ lệ headroom) kèm cơ chế. (b) Chỉ số tính từ twin dự báo khi nào cần thích nghi.
(c) Độ bền của bất định lan truyền qua mô hình, hiệu chỉnh từ dữ liệu và luật lai (tầng 2–3). (d) Phụ: giao thức đánh giá.

## 8. Không claim

Stale state làm routing lỗi (Shaikh 2001; Mitzenmacher 2000) · diễn giải tải theo tuổi (Dahlin 2000; CERT) · hysteresis và
hysteresis thích nghi (RON 2001; Seshadri–Katz 2003; handover MRO; SD-WAN dampening) · lý thuyết hysteresis dưới bất định
(Dixit 1989) · chống dao động do thông tin cũ (Khanna–Zinky 1989; Fischer–Vöcking) · dự đoán delay từ đo thụ động kèm
hysteresis (Burbano 2025; Liyanage 2026) · fallback theo độ tin cậy của twin (OpenTwin; Almohammedi 2026) · conformal gate,
risk trên ACCEPT, risk theo action (OpenTwin; CERT; LEC; Zhu 2026) · tối ưu của luật Neyman–Pearson/Lagrange (Neyman–Pearson;
Lekeufack 2024) · probabilistic twin (Kapteyn et al. 2021) · "tổng quát cho mọi mạng".

## 9. Assumptions · Limitations · Scope

- **Assumptions:** tải nền ngoại sinh; luồng nhỏ không chiếm tải; telemetry = đếm gói trên link theo cửa sổ W, có tuổi và
  nhiễu đếm; tải OU một thang thời gian (giả định yếu nhất; X2 kiểm nếu F1 có chuỗi thời gian); oracle một bước; hai path
  rời, mỗi path một link nghẽn.
- **Limitations:** bằng chứng chính là DES; testbed Mininet là HTB token bucket (≠ M/D/1/K), 4–8 Mb/s; pilot P01–P05 là
  exploratory, P02–P04 dùng mục tiêu cũ (b).
- **Scope:** tầng 1 bắt buộc cho NCKH (RQ1, RQ1-op, 16 ô); tầng 2 (RQ2 cùng chế độ, X1′); tầng 3 cho paper (dịch chuyển,
  ACI, M2, burstiness H2, Mininet). Không làm: vòng kín, nhiều luồng lớn, TE toàn mạng, telemetry probe-delay kiểu SD-WAN.
- **Ứng dụng khớp giả định:** quyết định cho từng luồng thời gian thực nhỏ (VoIP, control traffic).

## 10. Mốc và kill criteria

| Mốc | Ngày | Nội dung / GO nếu | Nếu không |
|---|---|---|---|
| Giữa kỳ | 13/10/2026 | F1 xong (điểm neo dưới dạng Π); tác giả tự dẫn được công thức nền; khoá m, r trước khi chạy F2 | Báo GVHD, điều chỉnh lịch |
| DP0 + DP1 | 20/10/2026 | ≥ 1 ô gần điểm neo có khoảng cách có ý nghĩa và P(I_D < −ε) ≥ 2α; lưới tầng 1 ≤ 3 CPU-ngày; hai cách tính oracle chênh < m/2; DP1-v2 (khung D18) PASS | NARROW (buffer sâu, cửa sổ dài) hoặc PIVOT "ngưỡng tĩnh đủ, và vì sao"; DP1 theo D18 |
| DP2 | 01/12/2026 | Có ô khoảng cách có ý nghĩa | Kết luận chính "ngưỡng tĩnh đủ trong phạm vi đã kiểm"; không đổi metric |
| DP3 | 15/12/2026 | Tầng 2 báo được theo prereg | Báo giới hạn; tầng 3 thành việc sau NCKH |

## 11. Phép thử ngược · Elevator test

- **Không ô nào có khoảng cách có ý nghĩa:** "ngưỡng tĩnh đủ trong phạm vi đã kiểm, vì mức đảo thứ tự thấp", kèm chỉ số
  RQ1-op để người vận hành biết khi nào không cần twin xác suất.
- **Có ý nghĩa theo tỉ lệ headroom nhưng dưới sàn ms:** khác biệt có thật về tương đối, người dùng không cảm nhận được; báo cả hai.
- **Elevator test (kịch bản):** "Khi mạng chọn đường cho một cuộc gọi, nó dựa vào số đo đã cũ và có nhiễu. Người ta thường đặt
  luật đơn giản: chỉ đổi nếu đường mới tốt hơn ít nhất X mili giây hoặc X phần trăm. Em hỏi: luật đơn giản đó thua cách tốt nhất
  có thể bao nhiêu mili giây, ở loại mạng nào, và twin có tự biết trước điều đó không."
  **Kết quả:** chưa làm — tác giả phải tự thử với một người thật và ghi nguyên văn câu họ nhắc lại.
