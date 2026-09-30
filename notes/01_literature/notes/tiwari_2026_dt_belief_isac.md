# Tiwari et al. 2026 — DT dựng belief state từ telemetry trễ (ISAC)

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | Digital Twin-Assisted Belief-State Reinforcement Learning for Latency-Robust ISAC in 6G Networks |
| Tác giả | Himanshu Tiwari; Binayak Kar; Priyanshu Tiwari |
| Nguồn | arXiv:2604.25967v1 (HTML) |
| Trạng thái | nhận ở workshop IEEE INFOCOM 2026 (ISAC-FutureG) theo ghi chú arXiv; 6 trang |
| Lượt đã đọc | 2 — toàn văn §I–V; hình chỉ đọc chú thích |
| Ngày đọc | 2026-09-30 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | thấp — twin đặt giá trị vào dự báo tâm tới hiện tại; không đo độ rộng so với ngưỡng đã tune |

Nhãn: [F] · [I] · [?]

## 0. Five Cs
- Category: đề xuất hệ thống + mô phỏng. Context: điều khiển ISAC tập trung (O-RAN), PPO.
- Correctness: trễ ~ N(50 ms, 15 ms) cắt tại 0 (§III-B, Table II); EKF vận tốc không đổi (§III-C); một cấu hình
  3 BS / 6 UE / 3 mục tiêu (Table II).
- Clarity: tốt; báo trung vị, không thấy số lần chạy hay CI trong phần đã đọc (§IV).
- Quyết định: lượt 2 đủ.

## 1. Một câu
Twin gom telemetry có tem thời gian, dùng EKF dự báo trạng thái tới lúc quyết định, rồi PPO hành động trên trạng thái
dự báo thay vì trên số đo cũ.

## 2. Problem · Assumptions
- A1 [F §III-B, eq. 6–7]: quan sát trễ ngẫu nhiên, có nhiễu đo.
- A2 [F §III-C, eq. 9–12]: động học tuyến tính vận tốc không đổi, nhiễu Gauss.
- A3 [F eq. 13]: belief = ước lượng EKF của mọi UE/mục tiêu + chỉ báo kênh dự báo.
- [I] Không thấy hiệp phương sai EKF trong đầu vào policy ⇒ "belief" ở đây là TÂM.

## 3. Method
Bộ đệm telemetry → chọn số đo mới nhất đã tới → EKF predict/update tới thời điểm t → PPO (actor–critic) xuất công suất
liên lạc, công suất cảm biến, góc beam, có ràng buộc tổng công suất (Alg. 1).

## 4. Evaluation
| Setup | Baseline | Metric | Kết quả chính | § |
|---|---|---|---|---|
| khép vòng, trễ 0–100 ms | DRL không biết trễ; PPO trên quan sát trễ; DT-only; convex/heuristic | throughput, MSE | 50 ms: throughput trung vị +12% vs DT-only, >40% vs PPO trễ; MSE −7% / −24% | §IV-C |
| như trên | như trên | giữ throughput | 100 ms: 88% · DT-only 86% · PPO trễ 58% · DRL 43% | §IV-D |
| như trên | như trên | xác suất vi phạm | ~ một bậc thấp hơn DT-only ở 50 ms | §IV-G |

## 5. Claim ↔ Evidence
| # | Claim | Loại | Phủ tới đâu | Khe hở? | § |
|---|---|---|---|---|---|
| 1 | Belief-state PPO bền với trễ | mô phỏng | một cấu hình, trung vị | Có — không CI | §IV |
| 2 | Lợi ích nhờ đồng bộ belief | mô phỏng | DT-only đã giữ 86% vs 88% | [I] phần lớn lợi ích nằm ở dự báo tâm | §IV-D |

## 6. Limitation
- Tác giả [F §V]: kênh không dừng; hệ lớn hơn.
- Tôi thấy [I]: không tách dự báo tâm với học policy; không oracle; không so luật ngưỡng đơn giản trên belief.

## 7. So với đề tài
- Trùng: telemetry trễ → twin dự báo tới hiện tại → quyết định (kênh tâm, Z loại (b), T4 §1).
- Khác, ĐÃ KIỂM: hành động liên tục, không đổi/giữ; không ngân sách harm; không oracle (§III–IV).
- Dùng được: lý do cho baseline forecast-to-now; câu Related Work.

## 8. Câu định vị
"Tiwari et al. đặt giá trị của twin vào dự báo trạng thái tới lúc quyết định (§III-C) và không tách phần đó khỏi phần
do policy học (§IV-D); đề tài đo đúng sự tách này cho đổi/giữ đường với oracle cùng thông tin."

## 9. Câu hỏi mở
- Policy có dùng hiệp phương sai EKF không? (không thấy trong eq. 13)
