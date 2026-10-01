# Báo cáo chạy GO-check rollout

> Báo cáo này giữ trạng thái khi tái lập go0. Kết quả tái lập sandbox trên
> 92/93 và 94/95 xem REPRODUCTION_REPORT.md; các seed đó hiện đã mở.

Ngày chạy: 2026-10-01. Repo/nhánh: `ndt-decision-risk` / `rollout-v6`.

## Phạm vi đã chạy

- Tái lập bằng 20 seed calibration `80001–80020` và 20 seed test
  `81001–81020` (`--seeds go0`).
- Mỗi luật SC/K2 tự đi quỹ đạo của mình (closed-loop rollout).
- Tune ngưỡng riêng trên calibration dưới harm budget; CI 95% ghép cặp theo
  seed test.
- Đánh giá `α ∈ {0,2%; 1%}` và cooldown `{0; 30 giây}`.
- Seed fresh chưa chạy vì chưa có dự đoán tác giả. Dải riêng 92001/93001
  được dành cho lần lặp này; TC3 giữ quy tắc đã khóa tại L1.5.

## Kết quả đo được

Thang đo test: luôn ở A = **14,633 ms**; oracle nhìn trước = **2,255 ms**.

| Cooldown | α | Delay SC | Delay K2 | SC − K2, CI95% | Harm SC/K2 | Switch SC/K2 trên 1000 epoch |
|---:|---:|---:|---:|---:|---:|---:|
| 0 s | 0,2% | 5,214 ms | 3,561 ms | **+1,652 [1,225; 2,080] ms** | 0,78α / 0,82α | 6,7 / 12,4 |
| 0 s | 1% | 3,176 ms | 3,170 ms | +0,006 [−0,044; 0,056] ms | 0,93α / 0,95α | 26,2 / 31,4 |
| 30 s | 0,2% hoặc 1% | 4,792 ms | 4,240 ms | **+0,552 [0,124; 0,981] ms** | 0,174% / 0,034% (tỉ lệ tuyệt đối, làm tròn) | 8,7 / 6,5 |

Giá trị dương của `SC − K2` nghĩa là K2 có delay thấp hơn. Trên seed tái lập,
K2 hơn SC rõ ở budget chặt 0,2%; ở budget 1% và không cooldown, CI chứa 0 nên
chưa có khác biệt. Với cooldown 30 giây, cùng một policy được chọn cho hai mức
α trong grid hiện tại. **α không hoạt động dưới cooldown 30 s** trên hai budget
đã quét; đây là cùng một kết quả. Harm thấp hơn budget trên test chưa tự nó
chứng minh multiplier KKT bằng 0 cho chính sách rollout có động học.
Dòng cooldown đạt TC1 gợi ý trên seed cũ, nhưng chưa giải thích cơ chế
xếp hạng theo rủi ro khi harm budget chặt.

## Artefact

- Output nguyên văn: `results/gocheck/go0_output.txt`.
- Code chạy: `experiments/gocheck/rollout.py`.
- Đặc tả chưa khóa: `notes/gocheck/GO_check_spec.md`.
- Cache mô phỏng (đã gitignore): `results/gocheck/raw/`.
- Môi trường tăng tốc đã ghi lock: `numba==0.67.0`, `llvmlite==0.49.0`.

## Kiểm chứng

- `python -m pytest -q`: **138 passed**.
- Kết quả `go0` khớp từng số được nêu trong hướng dẫn đầu vào.
- Tổng thời gian lệnh rollout: **70 giây**; phần mô phỏng hoàn tất sau 28 giây,
  phần còn lại là tính decision/tune/rollout.

## Trạng thái kết luận

Đây là **tái lập trên seed GO v0 đã được xem**, không phải xác nhận mới. Chưa
được dùng kết quả này để điền dự đoán hoặc thay tiêu chí. Chỉ chạy seed fresh
sau khi tác giả điền prediction, rồi commit khóa spec riêng GO-check.
