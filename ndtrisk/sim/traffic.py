"""THẾ GIỚI THẬT — tải trên từng link thay đổi theo thời gian.

Trả lời: tại mỗi bước thời gian t, utilization ρ_l(t) của mỗi link là bao nhiêu?

Input : mean ρ̄_l, biên độ σ, thời gian tương quan τ, dt, số bước, seed.
Output: ma trận ρ[t, link].
Nguồn đối chiếu: snapshot `measurements/sla_calib_v2.py::ar1_matrix`.
Không làm: không tính delay, không tạo telemetry cũ.
"""
