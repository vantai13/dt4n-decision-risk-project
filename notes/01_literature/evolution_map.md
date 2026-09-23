# Evolution map — các giới hạn dẫn tới câu hỏi nghiên cứu (2026-09-23)

Mũi tên biểu thị **bước chuyển về bài toán**, không khẳng định bài sau trích dẫn hay kế thừa trực tiếp bài trước. Mỗi cạnh nêu giới hạn của nút trước và nguồn cho bước chuyển; mức đọc cụ thể ở `search_log.md`.

## Mạng và quyết định

1. **Routing với link-state không chính xác** → **đánh giá tác động của stale link-state**. *Giới hạn:* một mô hình xác suất của state không tự giải thích ảnh hưởng của chu kỳ cập nhật lên blocking/setup failure; Guérin–Orda 1999 [§I–IV](https://static.aminer.org/pdf/PDF/001/122/204/qos_routing_in_networks_with_inaccurate_information_theory_and_algorithms.pdf), Shaikh et al. 2001 [PDF tác giả](https://www.cs.princeton.edu/~jrex/papers/qosroute.pdf). Cạnh này là đối chiếu chủ đề, **không phải quan hệ niên đại hoặc trích dẫn đã kiểm**.
2. **Stale-state routing** → **NDT action admission**. *Giới hạn:* đo hại do state cũ chưa cung cấp quy tắc chấp nhận một action theo predicted outcome safety; OpenTwin v2 [§VI, §VII-C](https://arxiv.org/abs/2605.24662) có conformal fidelity gate và drift detector. Đây là chuyển từ phân tích routing sang kiểm action trong O-RAN, không phải claim tiến hóa trực tiếp của một thuật toán.
3. **NDT action admission** → **route trust theo age và relative cost**. *Giới hạn:* gate của OpenTwin kiểm `C_t(a) ⊆ S` cho một action, chưa đo flip/regret giữa hai route ước lượng gần nhau; OpenTwin [§VI](https://arxiv.org/abs/2605.24662). Tuy vậy CERT đã có route certificate `LB≤OPT≤UB` dưới cost drift và age [§1–4](https://doi.org/10.31224/7306), nên đóng góp còn phải kiểm là vai trò `age × top-2 margin` trên selective harmful risk, với baseline CERT.

## Calibration và selective risk

4. **Split conformal** → **global ACI**. *Giới hạn:* coverage finite-sample chuẩn cần exchangeability, khó áp trực tiếp dưới drift; Gibbs–Candès [§2, Prop. 4.1](https://arxiv.org/abs/2106.00170) cho tần suất miscoverage dài hạn trên chuỗi, chưa có bảo đảm riêng từng age group.
5. **Global ACI** → **per-horizon ACI**. *Giới hạn:* một target chung không phân biệt các forecast horizon có thời điểm nhận nhãn và độ khó khác nhau; Hallberg Szabadváry [§3, Eq. 8–10](https://proceedings.mlr.press/v230/hallberg-szabadvary24a.html) cập nhật riêng theo horizon. Horizon dự báo không mặc nhiên bằng tuổi telemetry tại quyết định.
6. **Per-horizon ACI** → **delayed-feedback ACI diagnostic**. *Giới hạn:* chia theo horizon chưa mô tả tác động của delay so với memory của residual; El Halabi–Brandt [§2–4, §7.6](https://arxiv.org/abs/2609.07251) dùng `τ/L`, với hiệu lực khác nhau giữa AR(1), GARCH và Markov switching.
7. **Coverage/average decision risk** → **selection-conditioned risk**. *Giới hạn:* kiểm trung bình toàn bộ dự báo/quyết định không tự kiểm `P(error | ACCEPT)`; LEC [§3, Thm 3.1–3.2](https://arxiv.org/abs/2512.01556) đã kiểm ratio này dưới exchangeability cho model/intent routing. Vì vậy ACCEPT-conditional risk không thể nhận là ý tưởng mới; cần kiểm khi đối tượng là network path, telemetry cũ và chuỗi phụ thuộc thời gian.

## Freshness

8. **AoI** → **sai số ước lượng OU / AoII**. *Giới hạn:* tuổi thuần không cho biết state sai đến mức nào hoặc thông tin hiện có có đúng không; Ornee–Sun [abstract](https://arxiv.org/abs/1902.03552) tối ưu sampling/remote estimation OU, Maatouk et al. [abstract](https://arxiv.org/abs/1907.06604) đo tuổi của thông tin sai. Hai công trình này còn ở mức state/update, chưa đủ để kết luận risk của route được chọn.

**Điểm giao chưa khóa:** CERT đã phủ age-aware route certificate; LEC đã phủ risk trên ACCEPT; OpenTwin đã phủ NDT trust gate. Chưa được kết luận tính mới của `age × margin` trước khi kiểm PDF/proof CERT, Appendix Guérin–Orda và các mục snowballing còn lại.
