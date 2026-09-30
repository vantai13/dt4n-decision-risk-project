# O1 — Sở hữu pipeline đã cho PIVOT (Phần A: L1.1–L1.2)

> Nội dung do tác giả tự viết; Codex chỉ sửa tiêu đề và chuẩn hóa vị trí lưu file.

## §1. Pipeline

### 1.1 `f04b.workload_after`

**Làm gì:**
Hàm này theo dõi workload còn lại trong queue sau các sự kiện đến/phục vụ. Workload \(V\) có thể hiểu là lượng thời gian phục vụ còn phải hoàn thành trước khi packet mới được phục vụ.

**Vì sao cần:**
DES cần biết queue hiện đang tích bao nhiêu công việc để tính delay thực tế của packet và xác định trường hợp buffer đầy/drop.

**Nếu sai:**
Delay DES \(D\) sẽ sai ngay từ tầng mô phỏng. Khi đó \(I=D_{cur}-D_{alt}\), harm, gain, headroom và toàn bộ decomposition F6/F7 đều sai. Sai điều kiện đầy buffer đặc biệt ảnh hưởng các cell tải cao và K nhỏ.

---

### 1.2 `f04b.one_path`

**Làm gì:**
Mô phỏng một path theo thời gian và tạo các đại lượng như tải đo được \(\hat\rho\), delay DES và các đại lượng dùng để so với approximation.

**Vì sao cần:**
Đây là cầu nối giữa workload stochastic và dữ liệu mà NDT/policy thật sự nhìn thấy tại từng decision epoch.

**Nếu sai:**
Nếu \(\hat\rho\) sai thì twin input sai; nếu delay DES sai thì ground truth \(I\) sai. Khi đó cả static, oracle và K2 đều được đánh giá trên dữ liệu sai.

---

### 1.3 `f04b.simulate_pair`

**Làm gì:**
Ghép hai path thành một episode hai lựa chọn A/B, với random stream được tách bằng `spawn(2)`.

**Vì sao cần:**
Policy phải quyết định giữa current path và alternative path. Hai path cần stochastic realization riêng nhưng vẫn được sinh theo một cơ chế seed có kiểm soát để CRN/reproducibility hoạt động.

**Nếu sai:**
Quan hệ ngẫu nhiên giữa A và B bị sai, làm \(I_A=D_A-D_B\), \(\hat I_A\), gain và paired comparison sai. Các CI theo seed cũng có thể bị phồng hoặc thu nhỏ giả tạo.

---

### 1.4 `f02.static_run`

**Làm gì:**
Chạy luật static threshold tuần tự qua các epoch. Nếu score của alternative vượt threshold thì switch; nếu không thì stay. Current path ở epoch tiếp theo phụ thuộc quyết định trước đó.

**Vì sao cần:**
Đây là baseline chính. Không thể đơn giản vector hóa toàn bộ epoch vì decision ở epoch trước thay đổi current path ở epoch sau.

**Nếu sai:**
Trajectory của S0 sai, kéo theo \(J(S0)\), harm, gain, reference trajectory và nhiều estimand về sau sai.

---

### 1.5 `f02.orient`

**Làm gì:**
Chuyển dữ liệu đang được lưu theo A/B thành góc nhìn `current/alternative`.

Nếu current=A:

\[
I=I_A
\]

Nếu current=B:

\[
I=-I_A
\]

**Vì sao cần:**
Tất cả policy phải dùng một convention:

\[
I>0 \Rightarrow switch\ có\ lợi
\]

bất kể current path là A hay B.

**Nếu sai:**
Một nửa direction có thể bị hiểu ngược dấu. Harm, gain, oracle label, \(p_-\), K2 và decomposition đều bị ảnh hưởng.

---

### 1.6 `f02.tune_static`

**Làm gì:**
Tìm threshold static tốt nhất trên calibration seeds, dưới ràng buộc harm.

**Vì sao tune theo \(J\), không phải chỉ theo decision-level gain:**
Policy tự tạo trajectory của nó. Một policy ở lâu trên path xấu có thể tự tạo nhiều opportunity có gain lớn, nên nếu chỉ tune theo gain tại các decision point thì có thể thưởng sai policy đó. \(J\) đo delay thật mà flow trải qua trên toàn trajectory.

