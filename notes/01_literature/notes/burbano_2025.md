# Burbano et al. 2025 — MO-HAN: chọn edge server bằng dự đoán + độ tin cậy + hysteresis

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | Dynamic Edge Server Selection in Time-Varying Environments: A Reliability-Aware Predictive Approach |
| Tác giả (đúng thứ tự của PHIÊN BẢN đang đọc) | Jaime Sebastian Burbano; Arnova Abdullah; Eldiyar Zhantileuov; Mohan Liyanage; Rolf Schuster (FH Dortmund) |
| Nguồn | arXiv:2511.10146v1 (13/11/2025) |
| Trạng thái | preprint; chưa xác nhận venue |
| Lượt đã đọc | 2 — toàn văn §I–V, Eq. 1–7, Alg. 1, Table I; Fig. 3–4 chỉ đọc chú thích |
| Ngày đọc | 2026-09-27 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | thấp–trung bình — cùng họ "dự đoán + hysteresis" nhưng không có luật dùng bất định từng quyết định, không oracle, không mô hình tuổi |

Nhãn: [F] paper nói trực tiếp (có §/tr.) · [I] suy ra (ghi suy từ đâu) · [?] chưa kiểm

## 0. Five Cs (sau lượt 1)

- Category: đề xuất thuật toán + đánh giá testbed (bài hội thảo ngắn).
- Context: chọn server trong MEC; nối tiếp bộ dự đoán rational của cùng nhóm ([21] = arXiv:2511.02501).
- Correctness: giả định số đo thụ động mới nhất đủ đại diện cho latency sắp tới; không bàn tuổi/nhiễu [I]; cách có
  latency của server KHÔNG được chọn khi replay dataset không được nêu [?].
- Contributions (theo tác giả, §I): (1) chọn server dẫn dắt bởi dự đoán; (2) độ tin cậy thích nghi bằng EWMA;
  (3) nhận biết chi phí đổi bằng hysteresis.
- Clarity: ngắn, rõ; thiếu chi tiết thống kê.
- Quyết định: dừng ở lượt 2 (đủ cho positioning).

## 1. Một câu: paper làm gì?

MO-HAN chọn server có điểm tổng hợp thấp nhất giữa latency dự đoán (mô hình rational × exp từ payload, utilization,
arrival rate) và "độ thiếu tin cậy" EWMA, và chỉ đổi khi điểm cải thiện ít nhất một ngưỡng hysteresis cố định θ.

## 2. Problem · Assumptions

- Problem [F §III]: một thiết bị, J edge server; mỗi request chọn một server để giảm latency E2E và số handover.
- A1 [F §III-A, Eq. 1–2]: latency mỗi hop là hàm rational có điều biến mũ của (γ, Φ, Υ), hệ số học từ dữ liệu;
  latency E2E là tổng các hop.
- A2 [I, từ §III-A và §IV-D]: số đo gần nhất phản ánh latency của request sắp gửi; không mô hình tuổi hay nhiễu đo.
- A3 [F §IV-F]: mọi thuật toán được so trên cùng một dataset đã thu.

## 3. Method

Mỗi request, bộ dự đoán tính T̂_j cho mọi server. R_j là trung bình trượt mũ (β ∈ [0,8; 0,99]) của chỉ báo "latency
quan sát ≤ (1+δ)·dự đoán". Điểm S_j = α·T̂_j/T_max + (1−α)(1−R_j), thấp là tốt. Đổi sang server có S nhỏ nhất chỉ khi
S_hiện_tại − S_tốt_nhất ≥ θ. Theo ngôn ngữ đề tài: MO-HAN là **một ngưỡng cố định trên một tâm đã hiệu chỉnh** — R_j
dịch tâm theo lịch sử sai số của từng server — không dùng phân phối của từng quyết định [I].

## 4. Evaluation

