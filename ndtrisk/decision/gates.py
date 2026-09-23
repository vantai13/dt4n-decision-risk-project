"""TRUST GATE — ACCEPT hay ABSTAIN cho từng quyết định.

Trả lời: quyết định vừa chọn có đủ đáng tin để thực thi không?

Mỗi gate là một hàm: (margin_twin, age, [thông tin khác]) -> accept[t] (bool).
Dự kiến (baseline trước, đề xuất sau):
  always_trust · aoi_threshold · margin_only (hysteresis) · normalized_margin (giải tích)
  · forecast_to_now · age_conditioned_conformal (đề xuất)
ABSTAIN phải có ngữ nghĩa vận hành: static / sticky / wait (xem snapshot `cert/fallback.py`).
"""
