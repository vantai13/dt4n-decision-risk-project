# Phase 0 v2 — Closeout (2026-09-25) · TRẠNG THÁI: ĐÓNG CÓ ĐIỀU KIỆN

## Gate

| Validity | Trạng thái |
|---|---|
| Tag `pre-pivot-v14`; lưu trữ v1; ADR PIVOT-v14; đính chính; provenance tài liệu AI | ✅ |
| Brief v2: RQ tách loại; H2 dùng chỉ số đảo thứ tự; RQ2 trục sai mô hình; kill criteria | ✅ (elevator test: ☐ G2) |
| Mục tiêu: memo + K2 ghi bằng chữ mẫu số của α; K3, K21 có phương án | ✅ (chờ GVHD: G1) |
| Definitions v2: mọi estimand đủ cột, không trùng tên | ✅ |
| Evaluation protocol v1: hai tầng; F lồng nhau; knowledge parity; thực tế ngoài họ | ✅ |
| Thuyết minh v15 + biên bản họp GVHD thật có quyết định | ☐ G1 |

## Điều kiện để gắn tag `phase-0v2-complete`

- **G1:** buổi làm việc với GVHD thật; K2, K3, K14, K15, K20, K21 và tiêu đề có quyết định hoặc hạn quyết định; biên bản trong 24 giờ.
- **G2:** elevator test với người thật; ghi nguyên văn vào brief mục 11.
- **G3:** D14 được giải quyết ở buổi họp G1.
- **Tồn đọng cũ (không chặn):** C4 — push `wip-before-archive` của dt4n, kiểm VM; hạn trước Phase 7.

## Outcome

- Gap: strong candidate (DP1-v2 sẽ kiểm full text và forward citation).
- Hai bẫy hiệu chỉnh (tiêu hết ngân sách, đổi vô ích) được phát hiện và sửa trước khi code (P02).
- sd(log s) không dự báo được khoảng cách; `rd_kappa` là ứng viên chính (P03).
- Tham chiếu ngẫu nhiên làm thứ hạng đảo khi chạy thật; dùng quỹ đạo hiện trạng (P04).
- Testbed là token bucket; token bucket khớp testbed, lệch trung bình 3,3% (P05).

## Mang sang Phase 1 (bắt đầu ngay, không chờ G1)

- **F1:** điểm neo dưới dạng Π; kiểm Π_noise (> 1 thì xem lại chữ "stale").
- **F2:** decision-level với tham chiếu hiện trạng; họ tĩnh tuyệt đối + tương đối; cả ba chỉ số H2; κ ∈ {0; 0,01}.
- **F3–F5:** ngân sách thống kê, chi phí tính toán, oracle bin trên F chính.
- **Đọc full text** danh sách DP1-v2; forward citation Seshadri–Katz, Fischer–Vöcking.
- **Điều kiện học tập:** tự viết lại lõi P02 (`odds_kkt`, `fixed_common`) không nhìn code, so md5 `79ff4171…`.

## Cập nhật 2026-09-25 — sau nhận xét GVHD: CHỜ G2

| Điều kiện | Trạng thái |
|---|---|
| G1: GVHD quyết định K2, K3, K14, K20, K21, phạm vi, SESOI, framing, lịch | ✅ nhận xét bằng văn bản (`meetings/2026-09-25_gvhd_feedback.md`); K15 còn mở, không chặn |
| G2: elevator test với người thật | ☐ chưa làm — tác giả phải ghi ngày và câu người nghe nhắc lại trong brief mục 11 |
| G3: D14 | ✅ hết hiệu lực |
| Tồn đọng C4 (dt4n) | mở, hạn trước Phase 7 |

Tài liệu Phase 0 đóng băng tới DP0 (20/10/2026); chỉ thêm dòng đính chính. Chưa gắn tag `phase-0v2-complete`
cho tới khi G2 có bằng chứng thật.

## Mang sang Phase 1 (thay danh sách cũ)

- **Điều kiện cứng:** tự dẫn công thức và giải thích từng dòng trước khi viết vào `ndtrisk/`.
- **Mốc 13/10:** F1 (điểm neo dưới dạng Π; X2 có khả thi không); tự dẫn lý thuyết nền (M/D/1/K bằng lát cắt, OU, mục tiêu K2);
  khoá m, r trước khi chạy F2.
- **F2 theo K2:** gain_ms, headroom_ms, ba chỉ số H2, c ∈ {0; 0,25; 1}·S; decision-level với tham chiếu hiện trạng.
- **F3:** số seed cho mục tiêu gain (đuôi nặng). F4, F5 như plan.
- **DP0 + DP1 (20/10):** đọc full text Seshadri–Katz, Burbano, Liyanage, Almohammedi, Fischer–Vöcking, OpenTwin v2, CERT, Lekeufack, Zhu.
- Y.1541 (12/2011) đã được kiểm là còn hiệu lực; RFC 5976 xác nhận Class 0 có loss ratio ≤ 10⁻³. Việc dùng mức tuyệt đối này
  làm ngưỡng chênh lệch δ vẫn là lựa chọn phân tích và phải được mô tả như vậy.
