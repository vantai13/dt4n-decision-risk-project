# Zhang et al. 2026 — OpenTwin (v2)

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | [F metadata] OpenTwin: Closed-Loop Digital Twins for Trustworthy Policy Deployment in Open RAN |
| Tác giả (v2) | [F metadata] Zifan Zhang; Md Sharif Hossen; Dara Ron; Vijay K. Shah; Yuchen Liu |
| Nguồn | [F metadata] arXiv:2605.24662v2; DOI 10.48550/arXiv.2605.24662 |
| Trạng thái | [F metadata] preprint; v1 nộp 2026-05-23, v2 sửa 2026-08-28 |
| Lượt đã đọc | 1: □ · 2: □ · 3: chờ L1.5 (chỉ phần gate) |
| Ngày đọc | chưa đọc bởi tác giả |
| Mức đe doạ novelty | cao — cần tác giả tự xác nhận bằng full text |

Nguồn metadata: [trang arXiv v2](https://arxiv.org/abs/2605.24662v2). v1 có
tiêu đề và tác giả đầu khác; khi trích phiên bản đang đọc phải dùng Zhang et al.

Nhãn: [F] paper nói trực tiếp (có §/tr.) · [I] tôi suy ra (ghi suy từ đâu) · [?] chưa kiểm

## 0. Five Cs (sau lượt 1)

- Category:
- Context:
- Correctness (giả định có vẻ hợp lý?):
- Contributions (theo lời tác giả):
- Clarity:
- Quyết định: dừng / lượt 2 / lượt 3

## 1. Một câu: paper làm gì?

## 2. Problem · Assumptions (A1, A2, …)

## 3. Method (3–5 câu, bằng lời và ký hiệu của TÔI, không chép)

## 4. Evaluation

| Setup (topology/testbed/data) | Baseline | Metric | Kết quả chính (có số) | §/tr. |
|---|---|---|---|---|

## 5. Claim ↔ Evidence

| # | Claim của tác giả | Loại evidence (định lý / thí nghiệm / quan sát / lập luận) | Evidence thật sự phủ tới đâu | Khe hở? | §/tr. |
|---|---|---|---|---|---|

## 6. Limitation

- Tác giả tự nêu [F]:
- Tôi thấy [I]:

## 7. So với đề tài của tôi

- Trùng:
- Khác, ĐÃ KIỂM (§/tr.):
- Khác, CHƯA KIỂM / suy luận:
- Dùng được gì: method / baseline / metric / dataset / câu trích Related Work

## 8. Câu định vị

Chưa điền — tác giả cần tự đọc full text và dẫn §/trang.

## 9. Câu hỏi còn mở và bảng tương ứng biến

- Cần đọc lại sau lesson nào: L1.5 cho lượt 3 đầy đủ phần gate.
- Muốn hỏi tác giả / GVHD:
- Danh sách section và kiểm tra "§VI":

| Của tôi | Nghĩa | Tương ứng ở OpenTwin (§/tr.) — hoặc "không có" |
|---|---|---|
| z | tuổi telemetry tại lúc quyết định | |
| Ĉ_k | chi phí path theo twin | |
| m̂ | margin twin giữa top-2 | |
| s_pair | abs(m−m̂), score | |
| q̂ | quantile score trên calibration | |
| α | mức danh nghĩa | |
| ε | regret chấp nhận được | |
| ACCEPT/ABSTAIN + fallback | hành vi gate | |
| (ô trống) | biến của HỌ mà tôi không có | |

## Câu hỏi dẫn đường cho lượt 2

1. Gate lấy input gì; có age/timestamp/thời gian từ lần đo cuối không?
2. Score là sai số KPM hay đại lượng so sánh nhiều action?
3. Calibration lấy từ đâu, bao nhiêu mẫu, cửa sổ trượt hay cố định?
4. False approval dùng mẫu số nào; guarantee marginal hay per-action?
5. Guarantee là định lý hay thí nghiệm; giả định nào?
6. Gate có so sánh hai action không?
7. Từ chối thì mạng làm gì?
8. Baseline gồm gì; có always-trust không?

