# reference/v1_trust_gate/ — code của hướng v1 (trust gate), chỉ để ĐỌC

Chuyển từ `ndtrisk/decision/margin.py` và `tests/test_margin.py` ngày 2026-09-25 (Phase 0 v2, L0.1)
khi đề tài pivot sang switch-or-stay (decision log: PIVOT-v14). Trạng thái đầy đủ: tag `pre-pivot-v14`.

| File | Nội dung | Còn hữu ích cho v2? |
|---|---|---|
| margin.py | top-2 margin của twin, các score, luật ACCEPT | Nguyên tắc "chọn cặp chỉ từ y_hat để không rò rỉ sự thật" = tinh thần của oracle/policy cùng thông tin ở v2 |
| test_margin.py | 16 golden test | GM1 là mẫu tốt cho test "không rò rỉ trạng thái ẩn" ở Phase 4 |

Không import, không chạy (pytest chỉ thu thập `tests/`). Các stub v1 (`ndtrisk/sim/`,
`twin/stale_view.py`, `decision/gates.py`, `decision/routing.py`, `eval/metrics.py`) đã xoá;
nội dung (chỉ có docstring) xem tại tag `pre-pivot-v14`.
