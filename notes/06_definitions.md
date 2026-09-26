# Definitions — v2.1 (2026-09-25)

> Nguồn sự thật duy nhất cho ký hiệu, đơn vị và estimand. Soạn với hỗ trợ của công cụ AI; tác giả kiểm và chịu trách
> nhiệm nội dung. v2.1 theo nhận xét GVHD 2026-09-25: mục tiêu bằng ms, c thay κ, nhãn DES bằng tích phân chính xác,
> chỉ số H2 trên điểm quyết định. **Sửa file này TRƯỚC khi sửa code.** Đóng băng tới DP0.
> Bản v1 (top-2 margin): `notes/archive/v1_trust_gate/06_definitions.md`. Quyết định: K2, K3, K5, K6, K7, K17, K21, K22.

## Phần 1 — Dòng thời gian của một quyết định

```text
 cửa sổ đo            pipeline       quyết định   actuation        khoảng giữ (chấm điểm)
 [t_m − W, t_m] ──d──► twin nhận ···  t  ────a────► [t + a ,  t + a + H_hold]
        ● tâm cửa sổ                  │                        ● tâm khoảng giữ
        └──────── tuổi z ────────────┘                        │
        └─────────────────── tuổi hiệu dụng z_eff ─────────────┘
```

- Telemetry báo mỗi T_poll; twin dùng cửa sổ mới nhất đã nhận. Nếu quyết định không đồng bộ với telemetry,
  t − t_m phân bố đều trên [d, d + T_poll) (răng cưa) → jitter tuổi.
- z = (t − t_m) + W/2 (tính từ TÂM cửa sổ). z_eff = z + a + H_hold/2. z_eff chỉ dùng cho KỲ VỌNG; phương sai
  lấy từ cả quỹ đạo trên khoảng giữ.
- **Đính chính 2026-09-26:** câu trên về kỳ vọng chỉ đúng trong xấp xỉ **không có nhiễu đo**. Khi số đo
  `y` có nhiễu đếm với phương sai `R`, kỳ vọng tuyến tính có điều kiện của trung bình tải `G` trên khoảng giữ là
  `E[G | y] = μ + β(y − μ)`, với `β = Cov(G, y) / (V(W) + R)`; vì vậy không được thay `β` bằng
  `exp(−z_eff/τ)` trong kết luận định lượng.
- Epoch e: quyết định tại t_e = t_0 + e·H_hold; khoảng giữ [t_e + a, t_e + a + H_hold]; các khoảng giữ nối tiếp,
  không chồng nhau.

## Phần 2 — Ký hiệu

