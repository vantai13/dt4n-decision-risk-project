# experiments/pilot/ — artefact trước plan (thuyết minh v12–v14)

Code nháp sinh ra các con số trong mục "Kết quả sơ bộ" của thuyết minh. Được đưa vào repo ngày
2026-09-25 (Phase 0 v2, L0.1) để các con số đó truy được nguồn.

| Script | Sinh ra | Trích ở | Chạy lại ngày 2026-09-25 |
|---|---|---|---|
| `switch_or_stay_diagnostic.py` | `results/switch_or_stay_diagnostic.txt` | thuyết minh v14 §6.1 | trùng byte |
| `p01_load_information.py` | `results/p01_load_information_output.txt` | không trích trong thuyết minh | pilot khám phá của tác giả, có log riêng |
| `p02_objective_rules.py` | `results/p02_objective_rules_output.txt` | ADR K2, K21; memo L0.3 (không trích trong thuyết minh) | tạo 2026-09-25 |

Quy tắc: không dùng các file ở đây làm bằng chứng cho RQ1/RQ2. Logic đáng giữ sẽ được viết lại
sạch, có test, trong `ndtrisk/` ở các phase sau (L2.1, Phase 3).
