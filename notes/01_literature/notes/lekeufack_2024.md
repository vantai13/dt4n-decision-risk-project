# Lekeufack et al. — Conformal Decision Theory

| Trường | Giá trị |
|---|---|
| Tác giả | Jordan Lekeufack; Anastasios N. Angelopoulos; Andrea Bajcsy; Michael I. Jordan; Jitendra Malik |
| Nguồn | [arXiv:2310.05921v3](https://arxiv.org/abs/2310.05921), bản 02/05/2024 |
| Trạng thái | Preprint đang đọc; chưa xác nhận venue |
| Mức kiểm | 2026-09-23: PDF §III–IV, Theorem 1 và đầu §V; phần batch và toàn bộ experiment chưa kiểm sâu |
| Lượt đối chiếu nguồn | 2; lượt sau kiểm lại giả định eventually safe và Theorem 1 trong PDF ngày 2026-09-23 |
| Mức đe dọa | Cao cho claim “calibrate trực tiếp decision risk/fallback” |

**[F]** Bài điều chỉnh tham số `λ_t` của họ decision functions theo loss của hành động sau khi outcome xuất hiện, thay vì bắt buộc tạo prediction set trước (§III–IV). Loss giả định bị chặn trong `[0,1]`; Theorem 1 cho cận **empirical average loss qua tất cả bước** `≤ ε + O(1/t)` dưới điều kiện *eventually safe* cho một mức tham số bảo thủ (§IV). Dữ liệu có thể không i.i.d., nhưng điều kiện eventually safe và quan sát loss vẫn cần thiết.

**[F]** Abstract nêu ví dụ chuyển từ nominal policy sang safe backup policy; §V có robot navigation, trading và manufacturing. Đây là nền trực tiếp cho action gate/fallback, không chỉ prediction calibration.

**[I] So với đề tài:** RQ2 không thể claim cấu trúc ACCEPT/ABSTAIN + fallback hoặc direct decision-loss calibration là mới. Cần đưa direct online decision-risk controller làm baseline khi có thể quan sát loss sau quyết định. Theorem 1 không tự bảo đảm `P(harmful | ACCEPT)≤α`: mẫu số của nó là toàn bộ bước và loss của action thực thi. Nếu fallback che đi cost của path bị từ chối, phải nêu rõ counterfactual label đến từ simulator hay từ logged/off-policy data.

**[?] Còn mở:** kiểm các experiment và batch theorem chi tiết; xác định một họ quyết định có “eventually safe” trong routing theo budget ε của đề tài hay không.
