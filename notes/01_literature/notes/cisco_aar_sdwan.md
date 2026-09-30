# Cisco SD-WAN — Application-Aware Routing (tài liệu gốc)

| Trường | Giá trị |
|---|---|
| Tiêu đề | Policies Configuration Guide for vEdge Routers, Cisco SD-WAN Release 20 — chương Application-Aware Routing |
| Nguồn | cisco.com/c/en/us/td/docs/routers/sdwan/configuration/policies/vedge-20-x/policies-book/m-application-aware-routing.html |
| Trạng thái | tài liệu nhà cung cấp, không bình duyệt; trang ghi cập nhật 26/08/2022 |
| Lượt đã đọc | toàn chương, 2026-09-30 — Claude (AI) đọc và soạn; tác giả kiểm |
| Vai trò | mô tả THỰC HÀNH đo và đổi đường; KHÔNG phải bằng chứng khoa học về hiệu năng |

## 1. Hệ thống làm gì (lời của tôi)
- [F] Đo: phiên BFD tự chạy trên MỌI tunnel; Hello mặc định 1 s; loss/latency/jitter lấy từ Hello.
- [F] Tổng hợp: mỗi poll interval (mặc định 10 phút ≈ 600 Hello) tính trung bình; giữ 6 bucket (cửa sổ trượt).
- [F] Quyết định: lớp SLA dùng multiplier poll gần nhất (mặc định 6 ⇒ 1 giờ); mặc định chọn để damping, chống đổi lớp liên
  tục; multiplier = 1 để phản ứng nhanh.
- [F] Luật chọn: ngưỡng SLA tuyệt đối; nhiều tunnel đạt ⇒ chia tải hoặc màu ưu tiên; không tunnel nào đạt ⇒ best-of-worst
  với dải "variance" (ví dụ 5 ms) coi các tunnel gần nhau là ngang nhau.
- [F] Dampening (từ 20.5.1): tunnel dao động bị loại khỏi lớp SLA trong damp-multiplier × poll interval.
- [F] Đo thụ động (SAIE) dựa trên lưu lượng thật ⇒ [I] path đang mang lưu lượng có thể có nhiều thông tin hơn path rỗi.

## 2. Ý nghĩa cho đề tài
- Họ luật tĩnh + damping (ngưỡng, hold-down, dải dung sai) là thực hành thật ⇒ baseline có căn cứ.
- F7a: mặc định path phụ KHÔNG bị đo thưa hơn (BFD mọi tunnel cùng chu kỳ) ⇒ tiền đề cần nguồn khác. F7b không ảnh hưởng.
- Thang thời gian: mặc định 10–60 phút, cấu hình được xuống giây; đề tài (W = 0,5 s) ứng với cấu hình phản ứng nhanh —
  ghi vào phạm vi.
