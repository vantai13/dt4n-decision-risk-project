# Vì sao width nhỏ, biến nào làm nó tăng — 2026-10-01

## Kết luận có số đo

Đã tìm được cấu hình cho lợi ích K2−SC khoảng **11–13 ms**, kiểm trên 20 seed test mới sau khi chọn cấu hình bằng seed khám phá. Mức tăng có hai nguồn: phân biệt rủi ro hữu ích hơn và headroom của hàng đợi lớn hơn. Không thay SESOI 8,1 ms, không đổi α để tạo các kết quả chính.

Đây là nghiên cứu khám phá được người dùng cho phép sau khi đã xem map/confirm/frontier. Cấu hình hệ thống đã thay đổi nên không đảo ngược kết luận VoIP của cấu hình cũ. Chưa có nguồn thực tế cho tổ hợp tham số mới.

Đã hoàn thành 85 lượt đánh giá chính: audit 5, screen 35, screen mở rộng 13, kiểm số 4, factorial 16, holdout 11, hội tụ probe 1. Các lượt có cấu hình trùng để đối chứng; không phải 85 hệ thống độc lập. Một cấu hình K=1328 thất bại trước khi có số đo. Bổ sung kiểm 5 luật trên 5 cấu hình holdout. Chạy lại 5 ô audit từ manifest cho CSV giống từng byte. Toàn bộ suite lần cuối: **91 passed in 4.38s**.

## 1. Phân rã chính xác con số 0,648 ms

Đặt I = D_hiện_tại − D_thay_thế, aK/aC ∈ {0,1} là quyết định đổi của K2/SC.

```text
Δ = E[(aK − aC) I]
  = P(K2-only) E[I | K2-only] − P(SC-only) E[I | SC-only]
  = P(aK ≠ aC) E[(aK − aC) I | aK ≠ aC].
```

Audit m069 trên đúng seed confirm/frontier cũ:

```text
K2-only: 3,595% × 37,523 ms = +1,349 ms
SC-only: 1,260% × 55,664 ms = −0,701 ms
                                    = +0,648 ms

Tương đương: 4,855% × 13,339 ms = 0,648 ms.
```

**Nguyên nhân số nhỏ:** hai luật giống nhau ở khoảng 95% quyết định. Trong phần khác nhau, lợi ích K2 lấy thêm bị trừ đi phần SC lấy được mà K2 bỏ qua. Không thể đem lợi ích trên một lần đổi so trực tiếp với gain trung bình trên mọi quyết định.

Với DES hiện tại, S ≤ D ≤ KS nên |I| ≤ (K−1)S:

```text
|Δ| ≤ P(aK ≠ aC) × (K−1)S.
```

Tại m069, S=1,2096 ms, K=83: với tỉ lệ bất đồng 4,855% như đã đo, trần này chỉ khoảng **4,816 ms**. Muốn đạt 8,1 ms mà vẫn giữ K/S, cần ít nhất khoảng **8,17%** quyết định bất đồng, ngay cả nếu mỗi bất đồng đều có tác động cực đại đúng hướng. Đây là điều kiện cần rất lạc quan, không phải dự đoán đủ để đạt.

Audit strict frontier của m069/m071/m085/m080/m083 cho **strict_minus_legacy_ms=0** ở cả 5 ô. Mã mới chỉ cho phép ngưỡng chọn cả nhóm đồng điểm và loại Ibar≤0 của K2; hạn chế của mã frontier cũ không gây con số thấp ở các ô được audit. Harm test của SC và K2 ở m069 đều đúng 0,2% khi tối ưu frontier.

## 2. Công thức tách headroom và chất lượng chọn

Đặt HR=E[max(I,0)], ηK=gainK/HR, ηC=gainC/HR. Khi HR>0:

```text
Δ = HR × (ηK − ηC).
```

Trên cùng 20 seed holdout mới:

| Cấu hình | HR (ms) | Δ/HR | Δ (ms) | Tỉ lệ bất đồng |
|---|---:|---:|---:|---:|
| base_m069 | 17,966 | 5,388% | 0,968 | 4,699% |
| joint_small | 13,586 | 12,153% | 1,651 | 11,689% |
| joint_large | 94,603 | 11,852% | 11,212 | 11,370% |

