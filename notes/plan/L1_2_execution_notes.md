# L1.2 — Ghi chú thực hiện (2026-10-02)

Nguồn: attachment “Lesson 1.2: Từ dự báo đến phán quyết, thế nào là sandbox đúng?”.
Script lõi/N1 từ lesson ghi Claude; Codex thực thi, xuất số liệu, audit và viết báo cáo.
Base local c41cf7e; không có AGENTS.md bổ sung trong repo.

- Tạo/chạy n01 (không RNG), n01b (9101–9110, H=0,5/5/30), n01c (9101, 300 cặp).
- Thêm neo age bên cạnh rhohat/G_true; xuất metric theo seed/pooled, raw epoch,
  CSV 300 cặp, đối chiếu bảng lesson, hình phân rã và manifest SHA-256.
- Thêm n01_audit_ideal và n01_report để kiểm/sinh báo cáo. Không sửa hàm trong
  ndtrisk/, experiments/scan/ hoặc engine f04b. Đây là lệch bổ sung so với lesson.
- L1.2 đã cung cấp outcome trước khi chạy: không gọi dự đoán là tiền đăng ký mù.
- Không tìm thấy bản gốc LUOT_1 để sửa trực tiếp; thay đổi thiết kế ghi trong N1.
- Giữ n01b theo đúng công thức lesson, không sửa numerical posterior để ép số
  bảng lesson. Nguyên bản n01b được chạy lại trên 30 tổ hợp và so bitwise với raw local.
- Bảng lesson khác số ideal local: xem n01_lesson_comparison.csv. Có phép audit
  cửa sổ đo rất nhỏ; chưa xác định nguyên nhân khác biệt bên soạn lesson.
- Regret là trung bình ms/lần kiểm, không phải tổng; không phụ thuộc ε. 13,06%
  là toàn vùng thờ ơ, chỉ 6,44 điểm % của I<0 nằm trong vùng thờ ơ âm.
- CRN trong n01c so hai chế độ có thêm gói từ warm-up, chưa phải can thiệp tại t.
  Ngoại ứng trên B đo bằng probe; chưa triển khai mục tiêu chính nhóm chuyển Δρ>0.
- H và mốc lý tưởng là đề xuất nháp chờ tác giả. Ví dụ mô phỏng không cung cấp
  bằng chứng về nhịp vận hành thực tế. Lựa chọn N0 đã có không thay đổi.
- Phần tác giả tính trên giấy/tự kiểm vẫn để trống, không gán việc của AI cho tác giả.

Lệnh chính và link kết quả: experiments/results/n01_report.md.
Các đề nghị sửa kế hoạch (N-3, phân rã regret, H, bộ sinh, bất đối xứng,
trạng thái đầy đủ của ideal DES) đã phản ánh trong N1 cùng giới hạn local.
