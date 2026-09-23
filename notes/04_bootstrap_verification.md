# Bootstrap verification

Ngày chạy: 2026-09-23 (Asia/Saigon).

## Nguồn

- Repo nguồn: `https://github.com/vantai13/dt4n.git`
- Commit nguồn: `70d0e635b8189d20cdd5bae947257e0ff6c383a4`
- Cơ chế lấy file: `git show <commit>:<path>`; working tree chưa commit của repo cũ không được trộn vào snapshot.
- Ngoại lệ có chủ ý: workbook literature được bổ sung từ working tree theo Bước 5 của hướng dẫn. Bản Almasan-only ban đầu đã được thay bằng `Paper_Breakdown_DT4N_One_Comparison_Table_updated.xlsx` (9 sheet, có `Novelty Matrix`; SHA-256 `2736294d1f04909d134042c9ac2f1d905e79853fa92d15f86a5f8d5c9eae2a73`).

## Kết quả chạy

Lệnh test:

```text
$ .venv/bin/pytest -q
....................                                                     [100%]
20 passed in 0.96s
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
du -sh --exclude=.venv . = 1.1M
content_only (không tính .venv/.git) = 712K
git_metadata = 344K
tracked_files = 50
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
| `notes/01_literature/Paper_Breakdown_DT4N_One_Comparison_Table_updated.xlsx` | novelty matrix và breakdown các prior work |
| `notes/04_bootstrap_verification.md` | báo cáo tổng hợp lần chạy này |

## Phần cố ý chưa làm

Repo `dt4n` nguồn đang có nhiều thay đổi chưa commit và đang chậm hơn `origin/main` 55 commit ở thời điểm kiểm tra. Vì vậy không tag/archive, không sửa README, không đổi tên thư mục nguồn và không push trạng thái đó. Đây là biện pháp tránh làm mất hoặc gắn sai provenance cho công việc đang dở.

Repo mới đã được `git init -b main` và gắn remote chính thức:
`https://github.com/vantai13/dt4n-decision-risk-project.git`.

## Cập nhật 2026-09-23 (Lesson 0.1)

- Đính chính: "chậm origin/main 55 commit" được đo trên `origin/main` chưa fetch.
  Sau `git fetch`, `70d0e635` chậm `origin/main` 243 commit (`0 243`).
- Repo cũ: working tree được bảo toàn tại nhánh local `wip-before-archive`, commit
  `d387f4df694a95719ce5287b99a1246c0060de94`; stash được neo tại nhánh local
  `wip-stash-before-archive`. Tag local `archive-2026-09` trỏ tới
  `d45cf4ff26d8c6204a181f0fa77887e087a4d381` trong clone sạch.
- Push hai nhánh WIP, tag archive và README archive chưa thực hiện được vì máy hiện
  tại không có xác thực GitHub (HTTPS hỏi username; SSH từ chối public key).
- VM `dt4n-research-01`: chưa kiểm được vì `gcloud` không có tài khoản active.
- Remote hiện tại của repo mới:
  `https://github.com/vantai13/dt4n-decision-risk-project.git`.
- Lockfile tạo lại bằng `pip freeze --exclude-editable`.
- Kiểm tại repo làm việc: `20 passed in 0.95s` trên Python 3.14.5.
- Kiểm từ clone sạch cục bộ tại commit `4caf4383707fe9c452997f39490e3e3c2331a0f9`:
  cài 19 dependency từ lockfile, cài editable với `--no-deps`, rồi pytest
  `20 passed in 0.36s`; working tree clone sạch.
- Fast-forward trực tiếp tại `/home/vantai/dt4n` gặp thư mục read-only và dừng trước
  khi đổi `HEAD`; trạng thái checkout dở đã được cất trong stash recovery. Repo nguồn
  được trả về nhánh sạch `wip-before-archive`; việc chuẩn bị tag/README archive được
  thực hiện trong clone sạch `/home/vantai/dt4n-archive-work`.

## Cập nhật backup ngoài máy 2026-09-23

- Bundle: `/home/vantai/backup/dt4n-wip-2026-09-23.bundle` (9,061,555 byte).
- SHA-256: `1a08c2f9f2b4a9c125854c96af718d657ab1246b5fa1eeba82d9389530145028`.
- `git bundle verify`: OK; chứa `wip-before-archive` tại `d387f4df6` và
  `wip-stash-before-archive` tại `c2445f397`.
- Bản off-machine đã tải lên Google Drive:
  https://drive.google.com/file/d/1FFhmFlThiCcbHLNuMf292bxBdq1z7SLE/view?usp=drivesdk
- GitHub đã có tag annotated `archive-2026-09` → `d45cf4ff26d8c6204a181f0fa77887e087a4d381`,
  README archive trên `main` tại `f7aa249`, và nhánh `wip-stash-before-archive`.
- Nhánh `wip-before-archive` chưa push được: GitHub từ chối vì Personal Access Token
  hiện tại thiếu scope `workflow` để cập nhật `.github/workflows/tests.yml`. Nhánh này
  vẫn được giữ cả trong bundle local và bản bundle trên Google Drive.
