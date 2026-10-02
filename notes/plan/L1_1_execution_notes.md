# L1.1 — Ghi chú thực hiện (2026-10-02)

Nguồn: attachment “Lesson 1.1: Câu hỏi của bạn nằm ở đâu trong hệ thống?”.
Bản lesson tự ghi provenance Claude; Codex thực hiện trên repo local.
Đây là ghi chú thực hiện, không phải bản gốc LUOT_1_NOVELTY.md.

- `git pull --ff-only`: Already up to date; nhánh `rollout-v6`, base `e669f5c`.
  Commit này khác `7c60c76` được nêu trong lesson; kết quả sẽ đối chiếu ở độ chính xác bài in.
- Chưa tìm thấy LUOT_1_NOVELTY.md hoặc kế hoạch 02/10 trong repo/tên attachment;
  không tạo nội dung giả thay cho hai kế hoạch đó.
- Tạo N0, chạy n00 với seed pilot 9101, lưu stdout + số liệu + báo cáo,
  ghi experiment log và commit theo yêu cầu. Không phải tiền đăng ký mù:
  các số mục tiêu đã xuất hiện trong lesson trước lần chạy local.
- L1.1 ở đây thuộc lượt novelty mới; không thay thế L1.1 cũ trong lịch sử repo.

## Các sửa đổi kế hoạch cần mang tới Gate N

1. Mô tả twin bằng mô hình + ánh xạ dữ liệu; kiểm lại phát biểu về tương tác
   thời gian thực bằng tài liệu gốc khi làm lượt literature.
2. `des_world`/f04b ghép PSA với DES, chưa phải hai nhánh can thiệp giữ/áp dụng.
3. Vẽ phản hồi hành động → tải bằng nét đứt, ghi chưa có trong mô hình cũ.
4. Đưa Δρ và đối tượng hưởng lợi vào N0; Δρ≈0 là đối chứng.
5. Bổ sung ứng viên Polverini NOMS 2023 vào danh sách L1.7 lượt 1;
   thông tin này theo lesson, chưa xác minh tài liệu gốc ở lần triển khai.
6. Ghi lệch kế hoạch: n00 gọi hàm cũ và xuất số liệu minh hoạ.

## Giới hạn thuật ngữ khi đối chiếu code

`posterior` là cập nhật Gauss với phương sai nhiễu đếm xấp xỉ bằng
ρ̄·S/W, trong khi `telemetry_view` sinh đếm Poisson có cường độ phụ thuộc tải.
Bởi vậy “cùng mô hình/tham số OU và cùng đường cong PSA” không chứng minh
hậu nghiệm chính xác hay sai mô hình bằng 0 theo mọi nghĩa.
Tuổi `world.age` tính từ cuối cửa sổ đo; khác ký hiệu z từ tâm cửa sổ
trong definitions v2.1. `posterior` nhận `age + a` và tích phân cả W, H.
