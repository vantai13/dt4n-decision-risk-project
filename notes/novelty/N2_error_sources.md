# N2 — Nguồn sai của sandbox và cách phân rã (v0, 2026-10-02, nháp)

> Nguồn nháp: lesson do người dùng cung cấp (ghi Claude). Codex triển khai, đo và đối chiếu local ngày 2026-10-02.
> Chưa xác nhận tác giả đã đọc từng dòng/tính giấy/tự kiểm. Số liệu local: [báo cáo n02](../../experiments/results/n02_report.md).
> (một ô POS_probeB, 10 seed pilot, H = 0,5 s, luật Ī > 0, G_all, thế giới PSA). [QUYẾT] = tác giả quyết; chốt ở Gate N.

## 1. Bản đồ nguồn sai — mỗi nguồn vào twin qua đối số nào

Twin cũ = `posterior(rhohat, gap, W, H, rho_bar, sigma, tau, R)` + `DelayCurve(k, s_ms)` + `twin_view`.

| Họ | Nguồn | Cơ chế | Vào twin qua | Núm vặn vật lý | Công tắc cơ chế (mô phỏng) | Literature gọi là | Repo cũ |
|---|---|---|---|---|---|---|---|
| Thông tin | Độ trễ thông tin L = z + a | trạng thái trôi từ lúc đo tới lúc áp dụng | `gap` | T_tel, d, stall_p (→ z); a | cửa sổ kết thúc ở t + a (hoặc t) | staleness, AoI, actuation delay | có |
| Thông tin | Gộp cửa sổ | số đo là trung bình trên W, không phải trạng thái | `rhohat`, `W` | W (≡ T_tel trong world.py) | thay trung bình bằng giá trị tức thời | temporal aggregation | có (chưa tách) |
| Thông tin | Nhiễu đếm | số gói hữu hạn trong W | `rhohat`, `R` | W, tốc độ link | thay số đếm bằng trung bình chính xác (LỒNG trong gộp) | measurement noise | có |
| Thông tin | Twin không biết đúng tuổi | timestamp thiếu / lệch đồng hồ | `gap` sai | đồng hồ, pipeline | — | [?] | chưa có, để ngỏ |
| Mô hình | Tham số sai | ρ̄, σ, τ, K sai | `rho_bar`, `sigma`, `tau`, `k` | ước lượng từ dữ liệu ngắn, chế độ đổi | tham số đúng vs sai | parameter uncertainty | go_test (6 biến thể) |
| Mô hình | Cấu trúc sai | đường cong dừng ≠ hàng đợi thật; tải không OU | `DelayCurve`, dạng `posterior` | cơ chế hàng đợi, kiểu tải | twin đúng họ vs sai họ | model discrepancy, sim-to-real | f04b (PSA vs DES); X1′ đề xuất |
| Mô hình | Bỏ qua tác động ngược | không cộng Δρ vào đường mới | thiếu số hạng Δρ | Δρ | twin có / không số hạng Δρ | exogenous trace assumption | chưa có |

Trong minh hoạ này H định nghĩa estimand; sai lệch do dùng sai H của twin sẽ là bài toán khác. Phần ngẫu nhiên tương lai còn lại phụ thuộc mốc thông tin của lý tưởng (N1 §3). Ký hiệu z ở đây là tuổi từ CUỐI cửa sổ như world.age, không phải tuổi từ tâm trong definitions v2.1.
Ngoài phạm vi: lỗi cấu hình, hỏng thiết bị, tấn công, nhiều thay đổi đồng thời.

## 2. Ghép nối và lồng nhau

- T_tel trong world.py đổi CÙNG LÚC ba cơ chế: chu kỳ báo (→ z), cửa sổ (→ W), nhiễu (R = ρ̄S/T_tel).
- Trong mô hình đếm gói này, ước lượng rho bằng count/W không cho một số đo tức thời hữu hạn khi W→0: thiết kế ba mức inst/win/noisy. Không suy rằng mọi loại nhiễu cảm biến đều cần gộp cửa sổ.
- Với twin chỉ dùng bản tin mới nhất và biết timestamp như ở đây, treo vào qua z → thuộc phân phối của L. Twin dùng lịch sử có thể còn bị mất/méo chuỗi quan sát; ngoài phạm vi minh hoạ này.

## 3. Quy ước phân rã

