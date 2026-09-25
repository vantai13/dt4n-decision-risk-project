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