| Ký hiệu | Tên | Định nghĩa | Đơn vị | Tên trong code |
|---|---|---|---|---|
| L, C | kích thước gói, tốc độ link | gói cố định 1512 B | byte, bit/s | `pkt_bytes`, `link_bps` |
| S | thời gian phục vụ | L·8/C; đơn vị thời gian của DES (S = 1) | s | `service_s` |
| K | dung lượng hệ thống | số gói tối đa trong hệ thống, KỂ CẢ gói đang phục vụ (testbed: xem K7) | gói | `k_sys` |
| prop | trễ lan truyền của path | hằng số theo path | s | `prop_s` |
| ρ_l(t) | tải thật của link l | tải đề nghị / capacity | — | `rho` |
| μ, σ, τ | tham số OU | trung bình, độ lệch chuẩn dừng, thời gian tương quan | —, —, s | `ou_mu`, `ou_sigma`, `ou_tau_s` |
| C_a² | burstiness | hệ số biến thiên bình phương của khoảng cách gói đến | — | `ca2` |
| W, T_poll, d | telemetry | cửa sổ đếm; chu kỳ báo; trễ pipeline | s | `win_s`, `poll_s`, `pipe_delay_s` |
| n_W | số gói đếm | gói truyền + gói bị drop trong cửa sổ | gói | `n_win` |
| ρ̂_l | tải đo | n_W·S/W (tải đề nghị) | — | `rho_hat` |
| z, z_eff | tuổi, tuổi hiệu dụng | Phần 1 | s | `age_s`, `age_eff_s` |
| a, H_hold | actuation, khoảng giữ | Phần 1; H_hold = độ dài epoch | s | `act_delay_s`, `hold_s` |
| cur, alt | đường hiện tại / thay thế | mốc so sánh luôn là cur; hai path: alt là path còn lại | — | `path_cur`, `path_alt` |
| r_p | tốc độ probe | probe ảo Poisson trên MỖI path, không chiếm tải (K5) | 1/s | `probe_rate_hz` |
| D_cur, D_alt | delay trên khoảng giữ | trung bình delay (prop + chờ + phục vụ) của probe ĐƯỢC NHẬN trên khoảng giữ | ms | `delay_cur_ms`, `delay_alt_ms` |
| I_D | cải thiện delay thật | D_cur − D_alt (> 0: đổi có lợi) | ms | `imp_delay_ms` |
| loss_cur, loss_alt | loss trên khoảng giữ | probe bị drop / probe gửi | — | `loss_cur`, `loss_alt` |
| I_L | cải thiện loss thật | loss_cur − loss_alt (> 0: đổi giảm loss) | — | `imp_loss` |
| F | tập thông tin | đúng những gì policy thấy trước quyết định (K6); KHÔNG gồm probe | — | `info` |
| Î | cải thiện dự đoán | thống kê điểm do twin tính từ F | ms | `imp_hat_ms` |
| Ĉ_cur | delay dự đoán của cur | dùng cho ngưỡng tương đối (K22) | ms | `cost_hat_cur_ms` |
| p+, p− | xác suất có điều kiện | P(I_D > ε \| F), P(I_D < −ε \| F) | — | `p_plus`, `p_minus` |
| s | bất định | sd(I_D \| F) | ms | `sd_imp_ms` |
| M | số mẫu Monte Carlo | dùng ước lượng p± | — | `n_mc` |
| ε, δ | ngưỡng "đáng kể" | delay; loss: δ = 10⁻³ (K3, ITU-T Y.1541, lớp thời gian thực) | ms, — | `eps_ms`, `delta_loss` |
| α | ngân sách harm | trên MỌI epoch (K2) | — | `alpha` |
| Ī | cải thiện kỳ vọng | E[I_D \| F]; khác Î gần bão hoà (Jensen) | ms | `imp_exp_ms` |
| c | chi phí mỗi lần đổi | chính c = 0; độ nhạy {0,25; 1}·S (K21) | ms | `c_switch_ms` |
| λ | giá của harm | ms kỳ vọng sẵn sàng bỏ ra để tránh một lần đổi gây hại; λ ≥ 0 nhỏ nhất đạt harm ≤ α (K2) | ms | `lambda_harm_ms` |
| u | điểm quyết định | u = Ī − λ·p−; luật K2: đổi ⇔ u > c | ms | `score_ms` |
| H, r | ngưỡng tĩnh | tuyệt đối: đổi ⇔ Î > H; tương đối: đổi ⇔ Î/Ĉ_cur > r (K22) | ms, — | `h_fixed_ms`, `r_rel` |

## Phần 3 — Estimand

Mọi tỉ lệ ở tầng decision-level chia cho MỌI epoch được đánh giá, trừ khi tên nói khác. Tầng decision-level và
trajectory-level: xem K16 (L0.5).