| Setup (topology/testbed/data) | Baseline | Metric | Kết quả chính (có số) | §/tr. |
|---|---|---|---|---|
| Testbed thật: ESP32, 4 router, load generator TCP/UDP, capture node tcpdump, SeQaM/CAMS; >5000 mẫu; frame 400–600 KB | NR-HAN (gần nhất, không đổi), RR-HAN (vòng tròn), LL-HAN (tham lam) | mean, median, P95 latency; tỉ lệ handover | MO-HAN 44,1/42,4/55,0 ms, HR 37,4%; LL-HAN 43,3/41,6/57,1 ms, 68,7%; RR-HAN 49,5/50,1/60,2 ms, 98,9%; NR-HAN 47,1/45,4/59,4 ms, 0% | §IV-F, Table I |
| Tham số ví dụ | — | — | α = 0,5; β = 0,9; δ = 0,2; θ = 0,05 ("gần frontier") | §IV-F |

## 5. Claim ↔ Evidence

| # | Claim của tác giả | Loại evidence | Evidence thật sự phủ tới đâu | Khe hở? | §/tr. |
|---|---|---|---|---|---|
| 1 | Hạ latency trung bình và đuôi so với baseline tĩnh (NR) và chia đều (RR) | thí nghiệm | Đúng theo Table I | Không CI, một dataset | Abstract; Table I |
| 2 | Giảm handover gần 50% so với LL-HAN | thí nghiệm | 37,4% so với 68,7% | Không CI | Abstract; §IV-F |
| 3 | Tốt hơn LL-HAN về latency cho 95% request; kết luận: latency thấp hơn chính sách tĩnh và phản ứng | thí nghiệm | LL-HAN có mean (43,3) và median (41,6) THẤP HƠN MO-HAN (44,1; 42,4); MO-HAN chỉ thắng P95 (55,0 so với 57,1) | Có — §IV-F và §V rộng hơn Table I | §IV-F; §V; Table I |
| 4 | Thiết lập tham số "gần frontier" | sensitivity | Tham số chọn trên chính dữ liệu đánh giá [I] | Có — tune trên dữ liệu kiểm | §IV-F |
| 5 | Đổi liên tục gây chi phí thực | lập luận + trích dẫn | Thí nghiệm không mô hình chi phí re-authentication (tác giả tự nêu) | — | §I; §IV-F |

## 6. Limitation

- Tác giả tự nêu [F]: không tính chi phí re-authentication (§IV-F); hướng tới đa mục tiêu và federated edge (§V).
- Tôi thấy [I]: không CI, không lặp; tham số chọn trên dữ liệu đánh giá; replay cần latency phản thực của server không
  được chọn mà cách lấy không nêu [?]; không có luật dùng bất định để so; không mô hình tuổi/nhiễu telemetry.

## 7. So với đề tài của tôi

- Trùng: hysteresis trên chênh lệch dự đoán; chọn giữa nhiều đích; latency và ổn định.
- Khác, ĐÃ KIỂM (§/tr.): không mô hình tuổi/nhiễu (§III-A); không luật dùng phân phối hay xác suất gây hại
  (§III-B, Alg. 1); không oracle; không CI (§IV-F).
- Khác, CHƯA KIỂM / suy luận: R_j đóng vai trò hiệu chỉnh tâm theo server [I].
- Dùng được: baseline "μ + hysteresis + reliability" (protocol đã có "μ + k·s kiểu Liyanage/Burbano"); câu Related
  Work; ví dụ khác biệt giữa các luật chỉ cỡ 1–6 ms trên nền 40–60 ms.

## 8. Câu định vị

"Burbano et al. dùng một ngưỡng hysteresis cố định trên điểm dự đoán có hiệu chỉnh độ tin cậy và không so với luật
dùng bất định từng quyết định (§III-B, §IV-E); đề tài đo đúng khoảng cách đó so với oracle cùng thông tin, dưới
telemetry có tuổi và nhiễu, và thấy nó nhỏ hơn SESOI trong miền đã thử (f04b, f05)."

## 9. Câu hỏi còn mở

- Cần đọc lại sau lesson nào: không cần cho RQ1.
- Muốn hỏi tác giả / GVHD: khi replay dataset, latency của server không được chọn lấy từ đâu?
