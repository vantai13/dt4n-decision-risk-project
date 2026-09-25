# Definitions — v1 (2026-09-23)

Nguồn quy ước kỹ thuật cho code, summary.json và paper. Thay đổi phải ghi ADR trước.
Do agent soạn và kiểm theo yêu cầu người dùng; không phải bài tự làm của tác giả
hay xác nhận của GVHD. Bộ lựa chọn đã điền, có điều kiện xem lại trong §5.
Các module simulator/gate/metrics chưa triển khai đầy đủ quy ước này.

## 1. Ký hiệu và luật dự đoán

| Ký hiệu | Định nghĩa | Đơn vị | Tên code |
|---|---|---|---|
| Δt | khoảng lấy mẫu lịch sử, mặc định 0,01τ | s | `dt_s` |
| T_dec | độ dài epoch lấy một quyết định, mặc định 0,1τ | s | `dt_decision_s` |
| K | số path ứng viên, K≥2 | đếm | `k_paths` |
| ρ_l | tải/capacity link | không thứ nguyên | `rho` |
| τ | thời gian tương quan OU; khác thời gian đồng bộ | s | `tau_s` |
| u, z | thời điểm sinh telemetry mới nhất đã nhận; z=t−u | s | `age_s` |
| z/τ | tuổi chuẩn hóa | không thứ nguyên | `age_over_tau` |
| C_k, Ĉ_k | delay path thật tại t và delay twin từ telemetry tại u | ms | `cost_true_ms`, `cost_twin_ms` |
| e_k | C_k−Ĉ_k, thật trừ twin | ms | `err_ms` |
| â, â₂ | top-2 theo twin, sắp ổn định; index nhỏ thắng tie | index | `a_twin`, `a_twin2` |
| a* | argmin của C, index nhỏ thắng tie | index | `a_true` |
| m̂ | Ĉ_â₂−Ĉ_â ≥0 | ms | `margin_twin_ms` |
| m | C_â₂−C_â, giữ nguyên cặp của twin | ms | `margin_true_ms` |
| s_pair | abs(m−m̂) | ms | `score_pair_ms` |
| s_all | max_k abs(e_k−e_â) | ms | `score_all_ms` |
| D_ij | C_j−C_i, D_ji=−D_ij | ms | `diff_ms` |
| κ | μ_D/σ_D có dấu theo cặp có hướng; độ khó quyết định | không thứ nguyên | `decision_difficulty` |
| b | propagation offset hằng số cộng vào P1 để điều khiển κ ở D_lin | ms | `path_offset_ms` |
| W | lịch sử theo thời gian sinh telemetry, mặc định 200τ | s | `hist_window_s` |
| μ̂, σ̂, r̂(z) | mean, SD, ACF theo cặp có thứ tự | ms, ms, không thứ nguyên | `mu_hat_ms`, `sigma_hat_ms`, `r_hat` |
| â, b̂, ŝ_res | intercept, slope, residual SD hồi quy trễ | ms, không thứ nguyên, ms | `intercept_ms`, `slope`, `residual_sd_ms` |
| c, v | tâm và SD dự báo của D_ij hiện tại | ms | `center_ms`, `predictive_sd_ms` |
| m̃, p̂ | c/v và Φ(−c/v), cặp có hướng (â,â₂) | không thứ nguyên | `margin_norm`, `p_flip_pred` |
| m̃_naive, p̂_naive | m̂/ŝ(z), Φ(−m̃_naive); ŝ²=mean increment² | không thứ nguyên | `margin_norm_naive`, `p_flip_pred_naive` |
| q̂ | quantile của score phù hợp trên calibration tách biệt | ms | `qhat_ms` |
| α | mức danh nghĩa; chính 0,01, phụ 0,05 | tỉ lệ | `alpha` |
| ε | regret threshold chính 2, sensitivity {0;0,5;1;5} | ms | `eps_ms` |

Oracle cho một cặp cố định trong quá trình Gaussian dừng:
c=μ+r(z)(m̂−μ), v=σ sqrt(1−r(z)²), p̂=Φ(−c/v).
Operational dùng hồi quy OLS D(t) theo D(t−z): c=â+b̂ m̂,
v=SD phần dư (ddof=2 cho hai hệ số). OLS là quy tắc ước lượng được chọn,
không phải đồng nhất hữu hạn mẫu với cách ước lượng μ̂,σ̂,r̂ riêng.