**Nếu sai:**
Baseline có thể bị tune quá yếu hoặc quá mạnh. Khi đó gap K2−Static bị thổi phồng hoặc thu nhỏ và kết luận về value của adaptation không còn công bằng.

---

### 1.7 `f02.BinOracle`

**Làm gì:**
Chia belief/state thành các bin và dùng dữ liệu oracle để ước lượng các đại lượng như:

\[
\bar I,\qquad p_-
\]

trong từng vùng state.

**Vì sao cần:**
K2 không được biết tương lai trực tiếp; nó chỉ được dùng một belief/oracle estimate được học từ oracle seeds.

`min_count` giúp tránh dùng những bin quá ít mẫu, nơi mean và probability rất nhiễu.

**Vì sao học dọc reference trajectory:**
Oracle cần đại diện cho distribution state mà decision rules thực sự được so trên đó. Nếu học trên state distribution khác hẳn, evaluation có thể không còn cùng support.

**Nếu sai:**
\(\bar I\), \(p_-\), \(\lambda\), SC, K2 và toàn bộ center/pure decomposition sai.

---

### 1.8 `f02.tune_lambda`

**Làm gì:**
Tìm \(\lambda\) nhỏ nhất sao cho:

\[
E[a\,p_-]\le \alpha
\]

với:

\[
a=1[\bar I-\lambda p_->0]
\]

**Vì sao là \(\lambda\) nhỏ nhất:**
\(\lambda\) càng lớn càng phạt risk mạnh. Sau khi harm budget đã được đáp ứng, tăng tiếp chỉ làm policy bảo thủ và bỏ mất gain.

Nếu \(\lambda=0\) đã thỏa budget:

\[
K2(\alpha)=K2(\infty)
\]

và risk penalty không còn cần thiết.

**Nếu sai:**
K2 không còn đúng risk budget, nên safety gap và pure adaptation đều mất ý nghĩa.

---

### 1.9 `f04b.evaluate`

**Làm gì:**
Đánh giá các policy trên test seeds và tạo những cột như static gain, K2 gain, K2∞ gain, headroom và harm.

**Vì sao cần:**
Đây là nơi các decision rules được chuyển thành các con số cuối dùng cho F6.

**K2(∞) là gì:**
Là K2 với:

\[
\lambda=0
\]

nên switch nếu:

\[
\bar I>0
\]

không còn penalty do harm budget.

**Nếu sai:**
Bảng F6 và toàn bộ decomposition static/adaptation/safety/information sai.

---

### 1.10 `f05.features` / `GridOracle`

**Làm gì:**
Mở rộng cách xây oracle từ binning cũ sang state representation/grid có nhiều chiều hơn.

**Vì sao cần:**
F5/F6 muốn kiểm oracle giàu state hơn và tách value do center/width/information.

**Vì sao cần `oracle_same`:**
Khi hai implementation được đặt vào cùng trường hợp đặc biệt, chúng phải cho cùng kết quả. Đây là sanity check chống việc tưởng rằng gain đến từ information mới trong khi thật ra do implementation khác.

**Nếu sai:**
Có thể gán nhầm gain cho richer information/oracle.

---

### 1.11 `f05.tune_center`

**Làm gì:**
Tìm threshold trên posterior center:

\[
\bar I>H_c
\]

sao cho harm dự đoán thỏa ngân sách.

**SC khác K2 ở đâu:**

SC dùng:

\[
\bar I>H_c
\]

K2 dùng:

\[
\bar I-\lambda p_->0
\]

SC biết center nhưng không dùng width/risk từng epoch. Vì vậy:

\[
K2-SC
\]

cô lập phần value do risk/width reasoning tốt hơn.

**Vì sao SC phải dùng cùng harm criterion:**
Nếu SC và K2 bị ràng buộc khác nhau thì gap trộn decision sophistication với constraint khác nhau.

---

### 1.12 `f05.evaluate`

**Làm gì:**
Tạo decomposition của value.

Các mốc cơ bản:

\[
S0 \rightarrow SC \rightarrow K2(\alpha)
\rightarrow K2(\infty)\rightarrow Headroom
\]

Từ đó tách:

\[
SC-S0
\]

=center gain,

\[
K2-SC
\]

=pure width/risk gain,

\[
K2(\infty)-K2(\alpha)
\]

