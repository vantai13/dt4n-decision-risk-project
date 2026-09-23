# Experiment design — v1 (2026-09-23)

Bộ thiết kế do agent đề xuất theo yêu cầu người dùng. ADR ở `02_decision_log.md`,
estimand ở `06_definitions.md`. Chưa chạy e01–e12; chưa có GVHD phê duyệt.
Plan riêng tư không được đưa lên git. e06–e12 chỉ chốt vai trò cấp cao từ lesson,
không giả định đã đọc MASTER_PLAN riêng tư hoặc đã có config chi tiết.

## 1. Thế giới tham chiếu

W_ref = G1 · T0 · D_lin · A0 · M0, với hai path ứng viên cố định P1,P2.
Theo D12, cộng propagation offset hằng số b vào P1 để giữ độ khó
κ=μ_D/σ_D=κ_ref=0,5. Offset chỉ dịch mean của D=C_P2−C_P1, không đổi variance.

| Tham số | Giá trị | Lý do |
|---|---|---|
| G1 | butterfly 6 node, 8 link, danh mục 4 path từ topology_v7 | giữ hình học nguồn |
| K | 2: P1=uA-ac-vC, P2=uA-ad-vD | null hai-path, không confound chọn top-2 từ K>2 |
| rho_bar | 0,70 mọi link | còn cách biên 0,99 đủ xa, có độ cong để so D0 |
| sigma | 0,05 | biên trên cách 5,8 SD tại W_ref |
| kappa_ref | 0,5 | tránh W_ref dễ đến mức always-trust đã đạt harmful budget 1% |
| b trên P1 | 4,281255 ms | μ_D=5,5; σ_D=2,437490; b=μ_D−0,5σ_D |
| tau | 1 s | chuẩn hóa thời gian bằng z/tau |
| dt | 0,01 tau | grid lịch sử đủ mịn cho lag nhỏ nhất 0,01 tau |
| T_dec | epoch 0,1 tau, một uniform timestamp/epoch | phủ pha telemetry |
| W | 200 tau | baseline lịch sử dài; sai số fit do e02 đo |
| horizon đánh giá | 100.000 quyết định/run/OD | cố định trước xem test, tương đương 10.000 tau |
| warm-up | W + z_max | cùng thời điểm bắt đầu giữa các mức age |
| seeds | 0–9 | 10 run độc lập, CRN giữa phương pháp |
| ages z/tau | {0;0,01;0,05;0,1;0,3;0,5;1} | có fresh sanity và vùng approximation lệch |
| alpha | 0,01 chính; 0,05 phụ | risk–coverage ở hai mức, không chọn sau test |

Giữ base delay, bandwidth của link từ reference; dùng packet=1500 byte làm
quy ước synthetic (không claim ứng dụng thực). h_l=12/bw_Mbps ms là service time.
D0_l(rho)=base_l+h_l/(1−rho).
D_lin_l(rho)=base_l+h_l/(1−rho_bar)+h_l(rho−rho_bar)/(1−rho_bar)^2.
Đổi rho_bar thì tiếp tuyến đổi có chủ ý, chỉ so D_lin/D0 paired trong cùng cell.
Không gọi chênh giữa hai rho_bar khác nhau là effect chỉ của curvature.

Với mỗi cell e03, tính μ_D và σ_D từ D_lin chưa clip, rồi cộng offset b dưới đây
vào cả truth và twin của P1. Số làm tròn 6 chữ số; implementation phải tính từ
công thức, không đọc lại số làm tròn.

| rho_bar | sigma | μ_D (ms) | σ_D (ms) | b trên P1 (ms) |
|---:|---:|---:|---:|---:|
| 0,50 | 0,02 | 3,500000 | 0,350999 | 3,324501 |
| 0,50 | 0,05 | 3,500000 | 0,877496 | 3,061252 |
| 0,70 | 0,02 | 5,500000 | 0,974996 | 5,012502 |
| 0,70 | 0,05 | 5,500000 | 2,437490 | 4,281255 |
| 0,85 | 0,02 | 10,500000 | 3,899984 | 8,550008 |
| 0,85 | 0,05 | 10,500000 | 9,749960 | 5,625020 |
| 0,90 | 0,02 | 15,500000 | 8,774964 | 11,112518 |
| 0,90 | 0,05 | 15,500000 | 21,937411 | 4,531295 |

