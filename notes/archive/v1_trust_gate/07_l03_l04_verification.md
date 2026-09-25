# Kiểm tra lựa chọn L0.3/L0.4 — 2026-09-23

Phạm vi: kiểm tra số học VD1–VD6 bằng code hiện có, thống kê mô tả dữ liệu D1,
existing tests và consistency tài liệu. Không chạy e01–e12, không chứng minh
W=200τ hoặc ε=2 ms là tối ưu. Người dùng yêu cầu agent tự kiểm và điền choices.

## Môi trường và lệnh đã chạy

- Python 3.14.5; NumPy 2.5.3; pandas 3.0.6; dependencies theo requirements-lock.txt.
- `.venv/bin/python /tmp/verify_l03_choices.py`: script kiểm tạm, không commit code
  thí nghiệm vào Phase 0. Dùng assertions atol=1e−12 để đối chiếu expected với
  `margins`, `s_margin`, `s_vs_a1`, `accept_certified`, `accept_kappa`.
- `.venv/bin/pytest -q`: **20 passed in 0.37s**.
- `git diff --check`: không có lỗi whitespace.
- SHA256SUMS của ba asset: **3/3 PASS**; không sửa byte dữ liệu.

## Kết quả ví dụ (ms trừ cột error)

| VD | m_hat | m_true | s_pair | s_all | error | regret | Kiểm |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 0,2 | −0,2 | 0,4 | 0,4 | 1 | 0,2 | PASS |
| 2 | 40 | 35 | 5 | 5 | 0 | 0 | PASS |
| 3 | 0,02 | −0,02 | 0,04 | 0,04 | 1 | 0,02 | PASS |
| 4 | 2 | 0,4 | 1,6 | 1,6 | 0 | 0 | PASS |
| 5 | 1 | 0,5 | 0,5 | 4 | 1 | 1 | PASS |
| 6 | 0,6 | −0,4 | 1 | 1 | 1 | 0,4 | PASS |

VD5: m_hat=1≥qhat=0,8 nên gate vẫn ACCEPT. Score_all vượt quantile là failure
của coverage cho mẫu, chỉ biết khi có truth. VD6: C1 ABSTAIN, C2 ACCEPT;
regret=0,4≤ε=0,5. Không bịa lỗi tự làm ban đầu của người dùng.

## D1: thống kê tự tính

Median qua các dòng có rho trong interval trái đóng/phải mở, không weighted:

| rho | n | delay_mean_ms median | se_batch_mean_ms median |
|---|---:|---:|---:|
| [0,5;0,7) | 60 | 1,083101 | 0,052377 |
| [0,7;0,85) | 57 | 3,343350 | 0,196676 |
| [0,85;0,95) | 35 | 8,078884 | 0,292506 |
| [0,95;1,05) | 24 | 13,011568 | 0,302872 |

Tổng 176 dòng. Có thể tái tính bằng:

```python
import pandas as pd
p = pd.read_parquet('data/mininet_calibration/truth_table.parquet')
for lo, hi in [(0.5, 0.7), (0.7, 0.85), (0.85, 0.95), (0.95, 1.05)]:
    s = p[(p.rho >= lo) & (p.rho < hi)]
    print(lo, hi, len(s), s[['delay_mean_ms', 'se_batch_mean_ms']].median())
```

## Phiếu đã điền và nơi lưu lý do

Q1=a với jitter từng epoch; Q2=b; Q3=a; Q4=b; Q5=a;
Q6=a, chính 2 ms, phụ {0;0,5;1;5}; Q7=a; Q8=a;
Q9=rho_bar 0,7, sigma 0,05, K=2 cố định (G1 có danh mục 4 path).
Q10=D3 delay-only, D5 exogenous chờ GVHD, D6 hold+forecast baseline,
D7 tuổi chung, D8 OD cho generalization/evaluation, D9 z/tau và p_hat,
D10 10 seed + paired CRN; CI t vô điều kiện, run-bootstrap cho selective,
Holm trên family confirmatory khai trước.

Lý do chi tiết: `06_definitions.md` §5 và ADR trong `02_decision_log.md`.
Đây là lựa chọn thiết kế, chưa có dữ liệu để khẳng định precision, runtime hoặc
hiệu quả gate. Các pilot được cung cấp bởi lesson được phân biệt trong
`03_experiment_log.md` với Monte Carlo thực sự chạy ở lượt trước.

## Các điều chỉnh so với lời hướng dẫn

- Không dừng test khi tích đủ số lỗi: thời lượng khóa trước, ít lỗi thì inconclusive.
- Jitter theo epoch; một phase ngẫu nhiên/run chưa đủ khử khóa pha trong run.
- Không clipping ở null Gaussian exact; kiểm clipping riêng khi dùng miền vật lý.
- K>2 có selection effects và global risk khác pair risk.
- Conformal marginal coverage chưa bảo đảm conditional/selective risk≤α.
- Giá trị ε có lý do về thang đo, chưa chứng minh SLA hay độ chính xác path.
- Shared-link cancellation luôn đúng đại số với cặp cố định/additive cost,
  kể cả correlated links; đổi correlation của link riêng mới đổi luật margin.
- Độ lồi không tự chứng minh hướng sai calibration; không đòi mọi CI95% pointwise
  đồng thời phủ để rồi quy mọi sai lệch thành bug.

Sau review Lesson 0.5, W_ref v1 được phát hiện có κ≈2,256 nên quá dễ cho H2.
D12 thay bằng κ_ref=0,5 qua propagation offset; bảng số và pilot kiểm không suy biến
nằm ở `05_experiment_design.md` §1, §8 và `03_experiment_log.md`. Kiểm định
confirmatory vẫn cần đăng ký config/contrast ở đúng phase. Không có biên bản GVHD,
elevator test hay kết quả e01–e12 được suy diễn là đã hoàn tất.
