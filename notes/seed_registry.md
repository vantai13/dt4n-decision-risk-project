# Sổ đăng ký seed

Cập nhật 2026-10-01; nền commit `8876e12`. “Đã xem” là có output outcome
được đọc; tái lập bằng seed đó không trở thành xác nhận độc lập.
Các dải mới được kiểm bằng `rg -n '\b9[2-5]0[0-9]{2}\b' experiments notes tests`
trước khi thêm sổ này: không có kết quả khớp.

| Dải seed | Mục đích | Trạng thái | Commit / bằng chứng |
|---|---|---|---|
| 9001–10000; 11001–11932 | pilot, lý thuyết, F2–F8; nhiều dải con | lịch sử, không coi fresh; dải bao không ngụ ý mọi seed đã dùng | notes/03_experiment_log.md |
| 30001–30020 / 20001–20020 | confirm, frontier; explore anchor | đã dùng, đã xem | 66f972c; confirm.py |
| 60001–63020 | map và xác nhận cơ chế, các dải con | lịch sử, không coi fresh | notes/03_experiment_log.md; results/map/ |
| 70001–70008 / 71001–71008 | explore_width map | đã dùng, đã xem | cb7d6f4; explore_width.py |
| 72001–72020 / 73001–73020 | explore_width validation | đã dùng, đã xem | cb7d6f4; explore_width.py |
| 80001–80020 / 81001–81020 | GO v0, GO switch v1; GO-check tái lập và info validity | đã dùng, đã xem FIX; SYM/FF chỉ kiểm validity | dc72a77, 7c60c76; results/gocheck/ |
| 86001–86020 / 87001–87020 | rollout v2/v3 | đã dùng, đã xem | 634e133; rollout_v2.py |
| 86001–86020 / 89001–89020 | rollout v4/v5 | đã dùng lại calibration, đã xem test | 634e133, 8f0c899 |
| 90001–90020 / 91001–91060 | rollout v6, R3_outage | để dành; protocol draft, chưa mở | 8876e12; rollout_v6_protocol.json |
| 92001–92020 / 93001–93020 | GO-check Bước 1, R1 | đã xem sandbox và đã tái lập local, không còn fresh | khóa cấu hình local 9272119; fresh_output.txt |
| 94001–94020 / 95001–95020 | GO-check Bước 2 FIX/SYM/FF cùng thế giới | đã xem sandbox và đã tái lập local, không còn fresh | khóa cấu hình local 9272119; info_outcome_output.txt |
| 99001–99002 / 99101–99102 | smoke info-arrangement trong sandbox Claude | nguồn nói đã dùng, output xóa chưa đọc; local chưa kiểm độc lập | PREDICTIONS_claude.md |

Không dùng seed mới làm smoke test. Cập nhật trạng thái và commit kết quả sau
mỗi lần mở outcome. Seed bổ sung nằm trong RNG riêng `[seed, 424242]` không
phải một tập test độc lập.
