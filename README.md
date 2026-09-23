# dt4n-decision-risk-project

**Câu hỏi:** Khi nào trạng thái cũ (stale telemetry) của một Network Digital Twin làm
quyết định routing sai — và có phát hiện được những trường hợp đó trước khi hành động không?

Đọc theo thứ tự: `notes/00_research_brief.md` → `notes/03_experiment_log.md` → `experiments/`.

## Cài đặt
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Bản đồ repo
| Thư mục | Vai trò | Được import? |
|---|---|---|
| `notes/` | Tư duy: brief, literature, log quyết định, log thí nghiệm | — |
| `ndtrisk/sim/` | Thế giới thật (ground truth): topology, traffic, delay | có |
| `ndtrisk/twin/` | Cái nhìn của twin: telemetry có tuổi + mô hình | có |
| `ndtrisk/decision/` | Controller + trust gate | có |
| `ndtrisk/eval/` | Metric trên quyết định | có |
| `experiments/` | Mỗi file = một câu hỏi / một figure | không (chạy trực tiếp) |
| `data/mininet_calibration/` | Dữ liệu đo từ dự án cũ, read-only | đọc |
| `results/` | Output summary + figure (raw bị gitignore) | — |
| `emulation/` | Mininet validation — giai đoạn cuối | — |
| `reference/` | Code cũ để đọc, KHÔNG import | không |

## Ba tầng bằng chứng
A. Simulation (ndtrisk/) — evidence chính, nhanh, biết ground truth.
B. Realism — cắm dữ liệu đo (data/) vào simulation.
C. Emulation (emulation/) — kiểm tra xu hướng trên Mininet, ít cấu hình, làm sau cùng.

## Môi trường đã kiểm

| Python | Cách cài | Kết quả | Ngày |
|---|---|---|---|
| 3.14.5 (máy chính) | `pip install -r requirements-lock.txt && pip install -e ".[dev]" --no-deps` | pytest xanh | 2026-09-23 |

Chỉ ghi những phiên bản đã chạy xanh. `requires-python` trong `pyproject.toml` là
yêu cầu tối thiểu của code, không phải cam kết rằng lockfile cài được trên mọi
phiên bản đó.
