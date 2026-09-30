# Phase 1 v2 — Closeout (BẢN NHÁP 2026-09-30; hoàn tất sau họp 20/10) · TRẠNG THÁI: CHỜ DP0 + DP1

## Gate (chi tiết: F6 v2 Phụ lục C)
| Validity | Trạng thái |
|---|---|
| Sở hữu (Phần A) | ⚠️ một phần; xử lý theo quyết định GVHD 20/10 |
| Lý thuyết T4, T5 + script | ⚠️ AI soạn, tác giả kiểm (được phép) |
| κ̂ khoá trước f05c | ✅ nội dung · ⚠️ thời điểm commit (ghi log) |
| F7: tiền đăng ký, anchor, validity, cổng | ✅ |
| F8: cổng outcome | ❌ ô T10/FH — không diễn giải (đúng luật) |
| Literature L1.10 | ⚠️ Seshadri–Katz forward citation chưa; SD-WAN chỉ tài liệu Cisco |

## Outcome
- DP0: PIVOT (claim VoIP giữ nguyên) · DP1: NARROW — theo biên bản 20/10.
- Phân rã headroom: thông tin 59–84%, an toàn 6–14%, tâm 1–4%, độ rộng thuần ≤ 1,5% (F7).
- Luật bậc hai phân giải lần đầu (AA: 0,063 ± 0,023 ms so với dự đoán 0,051).
- Oracle bin không luôn là cận trên (F8) ⇒ K10′.
- Tiền lệ: Veeravalli–Kelly 1997; Jewson 2003 (positioning v2).

## Sai lệch đã ghi
- Phần A làm một phần trước F7 (log 30/09).
- Mục (12) của f08 thêm sau khi trợ lý thấy validity sandbox — chỉ phần báo (log 30/09).
- f02–f08 giữ nhãn lưới 251 điểm và K·S thay NaN để neo bit-exact; n_nan = 0 mọi run F7, F8 (definitions v3 Phần 4).

## Mang sang Phase 2
- Việc đầu tiên: kiểm tính mới RQ-I (họ VoI / thiết kế telemetry) ⇒ DP-I.
- Tiền đăng ký RQ-W, RQ-I trên seed test 20000–29999 và oracle 30000–39999 (chưa từng dùng).
- `ndtrisk/`: tích phân chính xác + NaN; twin trên trạng thái (backlog, tải); oracle kiểm trên seed giữ riêng (K10′).

## Tag
`phase-1v2-complete` gắn SAU khi biên bản 20/10, ADR và bảng trạng thái đã commit.
