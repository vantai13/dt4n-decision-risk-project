# dt4n-decision-risk-project

**Câu hỏi (thuyết minh NCKH v14):** Một luồng đang đi trên đường A; Network Digital Twin nhìn mạng
qua telemetry đã cũ và đề xuất đường B. Khi nào một ngưỡng chênh lệch cố định (hysteresis) là đủ để
quyết định đổi hay giữ đường, và khi nào cần lan truyền bất định qua mô hình của twin?

**Trạng thái:** Phase 0 v2 — khoá khung nghiên cứu sau pivot. Hướng v1 (trust gate, top-2 margin)
kết thúc tại tag `pre-pivot-v14`; tài liệu v1 ở `notes/archive/v1_trust_gate/`, code v1 ở
`reference/v1_trust_gate/`. Lý do đổi hướng: `notes/02_decision_log.md`, mục PIVOT-v14.

## Đọc theo thứ tự

1. `notes/00_research_brief.md` — brief v2 (2026-09-25; bản nháp AI, tác giả kiểm)
2. `notes/02_decision_log.md` — vì sao chọn, vì sao đổi
3. `notes/03_experiment_log.md` — dự đoán trước khi chạy, kết quả sau khi chạy
4. `notes/01_literature/` — related work, novelty matrix

## Cài đặt

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-lock.txt && pip install -e ".[dev]" --no-deps
pytest
```

## Bản đồ repo

| Thư mục | Vai trò | Được import? |
|---|---|---|
| `notes/` | brief, decision log, experiment log, literature | — |
| `notes/archive/v1_trust_gate/` | hợp đồng nghiên cứu hướng v1, chỉ để tra cứu | — |
| `ndtrisk/` | package chính; module được thêm theo phase (L2.1: `theory/`, Phase 3: DES) | có |
| `experiments/` | mỗi file một câu hỏi; `pilot/` là artefact trước plan | không |
| `data/mininet_calibration/` | số đo testbed dt4n, read-only; ý nghĩa cột ở `PROVENANCE.md` | đọc |
| `results/` | summary + hình; dữ liệu thô bị gitignore | — |
| `emulation/` | Mininet validation, làm sau cùng | — |
| `reference/` | code cũ để đọc: `dt4n_snapshot/`, `v1_trust_gate/` | không |

## Ba tầng bằng chứng

A. Mô phỏng sự kiện rời rạc (DES) — bằng chứng chính, biết ground truth, vặn từng tham số.
B. Realism inputs — tham số và phân bố đo được (tuổi telemetry, log tải) cắm vào DES.
C. Mininet — kiểm thứ tự phương pháp và dấu hiệu ứng trên hàng đợi Linux thật. Testbed dùng HTB
   token bucket, khác cơ chế với mô hình M/D/1/K của DES. Làm sau cùng, có time-box.

## Môi trường đã kiểm

| Python | Cách cài | Kết quả | Ngày |
|---|---|---|---|
| 3.14.5 (máy chính) | `pip install -r requirements-lock.txt && pip install -e ".[dev]" --no-deps` | pytest xanh (20 test, hướng v1) | 2026-09-23 |
| 3.14.5 (máy chính) | như trên | pytest xanh (4 test, sau pivot) | 2026-09-25 |

Chỉ ghi những phiên bản đã chạy xanh.