Dữ liệu fit chỉ gồm cặp telemetry đã nhận tại thời điểm quyết định; endpoint
không vượt u=t−z. Với A0 lịch sử đều Δt, dùng độ trễ z/Δt nguyên của grid.
A1/A2 dùng lịch sử timestamp gốc; không coi bản sao last-value hold là mẫu mới;
quy tắc ghép độ trễ bất quy tắc phải đăng ký ở e06 trước chạy.
Cửa sổ đóng tại u, đủ W khi t≥W+z. Không fit trên ground truth của test.

“Operational exact law” là tên baseline plug-in; exact chỉ áp cho oracle Gaussian
với conditioning phù hợp. Ở K>2, chọn cặp từ toàn bộ vector có thể thêm thông tin
so với conditioning trên một D; tính Gaussian của từng cặp không tự bảo đảm
calibration sau chọn cặp. K=2 cố định cho RQ1a chính; e06 kiểm cả hiệu ứng chọn cặp.

Nếu v=0 và mô hình thật sự xác định: p=1[c<0], với c=0 thì strict pair flip bằng 0;
m̃ để null. Nếu residual SD bằng 0 do thiếu/thoái hóa dữ liệu: p̂=null, ABSTAIN,
đếm invalid fit; không giả định certainty. Naive có ŝ=0 xử lý tương tự.
Không clamp p để cứu một fit lỗi.

## 2. Estimand và estimator

Đơn vị quyết định: một OD tại một thời điểm. Đơn vị lặp độc lập: run.
Mặc định trong mỗi run tính từng OD rồi trung bình đều OD đủ ≥2 path; tổng hợp
trung bình 10 run và CI t 95%. Đây là trung bình đều môi trường/OD, không traffic-weighted.

| Tên | Estimand | Đơn vị | Vai trò |
|---|---|---|---|
| `harmful_error_rate@eps` | P(R>ε), R=C_â−C_a* | tỉ lệ | chính tại ε=2 |
| `regret_mean_ms` | E[R] | ms | chính |
| `regret_p95_ms` | phân vị 95% R trong từng run/OD, rồi trung bình các phân vị | ms | phụ, không phải pooled p95 |
| `decision_error_rate` | P(â≠a*) | tỉ lệ | phụ |
| `pair_flip_rate` | P(m<0) | tỉ lệ | target của luật hai path |
| `contender_rate` | P(a* thuộc {â,â₂}) | tỉ lệ | K>2 |
| `coverage` | P(ACCEPT) | tỉ lệ | risk–coverage |
| `selective_pair_flip_rate` | P(m<0 given ACCEPT) | tỉ lệ | calibration |
| `selective_harmful_rate@eps` | P(R>ε given ACCEPT) | tỉ lệ | risk của gate |
| `selective_risk_pred` | E[p̂ given ACCEPT] | tỉ lệ | calibration |
| `selective_risk_ratio` | selective_pair_flip_rate/selective_risk_pred | không thứ nguyên | calibration chính |
| `ece_logbins` | Σ_b n_b/n abs(mean(label)_b−mean(p̂)_b) | tỉ lệ | phụ |
| `auroc` | AUROC p̂ với nhãn m<0 | không thứ nguyên | discrimination |
| `e2e_cost_ms` | E[chi phí action thực thi, gồm fallback] | ms | RQ2 sau khóa fallback L5.1 |
| `tie_rate` | P(ít nhất hai path cùng đạt minimum ở twin hoặc truth) | tỉ lệ | hygiene |
| `n_decisions`, `n_accept`, `n_pair_flip_accept` | số hợp lệ, ACCEPT, và ACCEPT bị đảo cặp | đếm | hygiene |

Selective: gộp counts qua run trong từng OD; F/A là risk thật, P/A là risk dự đoán
với P=Σ_ACCEPT p̂; ratio=F/P. Trung bình đều các risk/ratio của OD, báo cáo
từng OD. Bootstrap 10.000 lần lấy lại toàn bộ run (seed bootstrap 230923), giữ
cùng chỉ số run khi so paired. Không bootstrap các quyết định riêng lẻ.