| Tên (= tên cột) | Estimand | Tầng | Đơn vị | Vai trò |
|---|---|---|---|---|
| `gain_ms` | E[a·(I_D − c)] trên mọi epoch | decision | ms | **chính (mục tiêu K2)** |
| `headroom_ms` | E[(I_D − c)⁺]: gain của người biết trước I_D; cận trên của mọi luật | decision | ms | chuẩn hoá, quy tắc SESOI |
| `harmful_switch_rate` | P(đổi ∧ I_D < −ε) | decision | tỉ lệ | **chính (ràng buộc ≤ α)** |
| `gap_fixed_oracle_ms` | gain(oracle) − gain(tốt nhất của họ tĩnh K22, tune từng ô), cùng α, cùng tập quyết định | decision | ms | **RQ1 chính** |
| `gap_rel_headroom` | gap_fixed_oracle_ms / headroom_ms | decision | — | RQ1, quy tắc SESOI |
| `recovery_ratio` | (gain_luật − gain_tĩnh) / (gain_oracle − gain_tĩnh); chỉ báo khi khoảng cách có ý nghĩa | decision | — | RQ2 |
| `price_of_safety_ms` | gain(oracle, α = ∞) − gain(oracle, α) | decision | ms | phụ ("giá của an toàn") |
| `lambda_harm_ms` | λ đã hiệu chỉnh | decision | ms | chẩn đoán |
| `harm_excess_shift` | harmful_switch_rate ở test − α, tham số đóng băng | decision | điểm % | tầng 3 |
| `missed_improvement_rate` | P(giữ ∧ I_D > ε) | decision | tỉ lệ | phụ (so với v14) |
| `harmful_per_switch` | P(I_D < −ε \| đổi) | decision | tỉ lệ | phụ |
| `frac_harm_possible` | P(I_D < −ε) trên tập quyết định | decision | tỉ lệ | kiểm ràng buộc có thể cắn (≥ 2α) |
| `harmful_loss_rate` | P(đổi ∧ loss_alt − loss_cur > δ) | decision | tỉ lệ | phụ (K3) |
| `rd_score`, `sd_log_s_cond`, `self_gap_twin` (+ `_twin`) | Phần 6 | decision | —, ms | H2, RQ1-op |
| `sd_log_s` | sd(log s) trên mọi epoch | decision | — | phụ |
| `switch_rate`, `flap_rate` | P(đổi); P(đổi ngược trong ≤ 3 epoch \| đổi) | trajectory | tỉ lệ | phụ; bắt buộc báo khi c = 0 |
| `delay_mean_ms`, `delay_p95_ms`, `loss_rate` | của luồng trên path nó thật sự đi | trajectory | ms, tỉ lệ | phụ |
| `n_epochs`, `n_nan_epochs` | số epoch đánh giá; số epoch nhãn không xác định | cả hai | epoch | bắt buộc báo |

Estimator mặc định: tính trong mỗi run → trung bình qua seed → CI t (paired theo seed khi so hai luật).
**Quy tắc SESOI:** khoảng cách có ý nghĩa ⇔ gap_fixed_oracle_ms ≥ m VÀ gap_rel_headroom ≥ r (m, r khoá ngày 13/10, trước F2).

## Phần 4 — Quy ước

1. **Mẫu số:** mọi epoch được đánh giá (K2). Đổi K2 thì sửa ở đây trước khi sửa code.
2. **Vùng chết:** |I_D| ≤ ε thì không harmful, không missed.
3. **Hoà:** giá trị đúng bằng ngưỡng thì GIỮ.
4. **Epoch không xác định:** hệ thống đầy suốt khoảng giữ (DES) hoặc mất toàn bộ probe (Mininet) → D = NaN, epoch loại khỏi
   estimand delay (cả tử và mẫu), vẫn tính cho loss; báo `n_nan_epochs`.
5. **Warm-up:** bỏ epoch trong thời gian burn-in hàng đợi và epoch chưa có cửa sổ telemetry đầu tiên; báo `n_epochs`.
6. **Đơn vị:** phân tích theo epoch; lặp độc lập theo seed (không coi epoch là mẫu độc lập).
7. **p± ước lượng:** kẹp ở sàn 1/(M+1); luôn báo M hoặc kích thước bin.
8. **Tên:** đại lượng có đơn vị mang hậu tố `_s`, `_ms`, `_bps`; không thứ nguyên ghi rõ (`pi_noise`, `eps_over_s`).
9. **Probe là công cụ chấm điểm:** không policy nào được đọc probe (kiểm bằng test không rò rỉ ở Phase 4).
10. **Nhãn trong DES:** D và loss trên khoảng giữ tính bằng tích phân chính xác của workload V(t) (tuyến tính từng khúc):
    D = prop + S + trung bình theo thời gian của V trên phần thời gian hệ thống chưa đầy; loss = tỉ lệ thời gian hệ thống đầy.
    Theo PASTA, bằng trung bình của vô hạn probe Poisson. Estimand là delay trung bình theo thời gian; luồng CBR thật có thể
    lệch nhẹ. Probe lấy mẫu chỉ dùng cho Mininet, cần ≥ 1/δ = 1000 probe mỗi path mỗi khoảng giữ để phân giải δ.