D_lin không clip đạt κ=0,5 theo xây dựng. Khi chạy đối chứng có clip, D0 hoặc D1,
luôn đo và báo κ realized; không tuyên bố offset giữ κ chính xác sau biến đổi phi tuyến.
e06 không áp offset lên topology thật: báo phân phối κ theo OD/cặp, phân tầng kết quả
theo κ và không quy mọi khác biệt giữa topology cho sự phá vỡ của luật.

e01 dùng G0 hai link/path có cùng base=0 và h=1 ms để mean margin=0 cho Sheppard;
có bài kiểm công thức signed nonzero mean riêng trước khi áp cho G1 bất đối xứng.
T0 affine null là OU Gaussian không clip. Giá trị rho/cost ngoài miền vật lý được
ghi đếm, không clip để rồi vẫn gọi null chính xác.
D0 vật lý dùng clip [0;0,99]; chạy đối chứng D_lin với cùng clipping trên cùng
realization để tách effect clipping khỏi curvature. D1 chạy trong miền calibration
đã đọc từ bảng, cùng policy biên cho đối chứng; không ngoại suy âm thầm.

## 2. Thành phần và scope

| Thành phần | Kiểm soát | Mở rộng |
|---|---|---|
| G | G0 hai path, G1 butterfly | G2 nhiều topology/OD/K ở e06 |
| T | T0 OU độc lập | T1 OD, T2 heavy-tail, T3 trace |
| D | D_lin affine, D0 M/M/1 | D1 lookup Mininet |
| A | A0 tuổi cố định | A1 periodic arrivals + pipeline, A2 tuổi đo |
| M | M0 twin/truth cùng cost map | M1 twin D0 fit bằng calibration, truth D1 |

T2 ở tài liệu này nghĩa là heavy-tail, không regime switching. Mỗi cấu hình phải
ghi tên generator đầy đủ vì các lesson dùng T2 không nhất quán. e04 dùng AR(1)
innovation Student-t df={3,5}, rescale innovation để stationary variance=sigma²,
phi=exp(−dt/tau). Stationary marginal không được gọi là Student-t chính xác.
Burn-in riêng 50 tau cho generator này, rồi W+z_max lịch sử; T0 vẫn init dừng.
Kiểm variance/ACF thực đạt và tỷ lệ clipping; không chọn lại seed khi chúng lệch.

## 3. Sổ đăng ký thí nghiệm

