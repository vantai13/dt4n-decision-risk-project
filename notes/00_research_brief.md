# Research brief (≤ 1 trang) — v0

## Problem

Telemetry của Network Digital Twin luôn có tuổi, nên chi phí path mà controller nhìn thấy có thể khác ground truth tại thời điểm ra quyết định. Sai số state không tự động dẫn đến sai routing: nó chỉ nguy hiểm khi đủ lớn so với khoảng cách chi phí giữa hai path tốt nhất. Nghiên cứu này đo rủi ro ở cấp quyết định và thử phát hiện quyết định không đáng tin trước khi thực thi.

## Thesis

Không phải mọi sai số của twin đều nguy hiểm; điều quan trọng là sai số đó có đủ để đảo quyết định hay không.

## RQ1 — Characterization

Decision risk dưới stale telemetry có được giải thích chủ yếu bằng normalized margin — decision margin chia cho mức trôi kỳ vọng trong khoảng age — hay không, và quy luật này vỡ ở đâu?

H1: normalized margin sẽ sắp thứ tự decision error/regret nhất quán hơn age hoặc margin riêng lẻ qua nhiều regime tải. Bác bỏ H1 nếu nó không cải thiện khả năng phân biệt so với baseline đơn biến, hoặc thứ tự rủi ro đảo chiều giữa các traffic/topology regime.

## RQ2 — Trust gate

Gate có điều kiện theo age và margin có đạt coverage cao hơn tại cùng mức risk so với always-trust, AoI threshold, margin-only, normalized-margin giải tích và forecast-to-now không?

H2: age-conditioned gate sẽ Pareto-improve risk–coverage trên nhiều seed và vẫn giữ thứ tự phương pháp khi chuyển từ delay model mượt sang bảng Mininet đo thật.

## Assumptions

- Traffic là exogenous: quyết định routing không làm thay đổi quá trình tải trong paper 1.
- Simulator nắm ground truth; twin chỉ thấy trạng thái `t-z` và có thể dùng delay model khác.
- `truth_table.parquet` xấp xỉ delay tức thời theo utilization trung bình; giả định này yếu nhất gần vùng cliff/bão hòa.
- Tie-break, seed, config và cách tính regret phải cố định trước thí nghiệm.

## Out of scope (paper 1)

Guarantee dưới temporal dependence, LLM/agent, RL, federated learning và closed-loop Mininet quy mô lớn.

## Kill criteria

- Dừng nhánh normalized-margin nếu sau lưới regime/seed đăng ký trước, nó không tốt hơn cả age-only lẫn margin-only theo risk–coverage.
- Dừng claim transfer nếu thứ tự các gate không giữ được khi thay smooth delay bằng dữ liệu Mininet.
- Không mở rộng sang Mininet nếu e01/e02 không tái lập được theo seed hoặc metric quyết định chưa được khóa bằng test.

## Literature phải đọc full text trước khi claim novelty

OpenTwin v2 §VI; Zhu et al. ICML 2026 §2; Guérin & Orda 1999; một paper VoI/AoII; patent "canceling predictions".
