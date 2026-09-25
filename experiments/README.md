# experiments/

Quy ước:
- Tên file: `eNN_ten_ngan.py` (ví dụ `e01_two_path_sanity.py`). Một file = một câu hỏi.
- Mỗi thí nghiệm đọc một config trong `configs/` (có seed), ghi ra `results/eNN/`:
  `summary.json` (kèm git hash + config) và figure.
- TRƯỚC khi chạy: ghi dự đoán vào `notes/03_experiment_log.md`. SAU khi chạy: ghi kết quả + diễn giải.
- Code dùng lại nhiều lần → chuyển vào `ndtrisk/`. File ở đây chỉ nên là kịch bản mỏng.
- `fNN_*.py`: spike khả thi của Phase 1 (code nháp, bỏ đi được). `eNN_*.py`: thí nghiệm chính.
- `pilot/`: artefact trước plan (thuyết minh v12–v14), xem `pilot/README.md`.
