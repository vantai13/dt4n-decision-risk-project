# Decision log

| Ngày | Quyết định | Lý do | Thay thế đã cân nhắc |
|---|---|---|---|
| 2026-09-23 | Tách sang repo mới; repo dt4n archive tại `70d0e635b818` | Lõi khoa học ~1.2k dòng bị chìm trong ~150k dòng quy trình | Dọn dẹp tại chỗ (rủi ro kéo theo nợ cũ) |
| 2026-09-23 | Simulation là evidence chính; Mininet chỉ để validation | Thí nghiệm nhân quả cần biết ground truth và vặn tham số độc lập | Tiếp tục ép Mininet sinh tải có kiểm soát (S19–S25) |
| 2026-09-23 | ĐÍNH CHÍNH dòng 2026-09-23 ("repo dt4n archive tại `70d0e635b818`"): khi đó CHƯA archive. `70d0e635` là commit nguồn của snapshot, không phải điểm archive. Tag local `archive-2026-09` đã chuẩn bị tại commit `d45cf4ff26d8c6204a181f0fa77887e087a4d381`; push còn chờ xác thực GitHub. | Ghi chép đi trước thực tế (F0-1) | — |
| 2026-09-23 | Lấy lại `reference/` từ tag local `archive-2026-09` (5/10 file đổi). Dữ liệu giữ nguyên, checksum trùng tag. | Snapshot cũ lấy từ commit chậm 243 commit so với GitHub; con số "55" trước đó được tính trên `origin/main` chưa fetch (F0-2) | Giữ snapshot `70d0e635` (bỏ lỡ các sửa lỗi DEFAULT_TAU, perfect-twin, số block conformal) |
| 2026-09-23 | Tên repo chính thức hiện tại: `dt4n-decision-risk-project`; remote `https://github.com/vantai13/dt4n-decision-risk-project.git` | Giữ tên đang tồn tại trên GitHub vì máy hiện tại không có xác thực để rename; đồng bộ tiêu đề README với remote (F0-4) | Đổi thành `ndt-decision-risk` khi có xác thực GitHub |
| 2026-09-23 | Novelty matrix đổi tên thành `novelty_matrix.xlsx`; test kiểm cấu trúc thay cho checksum | Tài liệu sống không khóa checksum; test cũ báo sai khi file được lưu bằng Excel | Giữ checksum (phải sửa hash sau mỗi lần cập nhật) |
| 2026-09-23 | Kiểm kê trước archive: laptop có 489 thay đổi/file được đưa vào commit `d387f4df6` trên nhánh local `wip-before-archive`; stash được neo tại nhánh local `wip-stash-before-archive`. VM `dt4n-research-01` không kiểm được vì máy hiện tại chưa đăng nhập `gcloud`. | Chain of custody ghi đúng phần đã kiểm; hai nhánh và tag còn chờ push do thiếu xác thực GitHub | — |
