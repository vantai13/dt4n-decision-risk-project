# experiments/pilot/ — artefact trước plan (thuyết minh v12–v14)

Code nháp sinh ra các con số trong mục "Kết quả sơ bộ" của thuyết minh. Được đưa vào repo ngày
2026-09-25 (Phase 0 v2, L0.1) để các con số đó truy được nguồn.

| Script | Sinh ra | Trích ở | Chạy lại ngày 2026-09-25 |
|---|---|---|---|
| `switch_or_stay_diagnostic.py` | `results/switch_or_stay_diagnostic.txt` | thuyết minh v14 §6.1 | trùng byte |
| `p01_load_information.py` | `results/p01_load_information_output.txt` | không trích trong thuyết minh | pilot khám phá của tác giả, có log riêng |
| `p02_objective_rules.py` | `results/p02_objective_rules_output.txt` | ADR K2, K21; memo L0.3 (không trích trong thuyết minh) | tạo 2026-09-25 |
| `p03_h2_indices.py` | `results/p03_h2_indices_output.txt` | 06_definitions v2 Phần 6; ADR K17 bổ sung | tạo 2026-09-25 |
| `p04_evaluation_protocol.py` | `results/p04_evaluation_protocol_output.txt` | 05_evaluation_protocol v1 mục 2–3; ADR K16 | tạo 2026-09-25 |
| `p05_token_bucket_testbed.py` | `results/p05_token_bucket_testbed_output.txt` | K20 (đề xuất sửa); thuyết minh v15 §6.1 | tạo 2026-09-25 |

Quy tắc: không dùng các file ở đây làm bằng chứng cho RQ1/RQ2. Logic đáng giữ sẽ được viết lại
sạch, có test, trong `ndtrisk/` ở các phase sau (L2.1, Phase 3).

> Ghi chú 2026-09-25: P02–P04 dùng mục tiêu (b) (missed tại ngân sách harm). K2 đã chuyển sang gain (ms). Các pilot giữ làm
> bằng chứng cơ chế; độ lớn của chúng không chuyển sang mục tiêu mới.