Từ base sang joint_large: **Δ tăng 11,58 lần = HR tăng 5,27 lần × phần HR lấy thêm tăng 2,20 lần**. Đây là đẳng thức từ kết quả, không phải hồi quy suy đoán.

joint_small tăng hiệu ứng dù HR giảm: phần cải thiện này không thể giải thích đơn thuần bằng phóng đại delay. Từ joint_small sang joint_large, tỉ lệ bất đồng gần giữ nguyên, nhưng tác động ròng trên mỗi bất đồng tăng từ 14,13 lên 98,61 ms: phần tăng này chủ yếu gắn với quy mô hàng đợi.

## 3. Vì sao rủi ro có thể giúp xếp hạng

Nếu twin biết đúng μ(x)=E[I|x] và p(x)=P(I<−ε|x), bài toán giới hạn hại kỳ vọng là:

```text
max_a E[a(x) μ(x)]  subject to E[a(x) p(x)] ≤ α.
Lagrangian: E[a(x)(μ(x)−λp(x))] + λα.
=> a(x)=1 khi μ(x)>λp(x), λ≥0.
```

Với p>0, K2 xếp theo μ/p; SC xếp theo μ. Nếu μ/p tăng đơn điệu theo μ trên phần μ>0 liên quan đến ngân sách, hai thứ hạng trùng nhau và không có dư địa cho width. Muốn có width, phải có các cơ hội lợi lớn nhưng rủi ro cao bị đổi thứ tự với cơ hội lợi vừa và rủi ro thấp.

Trong thực nghiệm, p của twin không chắc đúng sau khi điều kiện hóa theo quỹ đạo S0; vì vậy không coi K2 là tối ưu thật. Ngưỡng được tune bằng outcome calibration, test đo harm thật. Các thí nghiệm mới chỉ kiểm K2 như một họ thứ hạng có thể hữu ích.

## 4. Các biến vật lý: tăng gì và không thể tăng đơn điệu gì

Với L=12096 bit/gói, C tính bằng bit/s:

```text
S = L/C
σ² = ρ̄ r_f/C
R = ρ̄ S/T_tel                       (nhiễu đếm trong twin)
R/σ² = L/(T_tel r_f)                 (khi dùng mô hình flow trên)
Δ_ms = 1000 S · F(K, ρ̄_A/B, σ_A/B, τ_A/B/S,
                 T_A/B/S, H/S, a/S, d_A/B/S, ε/S, α, ...).
```

F còn phụ thuộc cơ chế stall, luật tham chiếu và thông tin twin; công thức là phân tích thứ nguyên của chính mô hình, không khẳng định hàm đóng đơn giản.

- **Tăng K:** mở rộng thang delay và headroom, nhưng cũng tăng trí nhớ hàng đợi và delay gói. Không phải cải thiện mạng chỉ vì width lớn hơn.
- **Tăng biến động tải σ/r_f:** trong vùng đã thử giúp tạo nhiều trạng thái đáng phân biệt; không nên kéo vô hạn vì OU Gauss, clipping và số flow nền sẽ mất hợp lý.
- **Giảm ρ̄ từ 0,95 xuống 0,8 trong tổ hợp mới:** giúp tăng chênh lệch tương đối và giảm delay trung bình; không có luật chung “tải càng cao càng tốt”.
- **Độ tươi lệch:** có thể tạo rủi ro khác nhau tại cùng μ, nhưng B quá cũ cũng có thể mất toàn bộ thông tin. Tăng chu kỳ B không bảo đảm lợi ích ngoài mẫu tăng.
- **A đo nhanh hơn:** giảm tuổi nhưng cửa sổ đếm ngắn hơn làm R tăng; vì vậy nhanh hơn không đồng nghĩa tốt hơn. Khi tăng r_f đồng thời, tương tác khác hẳn thay riêng T_A.
- **α:** tăng ngân sách có thể tăng width ban đầu, rồi làm hai luật gần nhau. Screen base có Δ khoảng 0,224/0,640/0,973/0,116 ms tại α=0,05%/0,2%/0,5%/2%; đây là đổi yêu cầu rủi ro, không dùng để tạo kết quả holdout chính (giữ α=0,2%).
- **Giảm C:** tăng S nhưng cũng đổi nhiễu đếm và trí nhớ queue so với τ,H,T. Screen tại 1 Mb/s gần mất hiệu ứng; holdout vẫn còn 2,609 ms nhưng nhỏ hơn nhiều mức nhân 10 ngây thơ. Kết luận đúng là không có tỉ lệ tăng đơn giản nếu chỉ giảm C.