A=0: selective risk và ratio null; P=0: ratio null. Luôn báo cáo số run/OD
không ACCEPT, số fit invalid và số bootstrap replicate undefined. Nếu một OD
target undefined, aggregate đều OD cũng undefined; không âm thầm bỏ OD đó.
Nếu >5% bootstrap replicate undefined, không xuất CI định lượng. Nếu F=0
không diễn giải CI bootstrap [0,0] là chắc chắn không rủi ro: báo insufficient events.
Dưới 25 lỗi ACCEPT/OD trên toàn batch: flag ít sự kiện, không claim calibration
đạt; mốc 25 chỉ là cảnh báo (iid relative SE≈20%), không đảm bảo precision với chuỗi tương quan.

ECE dùng biên {0,1e−4,1e−3,1e−2,1e−1,1}, trái đóng/phải mở, bin cuối gồm 1;
bin rỗng trọng số 0. AUROC null khi thiếu một lớp; nêu rõ phân phối tuổi khi trộn.
Tie là equality chính xác, không dùng tolerance ngầm; numerical assertions riêng dùng atol=1e−12.
ε=0 trùng decision error chỉ khi không tie. Harmful dùng strict >.

## 3. Quy ước gate và validity

- C1: ACCEPT khi m̂≥q̂. C2: ACCEPT khi m̂≥q̂−ε.
- q̂ phải fit từ s_pair cho K=2; s_all cho K≥3. Score thật chỉ biết sau quyết định.
- Nếu score≤q̂, regret≤max(0,q̂−m̂) cho cặp (s_pair) hoặc mọi path (s_all).
  C1 cho regret=0; có tie vẫn có thể khác index a*. C2 cho regret≤ε.
- Coverage conformal marginal không tự suy ra selective risk≤α:
  P(harmful AND ACCEPT)≤α chỉ cho cận selective≤α/P(ACCEPT) khi assumptions hợp lệ.
  Temporal dependence và conditioning theo bin cần chứng minh/kiểm riêng.
- Chi phí được định nghĩa tại t. T_dec nhỏ so với τ chỉ cần nếu diễn giải như
  delay suốt epoch; instantaneous estimand vẫn tồn tại với T_dec lớn.
- Forecast chọn action khác hold phải dùng regret/nhãn theo action forecast;
  không dùng p_flip của cặp hold làm risk mọi path ở K>2.
- Null e01: Gaussian không clip + affine cost + K=2; Sheppard chỉ kiểm μ_D=0.
- Link chung triệt tiêu đại số cho một cặp cố định với additive cost, kể cả khi
  có tương quan; đổi joint distribution hoặc đổi cặp chọn có thể đổi risk.

## 4. VD1–VD6: lời giải tham khảo đã kiểm bằng code

Agent đã đọc đáp án trong lesson trước khi giải. Đây không phải bài tác giả tự
làm trước khi xem đáp án; không có ghi chép lỗi cá nhân để tái dựng.

| VD | (â,â₂,a*) | m̂ | m | e từng path | s_pair | s_all | error | regret ms | contender |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| 1 | A,B,B | 0,2 | −0,2 | 0,3;−0,1 | 0,4 | 0,4 | 1 | 0,2 | true |
| 2 | A,B,A | 40 | 35 | 3;−2 | 5 | 5 | 0 | 0 | true |
| 3 | A,B,B | 0,02 | −0,02 | 0,03;−0,01 | 0,04 | 0,04 | 1 | 0,02 | true |
| 4 | A,B,A | 2 | 0,4 | 1;−0,6 | 1,6 | 1,6 | 0 | 0 | true |
| 5 | A,B,C | 1 | 0,5 | 2;1,5;−2 | 0,5 | 4 | 1 | 1 | false |
| 6 | A,B,B | 0,6 | −0,4 | 0,8;−0,2 | 1 | 1 | 1 | 0,4 | true |

VD2: sai số có dấu là +3 và −2 ms (độ lớn 3 và 2). Lớn hơn VD1 nhưng margin
40 ms hấp thụ được sai số, quyết định đúng. State error lớn chưa đủ kết luận harmful.

