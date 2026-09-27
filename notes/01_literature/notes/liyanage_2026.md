# Liyanage et al. 2026 — Chọn edge server có tính rủi ro và ổn định dưới SLO

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | Risk-Aware and Stable Edge Server Selection Under Network Latency SLOs |
| Tác giả (đúng thứ tự của PHIÊN BẢN đang đọc) | Mohan Liyanage; Arnova Abdullah; Eldiyar Zhantileuov; Rolf Schuster (FH Dortmund) |
| Nguồn | arXiv:2604.21483v1 (23/04/2026); mã: github.com/ldmohan/ContainerLab-IWCMC-2026 (chú thích trong bài) |
| Trạng thái | được nhận trình bày tại IWCMC 2026 (theo ghi chú trên bản arXiv); chưa đối chiếu bản proceedings |
| Lượt đã đọc | 2 — toàn văn HTML §I–VI, Alg. 1–2, Table I–III; hình chỉ đọc chú thích |
| Ngày đọc | 2026-09-27 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | trung bình — cùng ý "dùng (μ, σ) + hysteresis", nhưng thiết kế không tách được giá trị của bất định; mục tiêu SLO khác mục tiêu của đề tài |

Nhãn: [F] paper nói trực tiếp (có §/tr.) · [I] suy ra (ghi suy từ đâu) · [?] chưa kiểm

## 0. Five Cs (sau lượt 1)

- Category: thiết kế lớp quyết định + đánh giá testbed.
- Context: nối tiếp bộ dự đoán rational và MO-HAN của cùng nhóm (§I, [1]–[2]).
- Correctness: Normal surrogate + cận Cantelli; dừng cục bộ trong cửa sổ (§III-D); cách có (μ_i, σ_i) cho server
  KHÔNG được chọn không nêu rõ [?].
- Contributions (theo tác giả, §I): (1) đánh giá rủi ro lai Normal–Cantelli; (2) hysteresis theo phân vị;
  (3) kiểm trên testbed nhiều server.
- Clarity: tốt.
- Quyết định: lượt 2 đủ; lượt 3 chỉ khi muốn tái lập bằng repo của họ.

## 1. Một câu: paper làm gì?

Lớp quyết định biến (μ, σ) của latency gần đây của từng server thành rủi ro vi phạm SLO để lọc server khả thi, xếp
hạng theo μ + kσ, và chỉ đổi khi ứng viên tốt hơn tương đối ít nhất Δ trong N bước liên tiếp.

## 2. Problem · Assumptions

- Problem [F §III-A]: K server; d_i(t) là latency quan sát; μ_i, σ_i trên cửa sổ trượt W; SLO τ = 500 ms.
- A1 [F §III-D]: latency dừng cục bộ trong cửa sổ.
- A2 [F §III-D]: Normal surrogate đủ cho suy luận phân vị; Cantelli làm lưới an toàn.
- A3 [F §III-E]: hộp đen, chỉ có quan sát đầu–cuối.
- [?]: d_i(t) của server không được chọn được đo thế nào (probe song song hay replay).

## 3. Method

p_Norm = 1 − Φ((τ − μ)/σ); p_Cant = 1/(1 + ((τ − μ)/σ)²). Alg. 1 chọn server có p_Norm nhỏ nhất và chỉ chấp nhận nếu
cả hai < ε. Alg. 2 lấy ứng viên có μ + kσ nhỏ nhất trong tập khả thi và đổi khi Score_cur − Score_j ≥ Δ·Score_cur trong
N bước liên tiếp. Tham số: ε = 0,15; k = 1,645; Δ = 0,05; N = 5 (§V-A). Theo ngôn ngữ đề tài: Alg. 2 là một **ngưỡng
tĩnh tương đối** (giống họ "rel") trên một **tâm đã dịch theo rủi ro** μ + kσ với k cố định — độ rộng chỉ vào qua một
lượng dịch có hệ số hằng, không phải đánh đổi tối ưu từng quyết định [I]. Nếu σ gần bằng nhau giữa các server, xếp
hạng theo μ + kσ trùng xếp hạng theo μ [I; đúng điều kiện H1 của T3].

## 4. Evaluation