=safety cost,

\[
Headroom-K2(\infty)
\]

=information gap.

**Nếu sai:**
Paper có thể kết luận sai rằng gain đến từ uncertainty width trong khi thực ra đến từ center hoặc information.

---

# 1.2 Data flow

Flow logic:

```text
seed
 ↓
stream key + spawn
 ↓
simulate path A/B
 ↓
episode
 ↓
chia calibration / test / oracle

CAL
 ↓
tune static
 ↓
reference trajectory

ORACLE
 ↓
orient theo reference trajectory
 ↓
learn oracle
 ↓
Ibar, p-, s

CAL + oracle prediction
 ↓
tune lambda / center threshold

TEST
 ↓
run policies
 ↓
gain + harm + J
 ↓
decomposition
```

Điểm dễ data leakage nhất là để **test seeds đi vào bước tune threshold, tune λ hoặc học oracle**. Test chỉ được dùng sau khi mọi policy parameter đã cố định.

---

# 1.3 Phân rã

Định nghĩa các mốc:

\[
S=\text{static}
\]

\[
K=K2(\alpha)
\]

\[
K_\infty=K2(\infty)
\]

\[
H=\text{headroom}
\]

Ta có:

\[
H
=
S+(K-S)+(K_\infty-K)+(H-K_\infty)
\]

vì các term trung gian triệt tiêu.

Với P2:

\[
3.700+0.149+1.289+9.418=14.556\text{ ms}
\]

Ý nghĩa:

- 3.700 ms: static đã lấy được;
- 0.149 ms: thêm do adaptation;
- 1.289 ms: phần phải hy sinh do safety constraint;
- 9.418 ms: phần còn mất vì information không đủ.

Đây là **đồng nhất thức**, không phải một empirical law.

---

# 1.4 CI của gap P2

Unit of replication phải là **seed**, không phải epoch.

Với 8 seed:

\[
CI_{95}
=
\bar x
\pm
t_{0.975,7}
\frac{s}{\sqrt8}
\]

và:

\[
t_{0.975,7}=2.365
\]

Sample standard deviation phải dùng:

\[
ddof=1
\]

Nếu dùng hàng nghìn epoch như independent samples, CI sẽ hẹp giả tạo vì các epoch trong cùng một simulation seed không phải independent experimental replicates.

---

# 1.5 Bảng 10 epoch — cách đọc

Mỗi epoch nên theo dõi:

| epoch | current | \(\hat I\) | static | \(\bar I\) | \(p_-\) | \(u\) | K2 | \(I\) |
|---|---|---:|---|---:|---:|---:|---|---:|

với:

\[
u=\bar I-\lambda p_-
\]

Điểm cần nhìn là những epoch:

\[
a_{K2}\neq a_{Static}
\]

Nếu cả hai đều switch hoặc đều stay thì uncertainty reasoning không tạo thêm decision value ở epoch đó.

---

# 1.6 Ba câu tự kiểm

### Vì sao tune theo J?

Vì policy tạo ra trajectory của chính nó. Decision-level gain có thể đánh giá cao một policy ở lại path xấu quá lâu vì policy đó tự tạo ra nhiều opportunity lớn. \(J\) đo delay thực mà flow phải chịu nên phù hợp hơn để tune policy.

### Vì sao oracle học dọc reference trajectory?

Để các policy được so trên cùng state distribution/support. Nếu oracle học trên distribution khác với states mà reference policy gặp, estimate có thể không đại diện cho bài toán decision-level đang đánh giá.

### Vì sao P1 có thể thấy K2 gain nhỏ hơn static mà chưa chắc là bug?

Một point estimate nhỏ hơn chưa đủ kết luận bug. Phải xem đúng estimand, trajectory, harm constraint và CI. K2 tối ưu theo risk-constrained criterion, không phải đảm bảo point estimate gain test luôn lớn hơn static trong mọi finite sample.

---

# §2. Kín sách — logic cần tái tạo

## `static_best`

Static chỉ được chọn một threshold \(H\):

\[
a_i(H)=1[\bar I_i>H]
\]

và phải thỏa:

\[
\frac1N\sum_i a_i(H)p_{-,i}\le\alpha
\]

Trong các threshold khả thi, chọn threshold cho gain lớn nhất.

## `k2_rule`