VD3: với ε=0,5, regret=0,02 nên harmful=0 dù decision error=1.
Metric đúng/sai không đo được mức nghiêm trọng.

VD4: C1 ACCEPT (2≥1,5); quyết định đúng dù score 1,6>1,5.
Score vượt quantile làm mất chứng nhận cho mẫu, không đồng nghĩa chọn sai.

VD5: với q̂=0,8, gate so margin vẫn ACCEPT (1≥0,8) cho cả hai cách đặt tên score.
Pair score≤q̂ chỉ chứng nhận thứ tự A/B; global optimum C nằm ngoài cặp.
All-score=4>q̂: sự kiện coverage thất bại, không có global certificate cho mẫu này.
Không được dùng truth để đổi ACCEPT thành ABSTAIN. Quantile all-score thực tế
phải được hiệu chỉnh riêng; chưa có calibration thì chưa biết q̂_all bằng bao nhiêu.

VD6: C1 ABSTAIN (0,6<1); C2 ACCEPT (0,6≥1−0,5).
Score=1≤q̂, cận regret=0,4 ms; thực tế error=1, regret=0,4≤0,5, harmful=0.
C2 có thể nhận thêm lỗi vô hại; kiểm float bằng tolerance, không sửa inequality định nghĩa.

### VD7–VD8 — lời giải tham khảo của agent, không thay bài làm tay

Người dùng yêu cầu agent điền và kiểm. Hai lời giải sau là đáp án tham khảo đã xem
đề trong Lesson 0.5; không ghi nhận là tác giả đã tự làm không dùng code/AI.

VD7: â=A, â₂=B, a*=B; m̂=0,8 ms, m=−0,9 ms. Sai số e_A=1,5,
e_B=−0,2, e_C=−1,8 ms. Vì vậy s_pair=1,7 ms và
s_all=max(|e_A−e_A|,|e_B−e_A|,|e_C−e_A|)=max(0;1,7;3,3)=3,3 ms.
Contender=true, decision error=1,
regret=0,9 ms, harmful tại ε=1 ms bằng 0 (strict regret>ε). C1 ABSTAIN vì
0,8<1,5; C2 ACCEPT vì 0,8≥1,5−1. C2 chỉ hứa regret≤ε trên sự kiện
s_all≤q̂; mẫu này có 3,3>1,5 nên certificate không áp dụng. Kết quả thực tế vẫn
0,9≤1 là đúng một cách ngẫu nhiên, không phải lời hứa đã được chứng nhận.

VD8: r=0,741, v=2sqrt(1−r²)≈1,343 ms trong cả hai trường hợp.
Với μ_D=0: c=0+0,741(1−0)=0,741; m̃≈0,552; p̂≈Phi(−0,552)≈0,291.
Với μ_D=4: c=4+0,741(1−4)=1,777; m̃≈1,323; p̂≈Phi(−1,323)≈0,093.
Cùng margin cũ và cùng tuổi nhưng conditional mean-reversion hướng về hai mean
khác nhau, nên risk khác. W_ref cũ có κ lớn, khiến mean lấn át fluctuation và làm
decision quá dễ; D12 giữ κ_ref=0,5 trong các cell đối chứng.

## 5. Sáu lựa chọn v1 (2026-09-23)

### 5.1 T_dec — Q1=a, bổ sung jitter

- Loại: estimator knob cho RQ1 dừng/exogenous; system parameter cho sticky RQ2.
- Giá trị: epoch 0,1τ; t_j=t_start+(j+U_j)·0,1τ, U_j uniform[0,1) độc lập
  và độc lập traffic. Dùng CRN lịch này giữa các phương pháp.
- Lý do: lấy mẫu dày để quan sát margin nhưng không coi chúng độc lập.
  Chỉ random một phase/run vẫn khóa pha bên trong run khi chu kỳ commensurate;
  jitter từng epoch tránh điều đó.
- Hệ quả: khoảng hai quyết định liên tiếp không cố định; lưu timestamp thật.
- Xem lại: L5.1 sticky/wait; simulator dùng OU transition đúng theo khoảng thời gian.

### 5.2 W — Q2=b, Q8=a