## 5. Phân rã tương tác 4 biến, giữ buffer 100 ms

Chạy đầy đủ 16 tổ hợp của r_f={300k,600k}, ρ̄_A/B={0,95;0,8}, T_A={0,5;0,1}, T_B={30;60}, cùng α=0,2%, K=83, C=10 Mb/s, τ=10 s, H=0,5 s. Dùng seed khám phá, không dùng holdout để chọn lại.

Width tăng từ 0,6397 lên 1,9163 ms. Phân bổ Shapley (trung bình đóng góp biên qua mọi thứ tự đổi biến):

| Thay đổi | Đóng góp vào Δ tăng (ms) |
|---|---:|
| r_f 300k → 600k | +0,6862 |
| ρ̄_A/B 0,95 → 0,8 | +0,3207 |
| T_A 0,5 → 0,1 s | +0,0658 |
| T_B 30 → 60 s | +0,2040 |
| Tổng | **+1,2767** |

Đây là phân rã bảng mô phỏng đã chạy, có phân bổ tương tác; không phải hằng số nhân quả phổ quát. Riêng đổi T_A ở cấu hình gốc làm Δ giảm từ 0,640 xuống 0,521 ms, nhưng trong toàn bộ tổ hợp đóng góp trung bình lại dương nhỏ. Điều này giải thích vì sao chỉ thử một biến có thể bỏ qua tổ hợp tốt.

## 6. Công thức cấu hình làm Δ vượt 8,1 ms

Các cấu hình joint đều dùng:

```text
C = 10 Mb/s; ρ̄_A = ρ̄_B = 0,8; r_f = 600 kb/s
σ_A = σ_B = sqrt(0,8 × 600k / 10M) ≈ 0,2191
T_A = 0,1 s; T_B = 60 s; τ_A = τ_B = 10 s (trừ dòng tau30)
H = 0,5 s; a = 0,05 s; d = 0,1 s
α = 0,002; ε = 0,6048 ms; stall=0
K = 83 / 332 / 664.
```

20 seed calibration mới 72001–72020, 20 test mới 73001–73020. Danh sách holdout được ghi và commit b99ddfe trước khi mở các seed này.

| Cấu hình | K·S (ms) | Δ frontier [CI 95%] (ms) | Δ ngoài mẫu [CI 95%] (ms) | Harm K2/SC ngoài mẫu (% quyết định) |
|---|---:|---|---|---|
| base_m069 | 100,4 | 0,968 [0,741; 1,310] | 0,748 [0,478; 1,018] | 0,2375 / 0,3075 |
| joint_small | 100,4 | 1,651 [1,347; 2,054] | 1,673 [1,314; 2,031] | 0,1400 / 0,1163 |
| joint_medium | 401,6 | 6,075 [4,810; 7,870] | 6,386 [4,964; 7,807] | 0,1538 / 0,0988 |
| joint_large | 803,2 | 11,212 [8,291; 14,568] | 11,333 [8,548; 14,119] | 0,1525 / 0,0925 |
| joint_large_tau30 | 803,2 | 12,597 [9,776; 16,281] | 13,411 [9,499; 17,323] | 0,2258 / 0,2067 |
| quietB | 100,4 | 2,093 [1,642; 2,457] | 1,764 [1,367; 2,162] | 0,1713 / 0,2000 |

Frontier của joint_large dùng harm đúng 0,2% ở CẢ hai luật. Frontier là tối ưu trên test; cột ngoài mẫu là ngưỡng học từ calibration và bất đẳng thức harm trên test không được đảm bảo tự động. Đặc biệt base_m069 SC vượt cả 1,5α trên holdout này; không giấu dòng này. joint_large_tau30 cũng hơi vượt α, dù dưới 1,5α.

