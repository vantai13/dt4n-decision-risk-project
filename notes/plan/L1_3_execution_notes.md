# L1.3 — Thực thi và giới hạn (2026-10-02)

Nguồn: attachment Lesson 1.3. Base commit d6d2551, nhánh rollout-v6.
Không có AGENTS.md bổ sung trong repo. Không sửa f08 đang mở trong IDE.

- Chạy n02 hai prior, n02b năm trường hợp gốc và win/inst thêm để tách nhiễu A.
- Các hàm world/twin_info/regret_of/regret có AST giữ nguyên từ attachment.
- Lưu seed metrics, contrasts/CI95 (cả bậc ba và Shapley), biểu đồ, báo cáo,
  kiểm thử, manifest và bảng so lesson. N2 dùng số local, ghi sai lệch.
- Sửa cách diễn giải neo: chỉ gần về regret, n02 không cùng chuỗi nhiễu bản tin
  với world gốc. Không tuyên bố neo bitwise L1.2 hoặc đồng nhất telemetry.
- Sửa “nhiễu A” trong lesson: noisy/inst còn bao gồm gộp A; đo riêng bằng win/inst.
- Thừa kế các giới hạn ideal W=1e-6 và OU liên tục vs world rời rạc ở L1.2.
- Giữ N-S2/N-S3 là đề xuất chờ tác giả. Kết quả dùng t, a=0,05 s cố định;
  không tự đổi chuẩn sang t+a hay xác nhận chu kỳ vận hành H=0,5 s là thực tế.
- Tạo realism_sources.md với ba giả định theo yêu cầu. Không có LUOT_1 bản gốc
  để sửa trực tiếp; các đính chính nằm trong N2.
- Kiểm literature ở mức abstract nhà xuất bản cho Owen/Song/Kennedy–O'Hagan,
  dẫn link trong N2; không claim đã kiểm mệnh đề không cộng tính của Howard.
- Chưa xác nhận tác giả tính trên giấy trước chạy hoặc hoàn thành tự kiểm.
  Bài tính Codex lưu sau chạy là đối chiếu từ các số đã công bố, không phải prereg.

Tái lập: xem experiments/results/n02_report.md. Nhật ký: notes/03_experiment_log.md.