| ID | Câu hỏi/RQ | IV | DV chính | Giữ cố định | Vai trò |
|---|---|---|---|---|---|
| e01 | Null có khớp oracle? | age grid, zero/nonzero mean | pair flip, predicted flip, Sheppard khi mean=0 | G0,K2,T0,D_lin,M0, no clip | validity |
| e02 | W hữu hạn làm risk lệch bao nhiêu? RQ1a | W/tau={10,50,200} | selective_risk_ratio, coverage, fit variability | W_ref trừ W, z/tau=0,3 | characterization; hướng pilot đã thấy |
| e03 | Ranh giới phi tuyến? RQ1a | rho_bar={0,5;0,7;0,85;0,9}, sigma={0,02;0,05}, age grid; D_lin/D0/D1 | selective_risk_ratio chính; harmful mô tả kèm ε/σ_D; regret | G1,K2,T0,A0; oracle/proxy và operational báo riêng | confirmatory sau chốt miền D1 |
| e04 | Heavy-tail tác động thế nào? RQ1a | Gaussian vs innovation t(df=3,5) | selective_risk_ratio, reliability, harmful | D_lin, phương sai/ACF mục tiêu, W_ref còn lại | confirmatory sau generator validity |
| e05 | Model mismatch tương tác age? RQ1a | M0/M1 × age grid | harmful, regret, interaction contrast | truth D1 ở cả M0/M1; twin map thay, cùng traffic | factorial nhỏ |
| e06 | Transfer topology/OD/K? RQ1b | paper 1: Abilene/GÉANT, K={2,3}, age A1; K=5,T3 là mở rộng | pair vs global error, contender, calibration; phân phối κ | cùng ngân sách và ε; không ép κ trên topology thật | scope thu gọn theo D15; chốt config cuối P3 |
| e07–e09 | Gate hơn baseline mạnh? RQ2 | phương pháp/C1/C2/fallback | selective harmful, coverage, e2e cost | paired traffic và dữ liệu calibration | chốt chi tiết L5.1 |
| e10–e11 | Trace/realism transfer | T3 và evidence thực có | các estimand đã khóa | chronological split, horizon có thật | chốt sau kiểm nguồn/license |
| e12 | Emulation kiểm xu hướng | subset cell đã đăng ký | harmful/regret/coverage | time-box 2 tuần | P6, sau simulator |

Shared-link cancellation chuyển thành unit test Phase 2: cố định cặp path,
thêm cùng một link cost vào cả hai không đổi D. Không dùng unit test để claim
overlap không ảnh hưởng global ranking của K>2. Tương quan có thể đổi variance
của phần không chung; link chung vẫn triệt tiêu đại số, không “trở lại” trong D.

## 4. Baseline và fairness

- Always-trust: không reject, coverage=1.
- AoI threshold và margin-only: tune threshold trên calibration; margin-only gate
  không đồng nhất hysteresis stateful (hysteresis cần baseline riêng ở L5.1).
- Operational Gaussian: giữ action hold, p_flip từ hồi quy trễ; alpha gate.
- Forecast-to-now + Gaussian gate: dự báo path costs tới hiện tại và chọn action
  forecast; với K2 dùng xác suất lỗi của chính action này. K>2 phải ước lượng
  joint uncertainty hoặc cận hợp lệ, không dùng công thức một cặp cho global risk.
- Naive normalized margin: ablation không mean reversion.
- Conformal C1/C2: quantile score pair/all phù hợp K, không gọi marginal coverage
  là bảo đảm selective risk. Mọi claim temporal cần assumptions riêng.

Cùng OD, timestamp range, sample identifiers, W giây lịch sử telemetry và thời
điểm truth-label trở nên khả dụng cho các phương pháp. Trễ label phải được ghi;
label chưa có không được dùng calibration online. Lịch sử điều khiển và nhãn test
tách biệt; test không dùng chọn threshold hoặc fit bất kỳ baseline nào.
Ngân sách tune cùng 20 candidate thresholds, cùng calibration objective; trường
hợp analytic không cần tune báo đúng như vậy. Optional Guérin–Orda chỉ bổ sung
sau đọc full text, không đồng nhất QoS feasibility với xác suất path tốt nhất.

## 5. Giao thức thống kê và điều kiện thông qua

D10 theo definitions §2. So phương pháp bằng hiệu paired mỗi run hoặc paired
run bootstrap cho selective. Với nhiều OD, cùng trọng số đều OD, không gộp theo
traffic volume. Luôn báo counts/zero ACCEPT/fit invalid và per-OD distributions.
Không dừng khi đủ lỗi, không lọc run không đẹp. Horizon có thể đổi sau pilot timing
và precision nhưng trước test; decision log ghi cả cấu hình cũ và mới.

e01: kiểm identity đại số và oracle conditional probabilities; đối chiếu Monte
Carlo aggregate bằng CI qua run. Không đòi mọi pointwise CI95% đều phủ đồng thời:
kiểm Holm family alpha=0,05 trên residual oracle của grid định trước. Rejection
là tín hiệu chẩn đoán, không chứng minh chắc chắn bug; kiểm randomness, test power,
clipping, conditioning và assumptions trước. Operational calibration không phải
định lý; không dùng nó làm tiêu chí “simulator có bug”.

