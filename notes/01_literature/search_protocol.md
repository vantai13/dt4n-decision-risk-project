# Phase 1 / Lesson 1.2 — protocol cho đợt tìm tiếp theo

Chốt lúc 2026-09-23 18:24 +07:00. Đây là **đăng ký muộn**: OpenTwin và lượt tìm thăm dò 2026-09-23 đã xảy ra trước thời điểm này; lịch sử nằm trong `search_log.md`. Commit của file này phải đứng trước các truy vấn mới được đánh dấu `F` trong log, không dùng làm bằng chứng cho các truy vấn cũ.

## Phạm vi

- **I1:** quyết định routing/control dưới state cũ, trễ hoặc bất định.
- **I2:** gate, abstention, fallback hoặc certificate cho quyết định.
- **I3:** age/freshness/feedback delay có hệ quả định lượng lên quyết định hoặc coverage.
- **I4:** conformal/calibration online khi feedback trễ hoặc dữ liệu phụ thuộc thời gian.
- **E1:** chỉ dự báo state, không có quyết định hay calibration; ngoại lệ: họ D nền.
- **E2:** chỉ tối ưu lịch update, không liên hệ sai số hoặc task; ngoại lệ: họ D nền.
- **E3:** không có full text tiếng Anh: chỉ giữ metadata/abstract và đánh dấu chưa đủ cho kết luận novelty.

Phân loại: **rất gần** nếu có route/action trust dưới dữ liệu cũ, hoặc đúng C-a/C-b; **gần** nếu thỏa ít nhất hai I; **nền** nếu thỏa một I cần cho lý thuyết/baseline. C-a: tuổi/thang nhớ cùng margin giải thích routing flip/regret. C-b: age/horizon-conditioned conformal/ACI cho accept/abstain/fallback. Luôn tách telemetry age lúc quyết định khỏi label-feedback delay.

## Nguồn, cách đếm, điều kiện dừng

Đợt formal `F` dùng 8–12 truy vấn trên arXiv API, ghi nguyên văn query và tham số; có thể bổ sung IEEE/ACM/nguồn khác nếu chúng trả danh sách và tổng đếm. Với mỗi truy vấn: tổng do nguồn trả → số tiêu đề xét/qua → số abstract xét/qua; ghi danh sách ID ứng viên và lý do loại. Không điền số từ ước đoán của giao diện web. Tìm nguồn ngoài arXiv bằng snowballing từ Guérin–Orda (A), OpenTwin (F), El Halabi–Brandt (E), Ornee–Sun (D), cộng CERT là đối thủ bổ sung. Mỗi start set: backward và forward, ghi số thực sự truy xuất/xét/giữ và giới hạn nguồn.

Time-box: 5 ngày làm việc kể từ 2026-09-23, kết thúc 2026-09-30. Dừng khi một vòng backward + forward trên cả bốn start set không thêm bài **rất gần**, hoặc hết time-box; nếu một nguồn/API không truy cập được, ghi tình trạng và backlog, không gọi đó là saturation. Kết luận novelty/DP1 chỉ sau khi kiểm full text của mọi bài **rất gần** và các bài bắt buộc.
