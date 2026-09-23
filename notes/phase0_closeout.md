# Phase 0 closeout — trạng thái chờ (2026-09-23)

**Chưa đóng Phase 0. Không được dùng file này để gắn tag `phase-0-complete`.**

Plan tham chiếu: PHASE_0 sha256 **chưa tính được** — file private không có trong
workspace đã kiểm. Không đưa plan private lên git chỉ để lấy hash; khi tìm thấy,
tính hash local rồi chỉ ghi chuỗi hash vào đây.

| Validity | Trạng thái | Bằng chứng / phần thiếu |
|---|---|---|
| Repo cũ archive, repo mới khớp thực tế | đạt có lưu ý | tag `archive-2026-09`; WIP bundle đã verify, một nhánh chưa push |
| Brief v1 + elevator test | **chưa đạt** | brief có; elevator test người thật chưa làm |
| Definitions + VD tự làm | **chưa đạt** | definitions có; VD7–VD8 hiện là lời giải agent, không phải bài tự làm |
| Design: W_ref không suy biến | đạt ở mức thiết kế | D12; design §1; pilot sanity 4 triệu mẫu |
| D2–D12 có ADR | đạt về tài liệu, D11 tạm thời | D11 còn chờ CFP 2027 và GVHD; D12 đã chốt kỹ thuật |
| GVHD đồng ý research contract | **chưa đạt** | chưa có cuộc họp/biên bản thật |

| Outcome | Ghi lại |
|---|---|
| Venue chính / dự phòng | đề xuất CNSM 2027 / GLOBECOM 2027; chưa được GVHD chốt |
| Ngày muộn nhất xong thí nghiệm | chưa thể tính vì CFP 2027 chưa công bố |
| Quyết định của GVHD | chưa có |
| Số claim confirmatory dự kiến | tối đa 6; contrast cụ thể chưa đăng ký |

## Mang sang Phase 1 khi gate đạt

- Đọc/kiểm full text các paper gần nhất và cập nhật novelty bằng bằng chứng trực tiếp.
- Tự dẫn luật Gaussian và điều kiện conditioning/selection cho K=2 rồi K>2.
- Chỉ bắt đầu implementation simulator sau khi các validity còn thiếu được xác nhận.

