# Nguồn gốc dữ liệu đo (tầng B — realism)

Các file ở đây được lấy NGUYÊN VẸN từ dự án cũ và là **read-only**.
Không sửa. Nếu cần biến đổi, viết code đọc chúng và ghi output ra chỗ khác.

| Mục | Giá trị |
|---|---|
| Repo nguồn | https://github.com/vantai13/dt4n.git |
| Commit nguồn | `70d0e635b8189d20cdd5bae947257e0ff6c383a4` |
| Ngày lấy | 2026-09-23 |
| Checksum | xem `SHA256SUMS` (được kiểm bởi `tests/test_data_assets.py`) |

| File | Đường dẫn trong repo cũ | Ý nghĩa |
|---|---|---|
| truth_table.parquet | results/LIVE/phase-20R/truth_table.parquet | Queue delay + loss **đo trên Mininet** theo (traffic mode ∈ {cbr, poisson, h2}) × (bw, queue) × ρ. 176 dòng. Dùng làm hàm "delay thật" cho biến thể realism. |
| truth_table_report.json | results/LIVE/phase-20R/truth_table_report.json | Báo cáo cách bảng được dựng (script build_truth_table.py). |
| link_model_v2_fit.json | results/LIVE/phase-L/link_model_v2_fit.json | Mô hình twin đã fit trên dữ liệu Phase L (dùng cùng reference/dt4n_snapshot/link_model_v2.py). |

Dữ liệu RAW (CSV sweep, trace Phase 20) KHÔNG được mang sang; chúng vẫn nằm trong
repo cũ tại `results/RAW/` và `results/SUPERSEDED/calib/` ở commit trên.

## Kiểm lại ngày 2026-09-23

Checksum của cả 3 file trùng với nội dung tại tag local `archive-2026-09`
(commit `d45cf4ff26d8c6204a181f0fa77887e087a4d381`), tức dữ liệu không đổi từ
`70d0e635` tới trạng thái cuối hiện có trên `origin/main` của dt4n. Tag đang chờ
push vì máy kiểm tra chưa có xác thực GitHub.