Tối đa 6 claim confirmatory trong cả paper; family cụ thể, direction, test và cell
contrast phải đăng ký trong experiment log trước mỗi batch. Hiện mới chốt thiết kế,
chưa đăng ký đủ sáu claim; không gắn nhãn mọi phép so exploratory là confirmatory.
Mốc SESOI calibration ±20% ratio do ADR, thiếu events thì inconclusive. Với gate,
SESOI đề xuất coverage +5 điểm phần trăm ở selective harmful≤1%; hiệu lực chỉ xét
sau L5.1 chốt fallback/calibration, không tối ưu ngưỡng bằng test.

## 6. Ngân sách tính toán

Mỗi run đánh giá 10.000 tau: khoảng 1.020.101 history steps gồm warm-up, 8 link.
e03 4 mean × 2 sigma ×10 seed =80 chuỗi (~6,53e8 link-values); age và method
dùng lại traffic. Float64 một chuỗi khoảng 65 MB, xử lý tuần tự/chunk, không giữ
toàn bộ sweep. Sinh traffic chỉ là một phần runtime: rolling fit, D1 interpolation,
gate và bootstrap cũng phải benchmark. Chưa có runtime eNN đã đo.

Mục tiêu khoảng 10 phút/thí nghiệm là ngân sách, không lời hứa. Đo pilot một cell
trước full sweep; nếu quá ngân sách, sửa grid và ghi ADR trước confirmatory, giữ
10 seed. Không tự cắt horizon nếu việc đó làm mất precision cần thiết.

## 7. Ngoài scope và điều kiện còn mở

Không closed-loop TE, RL/LLM, không theorem conformal mới. GVHD còn cần xác nhận
ε chưa có SLA. D15 cho phép giả định exogenous ở paper 1 chỉ khi controlled flow
chiếm f≤0,1σ capacity (với σ=0,05: f≤0,5%); kiểm và log f/σ trong từng config.
Closed-loop feedback và route flapping thuộc RQ3 và phải nêu ở Limitations.
Thiết kế e06–e12, labels và fallback phải hoàn thiện đúng phase trước chạy.
Đây là các checkpoint có chủ ý, không phải ô lựa chọn bỏ trống.

Do σ_D thay đổi mạnh qua cell e03, không dùng harmful@2ms để claim so sánh ngang
cell. Claim e03 dùng `selective_risk_ratio`; harmful chỉ mô tả và luôn báo ε/σ_D.

## 8. Pilot đã biết trước

- Monte Carlo exact/naive đã chạy trong phiên trước, seed0,n=2.000.000,z/tau=0,3:
  observed=0,0232197; exact=0,0232233; naive=0,0061156. Không gọi dự đoán mù.
- Bảng W=10/50/200 tau và bảng D0 ratio≈2–26 là số do tài liệu hướng dẫn cung cấp,
  agent đã đọc nhưng chưa tái chạy các script wsim.py/nl.py trong lượt này.
  Khai exposure trước khi đăng ký hypothesis. D0 pilot có clipping, fit/test dùng
  cùng mẫu, nên không dùng làm bằng chứng confirmatory tách riêng curvature.
- Độ lồi/Jensen cho kết quả về mean, không tự chứng minh hướng sai của conditional
  flip risk. Hướng risk phải kiểm, tránh gọi pilot thành định lý.
- Kiểm D12 do agent chạy ngày 2026-09-23: NumPy RNG seed 20260923,
  n=4.000.000, Gaussian OU exact, κ=0,5, σ_D=2,437490, z/tau=0,3:
  pair flip=0,2054485; harmful@2ms=0,03101175; mean regret=0,222038 ms.
  Đây là sanity check để loại thiết kế suy biến, không phải kết quả confirmatory.
