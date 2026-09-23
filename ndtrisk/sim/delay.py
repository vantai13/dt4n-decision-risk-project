"""THẾ GIỚI THẬT — từ tải suy ra delay/loss (hàm chi phí thật của mỗi path).

Trả lời: với ρ[t, link], delay và loss thật của từng path là bao nhiêu?

Biến thể dự kiến:
  - "smooth"  : mô hình queueing mượt (mặc định, dễ phân tích);
  - "measured": nội suy từ data/mininet_calibration/truth_table.parquet (realism, có cliff).
Output: cost_true[t, path].
"""