11. **Không dùng "knee" làm biến.** Hai định nghĩa cho kết quả khác xa (K = 11: 0,76 theo "loss > 0,1%" và 0,985 theo
    "dW/dρ cực đại"). Dùng Π_knee.
12. **Nghiệm M/D/1/K** tính bằng phương trình lát cắt (chỉ cộng số dương). Không giải bằng ma trận khi loss nhỏ
    (cho loss âm ở K = 100).

## Phần 5 — Nhóm không thứ nguyên

| Tên | Định nghĩa | Tên cột |
|---|---|---|
| Π_age | z_eff / τ | `pi_age` |
| Π_knee | σ / (1 − ρ̄) | `pi_knee` |
| Π_hold | H_hold / τ | `pi_hold` |
| Π_noise | √(ρ̄·S/W) / sd_age, với sd_age = σ·√(1 − e^(−2·z_eff/τ)) (sai số dự báo tối ưu của OU) | `pi_noise` |
| Π_relax | T_relax / τ, T_relax ≈ S/(1 − √ρ̄)² (bậc độ lớn, M/M/1; kiểm lại ở L2.1) | `pi_relax` |
| ε/S | ngưỡng / thời gian phục vụ | `eps_over_s` |
| K | buffer tính theo đơn vị S ("nông" 11, "sâu" 100) | `k_sys` |

Π_noise là **chỉ số bậc độ lớn**: công thức dùng z_eff trong phương sai, trái quy tắc Phần 1; không dùng cho kết luận định lượng.

Ghi chú: MASTER_PLAN từng dùng độ trôi không dự báo σ·√(2(1 − e^(−z/τ))). Với W = 0,5 s, ρ̄ = 0,9, σ = 0,03,
τ = 10 s, z_eff = 1 s, hai cách cho Π_noise = 5,78 và 5,64 ở 4 Mb/s. File này dùng 5,78 (công thức trên).

Giá trị tham chiếu (cùng tham số):

| Tốc độ link | S | Π_noise | T_relax | Π_relax | K = 100 tương ứng |
|---|---:|---:|---:|---:|---:|
| 4 Mb/s | 3,024 ms | 5,78 | 1,15 s | 0,115 | 302 ms |
| 100 Mb/s | 0,121 ms | 1,16 | 0,046 s | 0,005 | 12,1 ms |
| 1 Gb/s | 0,012 ms | 0,37 | 0,005 s | 0,0005 | 1,2 ms |

## Phần 6 — Chỉ số cho H2 (K17, định nghĩa lại theo K2)

- **Điểm quyết định** u_e = Ī_e − λ·p−_e tại λ vận hành (λ của oracle hoặc của twin, theo bản chỉ số).
- **Tập cân nhắc** E_c = {e : Ī_e > c}: epoch mà luật K2 có thể đổi (ngoài E_c, u ≤ c với mọi λ ≥ 0).
- **`rd_score`** = 1 − Spearman(Î, u) trên E_c (hạng trung bình khi hoà; |E_c| < 3 → 0). Bằng 0 khi thứ tự theo Î trùng thứ tự
  theo u, tức ngưỡng tĩnh trên Î tối ưu.
- **`sd_log_s_cond`**: sd(log s) trong 20 bin phân vị của Î, trung bình có trọng số theo số epoch.
- **`self_gap_twin`**: twin dùng chính Ī, p− của nó để tính gain dự đoán của luật K2 trừ gain dự đoán của ngưỡng tĩnh tốt nhất,
  cùng ngân sách dự đoán (ms). Dưới M0 đúng theo cấu trúc (verification); dưới X1′, X2 mới mang thông tin.
- Bản oracle dùng Ī, p±, s của oracle; bản twin (`_twin`) dùng của twin. `sd_log_s` là biến phụ.
- Lịch sử: `rd_kappa` (v2, theo mục tiêu (b)) được thay bằng `rd_score`. Bài học của P03 giữ nguyên: tính trên tập cân nhắc;
  cẩn thận hoà điểm do kẹp p± ở sàn Monte Carlo.
- Chọn chỉ số chính giữa `rd_score`, `sd_log_s_cond`, `self_gap_twin` ở DP0 bằng seed pilot; khoá trong prereg RQ1.

