# Guérin & Orda 1999 — QoS routing với thông tin không chính xác

| Trường | Giá trị |
|---|---|
| Tác giả | Roch A. Guérin; Ariel Orda |
| Nguồn | [IEEE/ACM ToN 7(3):350–364, DOI 10.1109/90.779203](https://doi.org/10.1109/90.779203); [PDF toàn văn lưu trữ](https://static.aminer.org/pdf/PDF/001/122/204/qos_routing_in_networks_with_inaccurate_information_theory_and_algorithms.pdf) |
| Mức kiểm | 2026-09-23: PDF 14 trang, đối chiếu lượt 2 vào §I–V, Proposition III.1, các heuristic §IV và kết luận; chưa kiểm mọi chứng minh Appendix |
| Lượt đối chiếu nguồn | 2; lượt đầu abstract, lượt sau PDF §I–V ngày 2026-09-23 |
| Mức đe dọa | Cao cho claim routing dưới state bất định và state aging; không có bằng chứng về selective calibrated gate |

**[F] Vấn đề.** §I-B chỉ ra update ngưỡng/định kỳ khiến true link state lệch khỏi quảng bá; mức bất định có thể được mô hình hóa từ cơ chế update. Tác giả chọn path có xác suất thỏa QoS cao nhất khi metric không chính xác, không giả định controller luôn biết state thật (§I-C).

**[F] Phương pháp.** Với bandwidth-only, §II biến xác suất thành link weights để tìm path phù hợp. Với end-to-end delay, rate-based và delay-based models ở §III–IV gặp các bài toán khó tính toán; Proposition III.1 nêu NP-complete cho R-D, §IV nêu NP-hard cho phiên bản delay-based. Paper đưa special cases và heuristic chia constraint/đường phân cấp. Từ “margin” xuất hiện ở §IV cho *slack của delay constraint*, **không phải top-2 path-cost margin**.

**[F] Phạm vi.** §I nêu mục tiêu chọn đường cho new flow; cân bằng resource utilization/admission có thể là tiêu chí khác nhưng nằm ngoài mục tiêu chính. §V nêu việc suy ra phân phối sai số network state thực tế còn mở. Không thấy một calibration-set finite-sample guarantee hoặc quy tắc ABSTAIN/ACCEPT có selective risk target trong các § đã đọc; đây là kết luận giới hạn ở phần đã kiểm, chưa phủ toàn Appendix.

**[I] So với đề tài.** Không nhận “state cũ dẫn tới route sai” hoặc “dùng uncertainty để chọn route” là mới. Baseline từ paper là chọn path có estimated QoS-success probability cao nhất; muốn hiện thực phải ước lượng cùng probability model của bài. Khác biệt cần kiểm thực nghiệm là risk/regret của **relative route choice** theo telemetry age và top-2 estimated cost margin, cùng gate ACCEPT/ABSTAIN đã calibration; so thêm CERT age-aware route certificate.

**[?] Còn mở.** Đọc proof Appendix và conference version INFOCOM 1997; kiểm có threshold admission gián tiếp trong extension/citation khác; đối chiếu heuristic cụ thể với mô phỏng hiện tại trước khi code baseline.
