# Almohammedi et al. 2026 — Phân xử xApp có theo dõi độ tin cậy của twin

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | Twin-Fidelity-Aware Resolution of Direct xApp Conflicts in Open RAN |
| Tác giả (đúng thứ tự của PHIÊN BẢN đang đọc) | Akram Almohammedi; Mohammed Balfaqih; Sam Darshi; Rami Langar; Wael Jaafar |
| Nguồn | arXiv:2607.22857v1 (24/07/2026) |
| Trạng thái | preprint; nộp IEEE TNSM (theo ghi chú arXiv) |
| Lượt đã đọc | 2 — toàn văn HTML §I–VIII, Eq. 1–13, Alg. 1, Table I–V; hình chỉ đọc chú thích |
| Ngày đọc | 2026-09-27 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | thấp cho RQ1; trung bình cho claim "fallback theo độ tin cậy twin" ở RQ2 (đã biết từ OpenTwin) |

Nhãn: [F] paper nói trực tiếp (có §/tr.) · [I] suy ra (ghi suy từ đâu) · [?] chưa kiểm

## 0. Five Cs (sau lượt 1)

- Category: thuật toán + mô phỏng system-level.
- Context: xung đột xApp trực tiếp trong O-RAN; baseline gần nhất là COMIX (chọn theo twin, không theo dõi độ tin cậy).
- Correctness: twin và mạng thật lấy từ cùng một mô hình, lệch là một offset d dB được tiêm vào (§VI-B); môi trường
  dừng trong mỗi lần chạy vì đường cong được tính trước [F §VI-B].
- Contributions (theo tác giả, §I): công thức hoá; bộ phân xử hard-switch theo độ tin cậy; đánh giá có drift.
- Clarity: tốt; thống kê cẩn thận.
- Quyết định: lượt 2 đủ.

## 1. Một câu: paper làm gì?

Bộ phân xử làm theo hành động twin đề xuất khi trung bình trượt của |tiện ích dự đoán − tiện ích quan sát| còn dưới
ngưỡng τ, và chuyển sang hành động tốt nhất từng quan sát trên mạng thật khi vượt ngưỡng.

## 2. Problem · Assumptions

- Problem [F §III–IV]: chọn hệ số trộn α ∈ {0; 0,05; …; 1} giữa hai đề xuất công suất phát; tối đa U = T − w_E·P_W.
- A1 [F §IV-D]: giai đoạn khởi động twin đã hiệu chỉnh (d = 0).
- A2 [F §IV-D]: điểm tối ưu biến đổi chậm hơn thang điều khiển.
- A3 [F §IV-D]: twin đánh giá được cả 21 hành động trong một chu kỳ.

## 3. Method

Mỗi bước: twin dự đoán Û cho 21 hành động và chọn argmax. Sau khi thực thi, tính e_t = |Û(α_t) − U_live(α_t)| và cập
nhật ε_t = β·ε_{t−1} + (1−β)·e_t (β = 0,7). Nếu ε ≥ τ (τ = 1) thì dùng hành động last-known-good (LKG) — hành động có
tiện ích thật cao nhất từng thấy. Theo ngôn ngữ đề tài: đây là **một ngưỡng tĩnh trên một tín hiệu độ tin cậy toàn cục**,
bảo vệ khỏi tâm bị lệch có hệ thống; không có bất định từng quyết định [I].

## 4. Evaluation

| Setup (topology/testbed/data) | Baseline | Metric | Kết quả chính (có số) | §/tr. |
|---|---|---|---|---|
| MATLAB 5G Toolbox, 7 cell, 42 UE; 20 seed; 40 bước (10 khởi động + 30 chính); drift d ∈ {0,…,10} dB | ES-only, CTO-only, naive blend, COMIX-style, QACM-style, Soft-ES, Soft-LKG | regret chuẩn hoá; QoS satisfaction; CI Student-t theo seed; hiệu paired | regret chuẩn hoá 0,017 ± 0,006 so với COMIX-style 0,159 ± 0,052 | §VI, Table III |
| Drift 10 dB, w_E = 0,1 | COMIX-style | regret | 0,55 ± 0,25 so với 11,19 ± 3,58 | §VII-B2 |
| Tối ưu ở biên, w_E = 1 | mọi luật | regret | các luật hội tụ về hiệu năng gần nhau | §VII-B3 |

## 5. Claim ↔ Evidence

| # | Claim của tác giả | Loại evidence | Evidence thật sự phủ tới đâu | Khe hở? | §/tr. |
|---|---|---|---|---|---|
| 1 | Theo dõi độ tin cậy cho độ bền dưới drift | thí nghiệm | Hiệu paired có CI loại trừ 0 ở mọi drift khác 0 với w_E = 0,1 | Chỉ một kiểu drift (offset công suất láng giềng) | §VII-B2, Fig. 8 |
| 2 | Không cần huấn luyện, không cần biết tối ưu | lập luận + thí nghiệm | τ chọn từ {1,…,5} theo regret TB trên toàn bộ lần chạy đánh giá | Có — chỉnh trên dữ liệu kiểm (nhẹ) | §VI-D |
| 3 | Không bị phạt khi không cần can thiệp | thí nghiệm | Minh hoạ ở w_E = 1 | Một cấu hình | §VII-B3 |

## 6. Limitation

- Tác giả tự nêu [F]: giả định khởi động hiệu chỉnh và tối ưu biến chậm; mở rộng tới xung đột gián tiếp, nhiều tham số,
  môi trường không dừng (§I, §VIII).
- Tôi thấy [I]: tiện ích thật của mỗi hành động là hằng trong một lần chạy — không có bất định ngẫu nhiên theo từng quyết
  định; drift chỉ là lệch có hệ thống; một loại xung đột.

## 7. So với đề tài của tôi

- Trùng: dùng twin để chọn hành động; lo ngại twin sai.
- Khác, ĐÃ KIỂM (§/tr.): bất định là lệch mô hình toàn cục theo thời gian (Eq. 6–8), không phải bất định từng quyết định
  do tuổi/nhiễu; không phải bài toán đổi/giữ đường; môi trường dừng trong run (§VI-B).
- Khác, CHƯA KIỂM / suy luận: cơ chế bảo vệ **tâm bị lệch**, nhất quán với phát hiện "giá trị nằm ở tâm" của đề tài [I].
- Dùng được: chuẩn thống kê (CI theo seed, hiệu paired, chỉ claim khi CI loại trừ 0 — §VI-E); baseline "fallback theo
  độ tin cậy" cho tầng 3 (dịch chuyển chế độ).

## 8. Câu định vị

"Almohammedi et al. gác twin bằng một tín hiệu độ tin cậy toàn cục khi twin lệch có hệ thống (Eq. 12, §IV-B); đề tài
xét câu hỏi khác — bất định thay đổi theo từng quyết định do tuổi và nhiễu của telemetry có nên thay ngưỡng cố định
không — và dùng cùng chuẩn so sánh paired theo seed."

## 9. Câu hỏi còn mở

- Cần đọc lại sau lesson nào: khi thiết kế tầng 3 (dịch chuyển chế độ, H3′).
