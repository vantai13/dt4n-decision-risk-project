# Attri 2026 — CERT: Certified Route Planning under Drifting Costs

| Trường | Giá trị |
|---|---|
| Tác giả | Krishi Attri |
| Nguồn | [engrXiv DOI 10.31224/7306](https://doi.org/10.31224/7306); [bản tác giả đăng với toàn văn hiển thị](https://www.researchgate.net/publication/406966969_CERT_Certified_Route_Planning_under_Drifting_Costs_Conformal_certificates_sense-to-certify_and_the_price_of_staleness) |
| Trạng thái | Preprint 10/06/2026; chưa xác nhận peer review |
| Mức kiểm | 2026-09-23: các đoạn §1–7 và một phần Appendix A qua toàn văn hiển thị; chưa đối chiếu PDF gốc từng phương trình |
| Mức đe dọa | **Rất cao** cho claim “đầu tiên chứng nhận route dưới state cũ bằng conformal/age”; cao cho RQ2 |

Nhãn: **[F]** phát biểu/nội dung đọc được trong bài; **[I]** hệ quả suy ra cho đề tài; **[?]** cần kiểm thêm.

## Five Cs / một câu

- **Category:** [F] certified route planning + sensing + non-exchangeable conformal trên cost biến động (§1–3).
- **Context:** [F] robot/road graph có edge cost thay đổi và chỉ quan sát một phần; quan sát mới có chi phí (§2).
- **Correctness:** [I] guarantee **có điều kiện** A1–A4 và yêu cầu phân biệt observed/latent cost; không được diễn giải thành guarantee arbitrary drift (§2, §4, §7).
- **Contributions:** [F] mỗi vòng đưa `LB ≤ OPT(t) ≤ UB` và độ tin cậy giảm theo staleness; điều khiển sensing theo certificate gap; các định lý T1–T7 (§1, §4).
- **Clarity:** [I] rất sát trust object của đề tài; ký hiệu `margin` trong bài chủ yếu là bề rộng interval/bound, chưa xác nhận có phân tích top-2 estimated cost margin như biến giải thích rủi ro.
- **Quyết định:** đọc sâu toàn bộ Appendix A và đối chiếu trực tiếp trước DP1.

## Problem, assumptions, method

- [F] Bài hỏi route hiện tại còn gần tối ưu bao nhiêu khi nhiều edge cost đã cũ; graph có cost thật `c_e(t)` chưa quan sát, age theo cạnh, một quan sát trả phí mỗi vòng (§1–2).
- [F] A1 chặn drift theo thời gian bằng `ρ_e`; A2 chặn drift của phân phối residual theo total variation; A3 noise đối xứng, đơn đỉnh cho phiên bản latent/sum-aware; A4 các edge chung buffer có cùng họ noise (§2).
- [F] Score từ residual đã trừ `ρ_e·age`; quantile có trọng số theo age. Interval cạnh có dạng `ĉ_e ± (λq + ρ_e a_e)`. Hai lần shortest-path search trên lower/upper edge costs tạo `LB, UB`; chênh `UB−LB` hướng sensing và là thước chứng nhận (§3, Appendix A.1).
- [F] T1a bảo đảm cho quan sát kế tiếp; T1b cho latent cost với margin gấp đôi và thêm điều kiện. Guarantee report có correction staleness, không phải một mức 1−α bất biến (§4).
- [F] T6 nêu per-round coverage là marginal; khi chính sách chỉ hành động ở các vòng certificate tốt, cần α-spending tại decision instants để có validity dọc trajectory (§4). Đây là cảnh báo selection trực tiếp cho gate ACCEPT của đề tài.

## Evidence và giới hạn

| Claim | Evidence đọc được | Phạm vi |
|---|---|---|
| Age-aware route certificate | Construction §3; T1a/T1b, T2′, T4–T6 §4 | Dựa trên A1–A4, calibration/sensing đúng giao thức |
| Hiệu quả thực nghiệm | §6: simulation 6×6, 25 seeds ×300 rounds/condition; replay traffic hai thành phố; so sensing baselines | Không phải field validation của coverage; §7 nói rõ điều này |
| Robustness khi mô hình drift sai | Các dòng off-model §6 và hạn chế §7 | Thực nghiệm, **không** có bound ngoài A1/A2 |
| Gate/freshness | Sum-aware certificate cần freshness gate để xử lý selection bias (§3–4) | Gate này liên quan điều kiện dùng upper bound; không tự động tương đương ACCEPT/ABSTAIN của đề tài |

## So với đề tài này

- **Trùng [F/I]:** stale edge costs, age đưa thẳng vào interval/certificate, conformal, path-level quality và regret gần tối ưu, quyết định có nên tiếp tục sensing/execute (§1–4). Do đó không claim “age-conditioned conformal cho route quality” hoặc “conformal route certificate dưới stale data” là đầu tiên.
- **Khác đang kiểm [I]:** đề tài nghiên cứu xác suất flip/harmful của lựa chọn routing do twin xếp hạng theo `z/τ_OU` và estimated margin, với gate ACCEPT/ABSTAIN trên risk/coverage; CERT ưu tiên deterministic drift bound, interval trên từng edge, certificate cho `OPT`, và sensing trả phí. Chênh lệch này chỉ có giá trị novelty khi chứng minh bài CERT không đã phân tích cùng decision score/risk target trong Appendix.
- **Baseline bắt buộc [I]:** triển khai một CERT-style age-widened robust route certificate trong scope so sánh có thể thực hiện, hoặc nêu rõ vì sao không khả thi và ít nhất đo against age-widening/interval-route baseline. Không chỉ so với global ACI.
- **Câu định vị tạm:** CERT đã chứng nhận chất lượng route khi map cũ bằng age-widened conformal intervals và sensing chủ động (§2–4). Đề tài chỉ có thể khác nếu đo/giải thích risk của *lựa chọn theo twin* bằng age × margin dưới OU và cho thấy gate có lợi hơn certificate kiểu CERT ở cùng ngân sách thông tin/rủi ro. **Chưa khóa câu này trước đọc Appendix và thí nghiệm.**

## Câu hỏi còn mở

1. T1/T6 đảm bảo chính xác gì tại tập vòng được chọn để hành động, và có khớp selective harmful risk không?
2. “Margin” của CERT có bao giờ là top-2 estimated route cost gap, hay chỉ certificate width?
3. Với observation age **chung** và không có paid sensing như thiết kế đề tài, CERT-style baseline rút gọn cụ thể là gì?
4. RQ2 còn khác biệt problem/method nào ngoài domain nếu CERT đã có upper bound cho incumbent regret?