| Setup (topology/testbed/data) | Baseline | Metric | Kết quả chính (có số) | §/tr. |
|---|---|---|---|---|
| Testbed: 3 server, 1 client, ứng dụng nhận diện biển báo; SLO 0,5 s | mean-only (không hysteresis); Alg. 1; Alg. 2 | delay TB, DMR, % bước có đổi | mean-only 0,448 s/39%/46%; Alg. 1 0,451/34%/89,5%; Alg. 2 0,429/34%/5,5% | §V-A, Table II |
| Độ nhạy dwell N | Alg. 2, N = 2…10 | % đổi, mean, P95 | N = 8 và 10: 0% đổi, mean 0,414 s, P95 0,472 s — tốt nhất bảng | §V-C, Table III |
| Replay containerlab 10 server | Alg. 2 | minh hoạ | hội tụ về vài server rủi ro thấp; tác giả nói không thay được triển khai thật | §V-F |

## 5. Claim ↔ Evidence

| # | Claim của tác giả | Loại evidence | Evidence thật sự phủ tới đâu | Khe hở? | §/tr. |
|---|---|---|---|---|---|
| 1 | Tính tới bất định giảm DMR 39% → 34% so với mean-only | thí nghiệm | Một trace, không CI; số bước không nêu — % đổi là bội của 0,5% gợi ý ~200 bước [I], khi đó chênh ~10 frame, cỡ 1 sai số chuẩn nhị thức [I] | Có — có thể không có ý nghĩa thống kê | Table II |
| 2 | Hysteresis giảm đổi 89,5% → 5,5% mà giữ DMR | thí nghiệm | Alg. 1 → Alg. 2 trong cùng trace | Hợp lệ trong trace | Table II |
| 3 | Tính bất định vào lựa chọn giảm vi phạm SLO | thí nghiệm | Thiếu ô "mean-only + hysteresis": không tách được phần do bất định và phần do hysteresis/feasibility | Có — thiết kế không factorial | §V-A, §V-H, Table II |
| 4 | N ≈ 5–6 là cân bằng tốt | sensitivity | N ≥ 8 (không đổi lần nào) cho mean và P95 thấp nhất; bài không bàn | Có | §V-C, Table III |
| 5 | Normal và Cantelli cho xếp hạng nhất quán | quan sát | "trên các trace của chúng tôi"; không định lượng | Có | §V-D, §V-G |

## 6. Limitation

- Tác giả tự nêu [F]: 3 server, 1 client; cần nhiều client và tải đa dạng (§V-H); Δ, N cố định (§IV-D); Gaussian
  có thể làm trơn hành vi cực trị (§III-D).
- Tôi thấy [I]: không CI, một trace; thiếu ô factorial; delay TB 0,43–0,45 s sát SLO 0,5 s nên DMR 34–39% là chế độ rất
  căng; không mô hình tuổi; "không đổi" thắng trong Table III gợi ý giá trị của việc đổi trong trace này thấp.

## 7. So với đề tài của tôi

- Trùng: (μ, σ) để xếp hạng + hysteresis; quyết định đổi/giữ; latency mạng.
- Khác, ĐÃ KIỂM (§/tr.): không tuổi/nhiễu telemetry (§III-A); mục tiêu SLO/DMR, không phải gain trung bình có ràng buộc
  harm (§III-A, §V-A); không oracle; không có ô "trung bình + hysteresis" (§V-A).
- Khác, CHƯA KIỂM / suy luận: μ + kσ với k cố định là ngưỡng tĩnh trên tâm dịch [I].
- Dùng được: baseline "μ + kσ + hysteresis tương đối + dwell N" cho tầng 2; DMR cho mở rộng mục tiêu SLO; repo để kiểm
  ngoài; câu Related Work.

## 8. Câu định vị

"Liyanage et al. báo cáo lợi ích khi kết hợp bất định với hysteresis nhưng không có ô 'trung bình + hysteresis'
(§V-A, Table II), nên không tách được giá trị của bất định khỏi giá trị của hysteresis; đề tài tách đúng hai phần này
(luật SC so với K2) so với oracle cùng thông tin trong DES, và thấy phần của bất định dưới 0,16 ms trong miền đã thử (f05)."

## 9. Câu hỏi còn mở

- Mục tiêu SLO (xác suất D > τ) có làm độ rộng có giá trị hơn mục tiêu trung bình không? — ứng viên mở rộng, hỏi GVHD.
- Có thể dùng repo của họ để chạy thêm ô "mean-only + hysteresis" trên trace của họ không? — kiểm ngoài rẻ.
