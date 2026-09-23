# Gibbs & Candès 2021 — Adaptive Conformal Inference Under Distribution Shift

| Trường | Giá trị |
|---|---|
| Tác giả | Isaac Gibbs; Emmanuel Candès |
| Nguồn | [arXiv:2106.00170](https://arxiv.org/abs/2106.00170); NeurIPS 2021 |
| Mức kiểm | 2026-09-23: PDF §2, §4.1, Proposition 4.1 |
| Vai trò | Nền + baseline global ACI |

**[F]** ACI cập nhật nominal miscoverage theo lỗi coverage vừa quan sát (§2). Proposition 4.1 chặn sai lệch giữa **tần suất miscoverage trên toàn bộ T bước** và target `α` bởi hạng cỡ `1/(γT)`, không cần ràng buộc lên phân phối sinh dữ liệu (§4.1). Kết quả đó không phải bảo đảm conditional theo age bin, theo tập ACCEPT hoặc cho một bước riêng.

**[I]** RQ2 nên so với global ACI được cập nhật đúng thời điểm nhãn đến; đo riêng coverage theo age bin, theo margin bin và selective harmful risk. Nếu nhãn của action bị từ chối không quan sát được, không giả vờ baseline có full feedback ngoài simulator.