quietB giữ cấu hình m069, chỉ chia σ_B cho 3; đây là một nhánh tăng hiệu ứng ở buffer nhỏ, nhưng chưa có ánh xạ thực tế hay novelty cho cấu hình.

## 7. Cái giá của con số lớn và kiểm độ vững

joint_large có delay trung bình A/B khoảng **117,54/116,55 ms**, so với joint_small **19,47/19,54 ms**. Buffer tăng tối đa 803 ms tạo cơ hội tránh delay rất lớn; không thể coi tăng buffer là khuyến nghị vận hành VoIP. Virtual probe rejection A/B khoảng **0,895%/0,821%**, chỉ là tỉ lệ từ chối các probe ảo trên lịch đều, không phải loss của gói thật được đếm trực tiếp. Metric vẫn chấm delay gói được nhận; chưa tối ưu loss/SLA.

| Kiểm trên joint_large | Δ frontier | Δ ngoài mẫu exact-threshold |
|---|---:|---:|
| 64 GH, 101 probe | 11,212 ms | 11,333 ms |
| 256 GH, 101 probe | 11,410 ms | 10,919 ms |
| 256 GH, 401 probe | 11,526 ms | 10,974 ms |

Hiệu ứng không biến mất khi tăng độ chính xác tích phân và đo delay. Các kiểm này dùng cùng seed, không phải ba lần tái lập độc lập.

Chạy lại **đủ 5 luật với đúng evaluate_cell/tune_lambda_realized 400 điểm của confirm cũ** trên raw holdout:

- joint_large: width 11,113 ± 2,780 ms, gain SC=1,893 và K2=13,006 ms, harm SC/K2=0,0925%/0,1475%; đạt toàn bộ điều kiện C.
- joint_large_tau30: width 13,395 ± 3,909 ms; đạt C.
- joint_large_gh256: width 10,465 ± 2,521 ms; đạt C nhưng CI dưới khoảng **7,943 ms**, chưa vượt 8,1 ms với độ tin cậy 95% trong biến thể này.
- joint_small và quietB cũng đạt C.

Trong cả 5 cấu hình, baseline tốt nhất được chọn trên calibration là SC. Vì vậy không chỉ thắng SC trong khi thua một baseline tốt hơn đã có. Tuy nhiên kết luận “chắc chắn vượt SESOI 8,1 ms trong mọi biến thể tính số/tune” **chưa được hỗ trợ**. Số trung bình đã vượt mốc ở vùng tham số mới; yêu cầu thực tế và tiền đăng ký cho ứng dụng vẫn còn.

## 8. Đối chứng đổi thang: tại sao tăng số ms chưa đủ

Nếu đổi mọi thời gian t→qt và C→C/q (r_f→r_f/q để giữ σ), giữ K, ρ̄, α và ε/S:

```text
rhohat không đổi; tuổi và workload nhân q;
I, Ibar, headroom, gain, width nhân q;
p_harm, thứ hạng, hành động và width/headroom giữ nguyên.
```

Đã kiểm bằng unit test DES và dữ liệu q=16: trên holdout Δ **0,9679557 → 15,4872910 ms**, đúng ×16 đến sai số <1e−7. Nhưng link thành 0,625 Mb/s, buffer 1,606 s, H=8 s, τ=160 s, T_A=8 s, T_B=480 s, ε=9,6768 ms. Đây là hệ thống khác, không phải thuật toán tốt hơn 16 lần.

Giữ ε tuyệt đối ở mức cũ trong biến thể q=16: frontier còn 9,259 ms và ngoài mẫu chỉ 4,079 ms [0,797; 7,360]. Do đó phóng đại ε cùng thời gian có ảnh hưởng quan trọng; phải công khai nếu dùng phép đổi thang.

## 9. Giới hạn còn lại và kết luận nghiên cứu

