# Provenance — dữ liệu AoI đo trên dt4n

- **Nguồn:** `https://github.com/vantai13/dt4n.git`, tag `archive-2026-09`, commit
  `d45cf4ff26d8c6204a181f0fa77887e087a4d381`.
- **Đường dẫn gốc:** `results/LIVE/phase-23/aoi_v7_estimates.json`; lấy byte-exact bằng `git show`, không chép tay.
- **Báo cáo/code gốc:** `docs/phase-23/20-aoi-on-topology-v7.md`, `measurements/aoi_probe_v7.py`,
  `measurements/aoi_estimate_v7.py`, `bridge/collector.py::collect_all`, `bridge/ditto_reader.py`.
- **Thiết kế:** topology v7 có 6 host, 6 switch, 8 link; 2 mode × 5 mức tải × 3 lần lặp × 120 s; probe mỗi
  0,1 s, không đồng bộ và đảo thứ tự đọc; 143.880 quan sát/mode; không có AoI âm.
- **`aoi.*`:** AoI giây bằng `t_obs−t_source` cho từng Thing link. `t_source` được lấy ngay trước khi collector
  đọc counter giao diện, tức cuối cửa sổ đo; `t_obs` là lúc HTTP GET từ Ditto trả về. Vì vậy asset đo
  `t−t_m`, chưa phải `z`; theo definitions, `z=AoI+W/2`.
- **Cửa sổ đo:** rate là `Δcounter/Δt` giữa hai lần đọc liên tiếp, với `Δt≈0,5 s`.
- **`effective_period.median_s`:** median của các hiệu liên tiếp giữa các giá trị `t_source` duy nhất theo từng
  logical link, rồi gộp qua run; đã tự kiểm trong `aoi_estimate_v7.py::effective_periods_across_runs`.
- **`aoi_rho.pearson`:** tương quan AoI với tải link lấy từ `txRate`; đây là tải đi qua, không phải tải đề nghị.
- **Mode:** CLEAN đẩy đủ 20/20 Thing mỗi chu kỳ; PROD chỉ đẩy Thing thay đổi, nhưng link gần như luôn đổi.
- **`cells`/`runs`:** thống kê theo `(mode, rho_bar)` gộp ba lần lặp / theo từng run, tổng 30 run.
- **`prediction_checks`, `closes_P23A`:** dự đoán đăng ký của dt4n; P23-A không đóng vì gate răng cưa cũ trượt.
- **Không có trong git:** khoảng 427 MiB dữ liệu JSONL thô. Ngày 2026-09-26 cũng không tìm thấy thư mục raw hoặc
  `rho_offered_long.csv` trong `/home/vantai`; vì vậy không ước lượng hồi tố tỉ lệ đuôi từ raw.

Checksum bắt buộc nằm trong `SHA256SUMS`.
