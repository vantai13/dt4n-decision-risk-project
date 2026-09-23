# reference/ — code cũ để ĐỌC, không để CHẠY

Snapshot từ repo dt4n tại commit `70d0e635b8189d20cdd5bae947257e0ff6c383a4`.

**Quy tắc:** không `import` bất cứ thứ gì từ thư mục này. Không sửa file ở đây.
Khi viết lại một chức năng trong `ndtrisk/`, mở file tương ứng ở đây để đối chiếu logic,
rồi viết lại gọn hơn (bỏ các hợp đồng RNG đóng băng, MUST_CHOOSE, provenance nặng...).

| File cũ | Đọc để lấy gì | Sẽ được viết lại ở |
|---|---|---|
| twin/topology_v7.py | Butterfly 6 node, 8 link, 4 path; hàm decide() | ndtrisk/sim/topology.py (thành 1 trong nhiều topology) |
| twin/link_model.py | Mô hình bậc thang v1 (cliff 0.9275) — chỉ để hiểu topology_v7 | không port |
| twin/link_model_v2.py | Twin đo được: PCHIP + sigma + domain | ndtrisk/sim/delay.py (biến thể "measured") |
| twin/cost_v2.py | Ghép delay = base + serialization + queue | ndtrisk/sim/delay.py |
| measurements/sla_calib_v2.py | ar1_matrix(): tải AR(1) độc lập từng link | ndtrisk/sim/traffic.py (vector hoá) |
| measurements/decision_error_v2.py | run_cell(): vòng lặp age z → a_twin vs a_truth | ndtrisk/twin/stale_view.py + experiments/ |
| measurements/build_truth_table.py | Cách dựng truth_table.parquet | chỉ để hiểu provenance |
| cert/margin_score.py | margin top-2, score, accept rule | ĐÃ PORT: ndtrisk/decision/margin.py |
| cert/conformal_age.py | q̂ theo bin age, split theo block | ndtrisk/decision/gates.py |
| cert/fallback.py | Ngữ nghĩa ABSTAIN: static / sticky / wait | ndtrisk/decision/gates.py + eval/metrics.py |

Muốn xem file khác của dự án cũ: mở repo cũ đã archive, đừng copy thêm vào đây.