- Metric: regret trung bình (ms/lần kiểm), có đồng nhất thức phân rã (N1 §3). Vẫn có thể tính hiệu/tương tác của tỉ lệ đếm về mặt đại số, nhưng không diễn giải một chiều lỗi là chi phí tránh được; phải báo cả DN/TCN.
- Thế giới cố định (CRN) giữa cấu hình n02; CI ghép cặp theo seed. Đây là coupling mới, không phải telemetry gốc từng bit; xem §8.
- Báo đủ: regret mọi cấu hình; hiệu ứng chính; tương tác (y11 − y10 − y01 + y00) theo từng mức của nguồn còn lại;
  Shapley. Với hai nguồn, chia đôi tương tác; tương tác bậc k được chia cho k nguồn trong biểu diễn coalition tương ứng. Báo cả bậc ba và đủ 6 thứ tự trong CSV; LUÔN báo kèm tương tác.
- Mức "bật" của mỗi nguồn phải có nguồn thực tế (realism_sources.md, L1.9); nếu không, ghi "giả định" và quét.
- Lặp lại theo H (N1 §5) và theo bộ sinh đề xuất (N1 §6): phân rã đổi theo cả hai.

## 4. Kết quả local (n02, n02b)

Các số local thay số chép từ lesson; một số nhánh tức thời M=0 không khớp ở độ chính xác được in. Bảng đối chiếu đầy đủ nằm trong báo cáo.

| Cấu hình S M P | Regret, twin tin B=0,80 (ms) | Regret, twin tin B=0,70 (ms) |
|---|---:|---:|
| 000 | 0.352648 | 0.352648 |
| 001 | 0.357420 | 0.359288 |
| 010 | 3.671163 | 3.671163 |
| 011 | 3.675225 | 3.867560 |
| 100 | 3.171435 | 3.171435 |
| 101 | 3.275420 | 4.316286 |
| 110 | 4.561915 | 4.561915 |
| 111 | 4.822959 | 6.034069 |

- S×M khi P=0: −1,928034 ±0,246005 ms (CI95 half); sửa riêng S cứu 0,890752; riêng M cứu 1,390480; cả hai cứu 4,209267 ms. Sửa riêng vẫn có ích, chưa thể gọi “gần như vô ích”.
- Bậc thang hai nguồn: S đứng đầu 2,818787 ms, đứng sau M còn 0,890752 ms. Shapley hai nguồn (P=0): S=1,854770, M=2,354497 ms.
- Với prior B=0,70, S×P khi M=0: +1,138212 ±0,324971 ms; khi M=1: +1.275757 ±0.425919 ms (xem CSV cho đủ chữ số).
- Shapley ba nguồn của P: 0.106613 ms (prior 0,80) → 0,716472 ms (prior 0,70). Không dùng “sai mô hình chỉ hại khi dữ liệu kém” như mệnh đề chung; ở đây chỉ thao tác prior mean B.

| Hiệu ứng gộp/nhiễu (ms) | S tắt | S bật |
|---|---:|---:|
| Gộp B, A tức thời | 2.052963 | 0.333767 |
| Gộp A, B tức thời | 0.152549 | 0.375829 |
| Nhiễu A sau khi giữ gộp A, B tức thời | 0.274841 | 0.621076 |
| Gộp cả A/B | 2.547048 | 0.727967 |
| Nhiễu cả A/B sau khi giữ gộp | 0.771467 | 0.662514 |

Dòng noisy/inst − inst/inst của lesson gộp cả hai tác động trên A. Đã thêm win/inst để tách riêng: nhiễu A là +0,274841/+0,621076 ms. Chênh nhiễu A−gộp B đổi từ −1,778123 ±0,166423 sang +0,287309 ±0,195445 ms trong ô này. Các contrast có CI ghép cặp ở CSV, không suy thứ hạng cho các ô khác.

## 5. Quyết định đề xuất

| ID | Đề xuất | Lý do | Trạng thái |
|---|---|---|---|
| N-S1 | Danh sách nguồn = bảng §1, hai họ thông tin / mô hình | mỗi nguồn gắn với đối số twin | đề xuất |
| N-S2 | Có thể dùng L=z+a để mô tả gap; phân rã đang chạy chỉ bật/tắt z và giữ a cố định | Tổng gap không quyết định duy nhất chuẩn phân rã | [QUYẾT]; gợi ý giữ thiết kế hiện tại, chờ tác giả |
| N-S3 | Chuẩn hiện tại tại t; nếu muốn loại cả a khỏi regret nền, thiết kế thêm chuẩn t+a | Chọn theo lượng thông tin được phép biết; không tự đổi mốc chỉ vì viết L=z+a | [QUYẾT]; chưa có xác nhận tác giả, chưa chạy t+a |
| N-S4 | Tách "đo" thành gộp + nhiễu (lồng nhau) | gộp chiếm ưu thế ở ô đã chạy khi B tươi | đề xuất |
| N-S5 | Mức mỗi nguồn lấy từ L1.9 trước khi phát biểu "nguồn nào chiếm ưu thế" | thứ hạng đổi theo mức | đề xuất |