K2:

\[
a_i(\lambda)
=
1[\bar I_i-\lambda p_{-,i}>c]
\]

Chọn \(\lambda\) nhỏ nhất sao cho:

\[
\frac1N\sum_i a_i(\lambda)p_{-,i}
\le\alpha
\]

Nếu hòa:

\[
\bar I-\lambda p_-=c
\]

thì stay.

---

# §3. Cỡ mẫu và vấn đáp

## 3.1 Harm-event count

Muốn kỳ vọng ít nhất 100 harm events:

\[
\alpha N\ge100
\]

Do đó:

\[
\alpha=0.5\%
\Rightarrow
N\ge20000
\]

\[
\alpha=1\%
\Rightarrow
N\ge10000
\]

\[
\alpha=2\%
\Rightarrow
N\ge5000
\]

---

## 3.2 CI với 90 seed

Nếu:

\[
sd_{seed}=0.478ms
\]

thì:

\[
h
\approx
1.99
\frac{0.478}{\sqrt{90}}
\approx0.10ms
\]

Nếu effect cần phát hiện chỉ:

\[
0.06ms
\]

thì ngay cả 90 seed vẫn chưa tạo một separation rất mạnh; CI có cùng bậc hoặc lớn hơn effect.

---

# 3.3 Vì sao dự đoán f04b ban đầu 1–4 ms lại sai?

Lập luận ban đầu tập trung vào việc queue memory tạo heterogeneity/uncertainty.

Nhưng sau T4 §3 ta biết pure value còn phụ thuộc:

\[
gap_{\text{pure}}
\approx
\frac{f_0\beta^2\kappa^2}{2a'}
\]

Ngay cả khi \(\kappa\) có thật, nếu:

\[
f_0
\]

rất nhỏ vì decision boundary nằm ở tail thì chỉ rất ít epoch có khả năng bị uncertainty làm đổi quyết định.

DES sau đó cho thấy boundary khoảng percentile 95, nên \(f_0\) là bottleneck mà lập luận ban đầu đã bỏ qua.

---

# 3.4 Phiếu vấn đáp

### 1. Vì sao decomposition cộng đúng headroom?

Vì nó là telescoping identity:

\[
S+(K-S)+(K_\infty-K)+(H-K_\infty)=H
\]

Các mốc trung gian triệt tiêu.

### 2. Vì sao tune static theo J?

Vì static tự tạo trajectory. \(J\) đo delay user thực chịu; gain decision-level có thể bị bias bởi chính trajectory mà policy tạo ra.

### 3. Vì sao adaptation gap nhỏ?

Không phải vì uncertainty bằng 0. \(\kappa\) trên DES có thật, nhưng boundary nằm rất xa tail nên \(f_0\) nhỏ; rất ít epoch ở vị trí mà width có thể đổi action.

### 4. Uncertainty phải lớn cỡ nào mới đáng?

Không có một giá trị \(\kappa\) universal. Local approximation là:

\[
gap_{\text{pure}}
\approx
\frac{f_0\beta^2\kappa^2}{2a'}
\]

nên cùng một \(\kappa\) nhưng \(f_0,\beta,a'\) khác thì practical value khác.

### 5. Vì sao F7 dùng path khác risk?

F6 mới kiểm path đối xứng. F7 kiểm threat rằng hai path có dynamics/risk khác nhau có thể tạo structure mà static cũ không hấp thụ được. Sau review phải cho static threshold theo direction để comparison công bằng.

### 6. Đổi estimand có phải chỉnh tiêu chí sau kết quả?

Nếu đổi sau khi nhìn outcome thì có nguy cơ post-hoc. Trong project này thay đổi phải được lý giải, ghi log và khóa trước experiment mới; các kết quả cũ vẫn giữ nguyên.

### 7. Static F7 có bị làm yếu?

Không. S0dir biết current path identity giống K2 và được tune hai threshold riêng. Đây là knowledge parity; mục tiêu là cô lập decision sophistication chứ không cho K2 thêm information.

### 8. Có ai đã làm decomposition C/W/I này chưa?

Hiện chỉ có thể nói đây là **strong candidate gap trong phạm vi literature matrix đã tìm**. Chưa đủ bằng chứng để tuyên bố tuyệt đối rằng không có ai từng làm.

---
