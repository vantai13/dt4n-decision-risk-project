# Kiểm tra Lesson 0.5 — 2026-09-23

## Phạm vi đã thực hiện

- Kiểm lại lỗi W_ref v1: P1/P2 tại rho_bar=0,70, sigma=0,05 có
  μ_D=5,5 ms, σ_D=2,437490 ms, κ=2,256419.
- Chọn D12 với κ_ref=0,5 và tính propagation offset cho đủ 8 cell e03.
- Chạy sanity Monte Carlo để chắc W_ref sửa đổi không còn làm H2 suy biến.
- Tra nguồn chính thức cho CNSM 2026, ICC 2027 và policy AI của IEEE; với
  CNSM/GLOBECOM 2027 chưa có CFP đã kiểm được thì giữ ô chưa biết.
- Chuẩn bị memo GVHD, venue notes, defense prep và closeout trạng thái chờ.

## Kết quả số

Lệnh tạm dùng Python/NumPy trong `.venv`, không thêm implementation Phase 2.
Với seed 20260923, n=4.000.000, OU Gaussian exact, κ=0,5,
σ_D=2,437490 ms, z/tau=0,3:

| Metric | Kết quả |
|---|---:|
| pair flip | 0,2054485 |
| harmful@2ms | 0,03101175 |
| mean regret | 0,22203761 ms |

Always-trust có harmful 3,10% > budget 1% ở cell sanity này, nên coverage 100%
không còn tự đạt H2. Pilot chỉ loại câu hỏi suy biến, không là evidence confirmatory.

## Kiểm tra repository

- `.venv/bin/pytest -q`: **20 passed in 1.07s**.
- `git diff --check`: PASS, không có whitespace error.
- Không sửa `ndtrisk/sim/`; không tạo tag `phase-0-complete`.
- Không tìm thấy `MASTER_PLAN.md` hoặc `PHASE_0.md` trong `/home/vantai` ở lượt
  kiểm này, nên không bịa SHA256 trong closeout.

## Kết luận gate

Sửa W_ref và hồ sơ kỹ thuật Lesson 0.5 đã hoàn tất. Phase 0 **chưa đóng** vì còn
việc chỉ con người mới hoàn thành hợp lệ: elevator test, bài làm tay/khả năng tự
bảo vệ, cuộc họp và quyết định thật của GVHD. D11 cũng phải kiểm lại khi CFP 2027 ra.