- Phương án B: e02 dành cho sai số tham số do W hữu hạn; W_ref=200τ,
  mức {10,50,200}τ; OLS trễ với residual SD ddof=2.
- Lý do: không giả định 200τ đủ để hết sai số; đây là nguồn risk cần đo.
- Validity e01: oracle affine Gaussian kiểm bằng sai số Monte Carlo; operational
  không khớp oracle không tự động là bug. Mốc calibration quan trọng là ratio ngoài
  [0,8;1,2], tương ứng sai lệch tương đối 20%, là SESOI thiết kế chứ không độ chính xác đã đạt.
- Hệ quả: giữ W cố định trước e03–e05; có oracle song song để phân biệt lỗi mô hình
  với lỗi fit. Không tự tăng W khi thấy test lệch.
- Xem lại: trace không đủ W hoặc regime shift; dùng horizon có thật, ghi amendment.

### 5.3 Khởi tạo — Q3=a

- Giá trị: OU từ N(μ,σ²); warm-up ít nhất W+z_max để có lịch sử cho mọi mức z.
- Lý do: loại transient của mô hình, phân biệt warm-up lịch sử với burn-in.
- Hệ quả: trace thật không thể tự tạo phân phối dừng; chia chronological và báo
  nonstationarity. Markov switching cần joint stationary initialization, chỉ lấy
  stationary regime label chưa bảo đảm joint process dừng.
- Xem lại: thêm switching/trace, kiểm phân phối đầu run.

### 5.4 Estimator selective — Q4=b

- Giá trị: pooled trong từng OD, bootstrap nguyên run, rồi mean đều OD theo §2.
- Ngân sách cố định: 100.000 quyết định đánh giá/run, 10 seed; Δt=0,01τ.
- Lý do: xử lý run có ít ACCEPT, không condition việc dừng theo lỗi quan sát.
- Kiểm precision: n_accept<10.000/run là cảnh báo coverage thấp; <25 lỗi pooled/OD
  là cảnh báo không đủ sự kiện. Không loại run hay kéo dài theo hai ngưỡng này.
- Nếu precision thiếu: báo inconclusive; thiết kế batch mới dựa trên pilot độc lập,
  khóa horizon trước khi chạy. Bootstrap không chữa được thiếu independent runs.
- Xem lại: e01 benchmark precision, trước confirmatory.

### 5.5 Calibration chính — Q5=a

- Giá trị: selective_risk_ratio, kèm actual/predicted risk, coverage, counts, CI.
- Lý do: so quan sát với đúng dự báo trên cùng tập ACCEPT; không nhầm ngưỡng α
  với risk trung bình dự đoán.
- Phụ: ECE logbins, reliability, AUROC; ratio không dùng khi predicted risk=0.
- Hệ quả: gần risk=0 ratio dễ nhiễu; kiểm count và sai số tuyệt đối trước diễn giải.
- Xem lại: L5.1 nếu cần cam kết risk theo yêu cầu operator.

### 5.6 ε — Q6=a

- Chính: 2 ms; sensitivity {0;0,5;1;5} ms.
- Neo: thang delay và bất định đo D1; không claim ngưỡng cảm nhận ứng dụng.
- Số liệu tự tính lại trên 176 dòng, chia rho trái đóng/phải mở:

| rho | n | median delay_mean_ms | median se_batch_mean_ms |
|---|---:|---:|---:|
| [0,50;0,70) | 60 | 1,0831 | 0,0524 |
| [0,70;0,85) | 57 | 3,3434 | 0,1967 |
| [0,85;0,95) | 35 | 8,0789 | 0,2925 |
| [0,95;1,05) | 24 | 13,0116 | 0,3029 |

- Lý do: 2 ms cao hơn SE link điển hình vài lần, vẫn nằm trong thang biến động
  delay nhiều ms; các mức 0,5–5 kiểm sensitivity một bậc độ lớn.
- Hệ quả: đây không phải chứng minh regret 2 ms vượt bất định path; covariance,
  nội suy và link chung phải xét riêng. D1 là lookup truth của simulation,
  không ground truth vật lý hoàn hảo.
- Xem lại: e06 thang WAN hoặc nguồn SLA; phải khai trước khi đổi mức chính.
