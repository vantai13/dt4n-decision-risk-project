# Biên bản MÔ PHỎNG — buổi làm việc Phase 0 v2 (2026-09-25)

> Claude (AI) đóng vai GVHD theo yêu cầu tác giả. KHÔNG phải quyết định học vụ. Mọi mục là đề xuất đã qua phản biện,
> trình GVHD thật (TS. Huỳnh Văn Đặng) ở buổi làm việc đầu tiên. D14 giữ hiệu lực tới buổi đó.
> Tài liệu dùng: brief v2, 06_definitions v2, 05_evaluation_protocol v1, objective memo, P02–P05.

| # | Câu hỏi | Phản biện chính | Đề xuất sau phản biện | Điều kiện |
|---|---|---|---|---|
| Q1 | Mục tiêu (K2) | "Người dùng cảm nhận delay trung bình" | (b), α = 1%, KKT, κ trong J | Báo "giá của an toàn" (ms), harmful_per_switch |
| Q2 | Loss (K3) | "δ = 1% lấy từ đâu?" | Nhãn riêng, δ = 1 điểm % | Quét {0,5; 1; 2}; nguồn phải mở được |
| Q3 | κ (K21) | "κ không có nguồn vận hành" | κ = 0,01 | κ = 0 bắt buộc ở e03 |
| Q4 | Mininet (K14, K20) | "Port pipeline sang Mininet mất 2–3 tuần" | X1′ token bucket trong DES là thực tế ngoài họ chính (P05: lệch 3,3% so với 57% của M/D/1/K); Mininet xác nhận ≤ 2 cấu hình | X1′ tái lập P05 ở Phase 3 |
| Q5 | Phạm vi | "13 baseline là quá nhiều" | Lõi 16 ô, 8 luật, M1 + X1′ | Ưu tiên 2: H2, jitter tuổi |
| Q6 | SESOI | "Người vận hành không hiểu điểm %" | Giữ bản nháp brief | Khoá ở DP0; kèm quy đổi ms |
| Q7 | Tiêu đề | — | Tên đã đăng ký + phụ đề "Trường hợp quyết định đổi hay giữ đường" | Hỏi thủ tục khoa |
| Q8 | Đầu ra (K15) | "Đồ án và NCKH dùng chung kết quả?" | Báo cáo NCKH bắt buộc; paper quyết định ở DP2 | Hỏi quy định dùng chung |
| Q9 | "Stale" | "Π_noise = 5,78 ở 4 Mb/s" | Kiểm ở DP0 | Π_noise tại điểm neo > 1 → "cũ và nhiễu" |
| Q10 | Hiểu bài | "P02–P05 do AI viết" | Tự viết lại lõi P02; elevator test | Trước DP0 |
| Q11 | Hồ sơ | "Quy trình đang phình" | K23: ADR chỉ khi đổi RQ/H/metric/baseline/dữ liệu/F | — |
| Q12 | Lịch | "Tuần 1 sắp hết" | F1 bắt đầu ngay; DP0 giữ 13/10/2026 | — |
