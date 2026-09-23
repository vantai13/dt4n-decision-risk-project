# Wang et al. 2026 — LEC, selection-conditioned risk control

| Trường | Giá trị |
|---|---|
| Tác giả | Zhiyuan Wang; Aniri; Tianlong Chen; Yue Zhang; Heng Tao Shen; Xiaoshuang Shi; Kaidi Xu |
| Nguồn | [arXiv:2512.01556v3](https://arxiv.org/abs/2512.01556); abstract ghi accepted ICML 2026 |
| Mức kiểm | 2026-09-23: PDF §3, Theorem 3.1–3.2, đầu §4; chưa đọc toàn bộ proof và experiments |
| Mức đe dọa | **Rất cao cho việc lấy `P(error | ACCEPT)` làm novelty phương pháp**; domain là model/intent routing |

**[F] Trust target.** LEC đặt `S=1` khi một output được chấp nhận, `err=1` khi sai, `Z=S·err`, rồi điều khiển `E[Z]/E[S]≤α` bằng ràng buộc tuyến tính `E[Z−αS]≤0` (§3.2, Eq. 1–4). Đây chính là loại mẫu số trên tập ACCEPT mà đề tài đang quan tâm. Nếu `E[S]=0`, guarantee rỗng; paper nêu rõ trường hợp này.

**[F] Method/guarantee.** Threshold được chọn trên calibration set bằng điều kiện hữu hạn mẫu với hiệu chỉnh `−1` (Eq. 5–7). Theorem 3.1 áp dụng cho một model; Theorem 3.2 cho hệ hai model, nơi input quá bất định ở model đầu được chuyển sang model kế rồi cuối cùng có thể abstain (§3.3). Cả hai theorem giả định calibration/test **exchangeable** và phát biểu xác suất marginal qua ngẫu nhiên của calibration set và test sample, dù điều kiện theo sự kiện ACCEPT.

**[I] So với đề tài.** Không claim “lần đầu kiểm soát selective risk trên ACCEPT”, “fallback/delegation có guarantee” hoặc “biến ratio thành linear expectation constraint” là mới. LEC route **input giữa các model**, không route packet/path qua graph, và không condition theo telemetry age/top-2 path-cost margin. Khác biệt đó phải được kiểm bằng đối chứng: một threshold LEC dùng chính score age+margin của đề tài, cùng calibration budget. Chuỗi thời gian OU không mặc nhiên thỏa exchangeability của LEC; cần blocked/time-aware evaluation hoặc phương pháp phù hợp.

**[?] Việc tiếp:** kiểm proof Theorem 3.1–3.2, độ nhạy khi ACCEPT hiếm và cách chọn threshold sau khi nhìn calibration; đối chiếu một baseline LEC-style với RQ2.