## Phần 7 — Ví dụ tính tay

**VD1.** Đường hiện tại A. Trên khoảng giữ: A nhận 50/50 probe, trung bình 42,0 ms; B nhận 50/50, trung bình 35,0 ms.
ε = 2 ms. Twin dự đoán Î = 3 ms; ngưỡng tĩnh H = 5 ms.
→ I_D = 7 ms > ε. Ngưỡng tĩnh: Î = 3 < H → giữ → **missed**. Một ngưỡng "an toàn" có thể bỏ lỡ cải thiện lớn.

**VD2.** Đường hiện tại A; D_A = 20,4 ms, D_B = 21,1 ms; policy đã đổi. Với ε = 0,5 ms và ε = 1 ms, lần đổi có gây hại?
→ I_D = −0,7 ms. ε = 0,5: −0,7 < −0,5 → **harmful**. ε = 1: vùng chết → không harmful, không missed. Nhãn phụ thuộc ε,
nên phải báo trên cả lưới ε.

**VD3.** Đường hiện tại A; policy đã đổi. A nhận 95/100 probe, trung bình 30 ms; B nhận 80/100, trung bình 20 ms.
ε = 2 ms, δ = 10⁻³.
→ I_D = +10 ms (tốt về delay). loss_A = 0,05; loss_B = 0,20; I_L = −0,15 < −δ → **harmful về loss**. B trông tốt về
delay một phần vì 20% probe bị drop (thường là những gói lẽ ra chờ lâu nhất) không được tính: survivorship.

**VD4.** Một run 1000 epoch, c = 0. Policy đổi 120 lần, tổng I_D trên các lần đổi là 240 ms; 9 lần có I_D < −ε.
→ `gain_ms` = 240/1000 = 0,24 ms; `harmful_switch_rate` = 0,9% (≤ α = 1% ✓); `harmful_per_switch` = 7,5%.
Nếu `headroom_ms` = 0,80 ms thì luật này đạt 30% headroom.

**VD5.** W = 0,5 s, T_poll = 0,5 s, d = 0,1 s, a = 0,05 s, H_hold = 0,5 s; quyết định không đồng bộ với telemetry.
→ t − t_m ∈ [0,1; 0,6) → z ∈ [0,35; 0,85) s → z_eff ∈ [0,65; 1,15) s, trung bình 0,9 s. Jitter tuổi rộng đúng
T_poll = 0,5 s. Nếu quyết định ngay khi telemetry tới: z = d + W/2 = 0,35 s cố định, không có jitter.

**VD6.** Cùng tham số Phần 5: Π_noise = 5,78 ở 4 Mb/s và 1,16 ở 100 Mb/s. K = 100 gói tương ứng 302 ms ở 4 Mb/s nhưng
12,1 ms ở 100 Mb/s. "Buffer sâu" phải nói theo đơn vị S (hoặc thời gian), không theo số gói trần.

**VD7.** Ba quyết định (ε ≈ 0; odds = Φ(Î/s)/Φ(−Î/s)): A (Î 1, s 1) → odds 5,3; B (Î 4, s 2) → 43,0; C (Î 8, s 16) → 2,2.
Hạng theo Î: A 1, B 2, C 3. Hạng theo odds: C 1, A 2, B 3. Hiệu hạng d = (−1; −1; 2), Σd² = 6.
Spearman = 1 − 6·Σd² / (n(n² − 1)) = 1 − 36/24 = −0,5 → rd = 1,5. Chỉ với {A, B}: Spearman = 1 → rd = 0.
C có Î lớn nhất nhưng bất định lớn hơn hẳn, nên đảo thứ tự. Đó là loại heterogeneity làm ngưỡng tĩnh thua.

**VD8 (vì sao K2 dùng ms).** P và Q cùng p+ = 0,9, p− ≈ 0; E[I_D | F] của P là 0,7 ms, của Q là 30 ms. Mục tiêu (b) phạt bỏ lỡ
P và bỏ lỡ Q như nhau (mỗi cái 1 missed); mục tiêu K2 phân biệt 0,7 ms và 30 ms, đúng thứ người dùng VoIP cảm nhận.
