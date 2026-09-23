# Bootstrap verification

Ngày chạy: 2026-09-23 (Asia/Saigon).

## Nguồn

- Repo nguồn: `https://github.com/vantai13/dt4n.git`
- Commit nguồn: `70d0e635b8189d20cdd5bae947257e0ff6c383a4`
- Cơ chế lấy file: `git show <commit>:<path>`; working tree chưa commit của repo cũ không được trộn vào snapshot.
- Ngoại lệ có chủ ý: novelty matrix `.xlsx` được bổ sung từ working tree theo Bước 5 của hướng dẫn.

## Kết quả chạy

Lệnh test:

```text
$ .venv/bin/pytest -q
..................                                                       [100%]
18 passed in 0.37s
```

Kiểm checksum dữ liệu:

```text
truth_table.parquet: OK
truth_table_report.json: OK
link_model_v2_fit.json: OK
```

Kiểm độc lập với snapshot cũ:

```text
PASS: no imports from reference/
```

Đọc dữ liệu calibration bằng pandas/pyarrow:

```text
rows=176 columns=14
modes=cbr,h2,poisson
rho_min=0.5000 rho_max=1.0400
truth_table.parquet bytes=19642
```

Kích thước repo sau `git gc`:

```text
du -sh --exclude=.venv . = 936K
content_only (không tính .venv/.git) = 660K
git_metadata = 276K
tracked_files = 49
```

Môi trường:

```text
Python 3.14.5
```

Danh sách phiên bản Python đầy đủ nằm ở `requirements-lock.txt`.

## File kết quả và ý nghĩa

| File | Kết quả chứa trong đó |
|---|---|
| `data/mininet_calibration/SHA256SUMS` | SHA-256 khóa 3 asset dữ liệu đo |
| `data/mininet_calibration/PROVENANCE.md` | repo, commit và đường dẫn nguồn của dữ liệu |
| `tests/test_data_assets.py` | kiểm checksum và schema/mode của truth table |
| `tests/test_margin.py` | 16 golden test cho decision margin |
| `requirements-lock.txt` | phiên bản dependency thực tế đã cài |
| `notes/00_research_brief.md` | problem, RQ1/RQ2, assumptions và kill criteria |
| `notes/04_bootstrap_verification.md` | báo cáo tổng hợp lần chạy này |

## Phần cố ý chưa làm

Repo `dt4n` nguồn đang có nhiều thay đổi chưa commit và đang chậm hơn `origin/main` 55 commit ở thời điểm kiểm tra. Vì vậy không tag/archive, không sửa README, không đổi tên thư mục nguồn và không push trạng thái đó. Đây là biện pháp tránh làm mất hoặc gắn sai provenance cho công việc đang dở.

Repo mới đã được `git init -b main`, commit local và gắn remote
`git@github.com:vantai13/ndt-decision-risk.git`. Push chưa thành công vì máy hiện tại
không có GitHub CLI và GitHub từ chối SSH key với lỗi
`Permission denied (publickey)`. Cần tạo repo private trên GitHub và cấu hình thông tin
xác thực trước khi chạy lại `git push -u origin main`.