## 6. Phương pháp có tiền lệ — đầu vào không-claim cho L1.8

- Factorial 2^k (Jain 1991) và Shapley value (Shapley 1953): theo lesson, chưa kiểm nguyên bản ở lượt này.
- Owen (2014) gắn Shapley với lượng phương sai được giải thích: đã kiểm abstract nhà xuất bản, không gọi phân rã regret ở đây là Sobol/Shapley effects theo phương sai. [Sobol’ Indices and Shapley Value](https://epubs.siam.org/doi/10.1137/130936233).
- Song, Nelson & Staum (2016) phân tích Shapley effects khi đầu vào phụ thuộc và cách tính Monte Carlo: đã kiểm abstract nhà xuất bản. [Shapley Effects for Global Sensitivity Analysis: Theory and Computation](https://epubs.siam.org/doi/10.1137/15M1048070).
- Howard (1966), *Information Value Theory*, DOI 10.1109/TSSC.1966.300074: giữ trong danh sách đọc theo lesson. Trang IEEE không trả nội dung bài trong lượt này; chưa xác minh mệnh đề cụ thể “tương tác như ở đây đã được chỉ ra năm 1966”. [Trang bài gốc](https://ieeexplore.ieee.org/document/4082064).
- Kennedy & O’Hagan (2001) phân biệt bất định tham số và phần sai còn lại của mô hình dù đã khớp tham số: đã kiểm abstract nhà xuất bản. [Bayesian calibration of computer models](https://rss.onlinelibrary.wiley.com/doi/10.1111/1467-9868.00294).

Định vị bằng giá trị thông tin là hướng diễn giải cần kiểm tiếp; factorial của một luật xấp xỉ cố định chưa tự động bằng giá trị thông tin Bayes tối ưu. Không claim phương pháp mới hoặc kết luận novelty từ lượt minh hoạ này.

## 7. Lịch sử sửa

- 2026-10-02 v0: nháp đầu (hỗ trợ AI). Sửa so với kế hoạch: thêm gộp cửa sổ; treo bản tin thuộc L; tác động ngược
  thuộc sai mô hình; tương tác có thể âm; Shapley không xoá tương tác; họ hàng gần nhất là giá trị thông tin.

## 8. Kiểm và giới hạn bổ sung khi thực thi

- 4 hàm model/metric giữ nguyên AST so với script cung cấp; công tắc không làm đổi hash world. P=0 khớp giữa hai prior; 4 endpoint n02b trùng từng bit n02 theo seed.
- n02 dùng u độc lập theo epoch. B có 39.237/39.322 cặp epoch cùng r_last nhưng số đếm khác. world.telemetry_view gốc chỉ rút số đếm một lần cho mỗi bản tin và tái sử dụng nó. Do đó n02 không có cùng phụ thuộc thời gian với telemetry gốc; không dùng CI chồng lấp với L1.2 làm bằng chứng tương đương.
- W=1e-6 và posterior/curve là xấp xỉ như L1.2. Giữ công thức gốc để tái lập; chưa xác định nguyên nhân mọi sai lệch số với bảng lesson.
- Trạng thái tức thời tại một đầu mút và trung bình một cửa sổ không phải hai tập thông tin lồng nhau hoàn toàn. Nhánh inst không cung cấp toàn lịch sử mà win có sử dụng. Không gọi mọi hiệu regret là lượng thông tin “bị phá” hoặc giá trị thông tin tối ưu.
- Nhận định chỉ sửa z và sửa a tương đương cần điều kiện dừng, W/nhiễu/luật/bộ sinh tương ứng; thay T_tel thường đồng thời thay W và R.
- Các mức 30 s, W=T_tel, sai prior −0,05/−0,15 vẫn là GIẢ ĐỊNH; xem [realism_sources](realism_sources.md).
- Chưa có xác nhận tác giả chọn N-S2/N-S3, H vận hành, hoặc hoàn thành tính giấy/tự kiểm. [Bài tính do Codex soạn](N2_calculation_examples.md) không thay cho việc tự làm của tác giả.

2026-10-02: cập nhật số đo local; bổ sung win/inst để tách nhiễu A; ghi sai lệch telemetry theo epoch, xấp xỉ ideal và mức kiểm nguồn literature.