1. Đây là mô phỏng OU, hai path độc lập, một flow nhỏ không đổi tải, twin biết tham số và một cửa sổ. Chưa phải ứng dụng thật; chưa kiểm twin lịch sử/Kalman hay feedback đường truyền.
2. Có chọn cấu hình sau khám phá; holdout tách seed và được khóa danh sách trước chạy nhưng vẫn là nghiên cứu khám phá, nhiều cấu hình/CI chưa hiệu chỉnh multiplicity.
3. Thế giới không hoàn toàn ghép cặp pathwise giữa mọi cấu hình: thay số gói/cửa sổ có thể đổi tiêu thụ RNG. Dùng cùng số seed không tự đảm bảo common random numbers hoàn chỉnh. Phân rã đẳng thức là chính xác; diễn giải cơ chế từ can thiệp có biến thiên Monte Carlo.
4. Cấu hình joint có khoảng 13,3 flow nền theo công thức, Gaussian tải âm khoảng 0,006%, trên trần lưới rho=1,4 khoảng 0,303%. DES clip tải âm, twin curve giữ biên ngoài lưới. Kiểm GH/probe không kiểm hết sai số này hoặc độ phân giải lưới đường cong.
5. K=1328 làm solver weights tràn số, đã ghi failures.json; không tuyên bố kết quả cho ô lỗi. K=664 đã qua các kiểm tính số nêu trên nhưng chưa phải bằng chứng hội tụ mọi xấp xỉ.
6. Exact-threshold exploratory calibration thay lưới λ 400 điểm; có kiểm lại pipeline 5 luật cũ để định lượng khác biệt.
7. Chưa tính chi phí mỗi lần đổi đường. Với các hành động giữ cố định, nếu mỗi lần đổi có chi phí c ms thì Δ_net = Δ − c[P(aK=1)−P(aC=1)]. Vì K2 có thể đổi nhiều hơn, lợi ích ròng cần được tính lại cho ứng dụng; công thức này chưa tune lại policy theo cost và chưa đưa cost vào định nghĩa harm.

Kết quả trả lời được yêu cầu: số thấp ban đầu do ít quyết định khác nhau và quy mô tác động nhỏ; đã tìm được cả nhánh cải thiện discrimination ở cùng buffer (khoảng 1,65–2,09 ms) và nhánh kết hợp headroom + discrimination (khoảng 11–13 ms). Nếu tiếp tục thành nghiên cứu ứng dụng, ưu tiên xác định hệ thống thật chấp nhận queue-delay scale này và kiểm lợi ích khi twin dùng lịch sử; không cần quét mù để làm số lớn thêm.

## 10. Tái lập và vị trí dữ liệu

Code: experiments/scan/{strict_frontier,explore_width,analyze_width}.py; diagnostics bổ sung ở des_world.py, không đổi các mảng telemetry/delay cũ.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m experiments.scan.explore_width --stage audit --bootstrap 100
.venv/bin/python -m experiments.scan.explore_width --manifest results/explore_width/verify_manifest.json --label verify_replay
# --manifest dùng đúng cấu hình/seed/bootstrap đã lưu; --label lưu riêng lần tái lập.
# screen_extended_manifest.json có cả K=1328 đã lỗi; xem failures.json và screen_checks_manifest.json.
.venv/bin/python -m experiments.scan.analyze_width
```

results/explore_width/:

- audit.csv: tái lập strict vs legacy và phân rã các ô gốc.
- screen.csv, screen_extended.csv, screen_checks.csv: mọi thử nghiệm khám phá đã thành công.
- factorial.csv, factor_attribution.csv: 16 tổ hợp và đóng góp Shapley.
- verify.csv, verify_seeds.csv: 11 cấu hình trên seed mới; số đầy đủ, CI và harm.
- numerical_robustness.csv: 256 GH/401 probe.
- five_rules_holdout.csv: đủ 5 luật theo pipeline confirm cũ.
- *_manifest.json: cấu hình đầy đủ và seed cho từng giai đoạn.
- failures.json: cấu hình lỗi được giữ lại.
- width_mechanisms.png / .pdf: biểu đồ nghiên cứu.
- raw/*.npz: cache tái lập từ seed, git-ignored; không push dữ liệu thô lớn.

Log terminal: results/scan/explore_{audit,screen,extended,checks,verify,factorial,numerical}_output.txt.
