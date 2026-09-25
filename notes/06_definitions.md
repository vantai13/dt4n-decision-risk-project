# Definitions — v2 (2026-09-25)

> Nguồn sự thật duy nhất cho ký hiệu, đơn vị và estimand của hướng switch-or-stay. Bản nháp do Claude (AI) soạn
> theo yêu cầu tác giả (L0.4); tác giả kiểm từng mục. Docstring trong `ndtrisk/`, cột trong `summary.json` và §III
> báo cáo phải dùng đúng các định nghĩa ở đây. **Sửa file này TRƯỚC khi sửa code.**
> Bản v1 (top-2 margin): `notes/archive/v1_trust_gate/06_definitions.md`.
> Quyết định liên quan: K2, K3, K6, K7, K17, K21, K22 (`02_decision_log.md`).

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
| ε, δ | ngưỡng "đáng kể" | delay; loss (K3: δ = 0,01) | ms, — | `eps_ms`, `delta_loss` |
| α | ngân sách harm | trên MỌI epoch (K2) | — | `alpha` |
| κ | giá mỗi lần đổi | đơn vị: "sự kiện missed" trên một lần đổi (K21: 0,01) | — | `kappa` |
| λ | giá của harm | nhân tử Lagrange; λ ≥ 0 nhỏ nhất đạt harm ≤ α (K2) | — | `lambda_harm` |
| H, r | ngưỡng tĩnh | tuyệt đối: đổi ⇔ Î > H; tương đối: đổi ⇔ Î/Ĉ_cur > r (K22) | ms, — | `h_fixed_ms`, `r_rel` |
| η | ngưỡng odds (dạng cũ) | chỉ dùng khi κ = 0: đổi ⇔ p+/p− > η, η = λ | — | `eta` |

## Phần 3 — Estimand

Mọi tỉ lệ ở tầng decision-level chia cho MỌI epoch được đánh giá, trừ khi tên nói khác. Tầng decision-level và
trajectory-level: xem K16 (L0.5).

| Tên (= tên cột) | Estimand | Tầng | Đơn vị | Vai trò |
|---|---|---|---|---|
| `harmful_switch_rate` | P(đổi ∧ I_D < −ε) | decision | tỉ lệ | **chính** (ràng buộc ≤ α) |
| `missed_improvement_rate` | P(giữ ∧ I_D > ε) | decision | tỉ lệ | **chính** |
| `switch_rate` | P(đổi) | decision | tỉ lệ | chính (trong J) |
| `objective_j` | missed_improvement_rate + κ·switch_rate | decision | tỉ lệ | **tiêu chí K2** |
| `gap_fixed_oracle` | J(tốt nhất của họ tĩnh K22, tune từng ô) − J(oracle), cùng α, cùng tập quyết định | decision | điểm % | **RQ1 chính** |
| `gap_missed` | như trên nhưng chỉ missed | decision | điểm % | phụ (so với thuyết minh) |
| `recovery_ratio` | (J_tĩnh − J_luật) / (J_tĩnh − J_oracle); chỉ báo khi gap ≥ SESOI_claim | decision | — | RQ2 |
| `harm_excess_shift` | harmful_switch_rate ở test − α, λ đóng băng từ calibration | decision | điểm % | **RQ2** (tiêu chí thất bại chính) |
| `harmful_per_switch` | P(I_D < −ε \| đổi) | decision | tỉ lệ | phụ (so với v1, LEC) |
| `frac_harm_possible` | P(I_D < −ε) trên tập quyết định | decision | tỉ lệ | kiểm ràng buộc có thể cắn (≥ 2α) |
| `lambda_harm` | λ đã hiệu chỉnh | decision | — | chẩn đoán (giá của harm) |
| `rd_kappa`, `rd_kappa_twin` | Phần 6 | decision | — | H2 (ứng viên chính) |
| `sd_log_s_cond`, `sd_log_s_cond_twin` | Phần 6 | decision | — | H2 (ứng viên chính) |
| `sd_log_s` | sd(log s) trên mọi epoch | decision | — | phụ |
| `harmful_loss_rate` | P(đổi ∧ I_L < −δ) | decision | tỉ lệ | phụ (K3) |
| `flap_rate` | P(đổi ngược trong ≤ 3 epoch \| đổi) | trajectory | tỉ lệ | phụ |
| `delay_mean_ms`, `delay_p95_ms` | delay probe nhận được trên path luồng thật sự đi | trajectory | ms | phụ |
| `loss_rate` | tỉ lệ probe mất trên path luồng thật sự đi | trajectory | tỉ lệ | phụ |
| `n_epochs`, `n_nan_epochs` | số epoch đánh giá; số epoch có path mất toàn bộ probe | cả hai | epoch | bắt buộc báo |

Estimator mặc định: tính estimand trong mỗi run → trung bình qua seed → CI t (paired theo seed khi so hai luật).

## Phần 4 — Quy ước

1. **Mẫu số:** mọi epoch được đánh giá (K2). Đổi K2 thì sửa ở đây trước khi sửa code.
2. **Vùng chết:** |I_D| ≤ ε thì không harmful, không missed.
3. **Hoà:** giá trị đúng bằng ngưỡng thì GIỮ.
4. **Epoch không xác định:** path mất toàn bộ probe → D = NaN, epoch loại khỏi estimand delay (cả tử và mẫu),
   vẫn tính cho estimand loss; báo `n_nan_epochs`. Ở decision-level, mọi luật cùng tập epoch nên loại trừ công bằng.
5. **Warm-up:** bỏ epoch trong thời gian burn-in hàng đợi và epoch chưa có cửa sổ telemetry đầu tiên; báo `n_epochs`.
6. **Đơn vị:** phân tích theo epoch; lặp độc lập theo seed (không coi epoch là mẫu độc lập).
7. **p± ước lượng:** kẹp ở sàn 1/(M+1); luôn báo M hoặc kích thước bin.
8. **Tên:** đại lượng có đơn vị mang hậu tố `_s`, `_ms`, `_bps`; không thứ nguyên ghi rõ (`pi_noise`, `eps_over_s`).
9. **Probe là công cụ chấm điểm:** không policy nào được đọc probe (kiểm bằng test không rò rỉ ở Phase 4).

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

Ghi chú: MASTER_PLAN từng dùng độ trôi không dự báo σ·√(2(1 − e^(−z/τ))). Với W = 0,5 s, ρ̄ = 0,9, σ = 0,03,
τ = 10 s, z_eff = 1 s, hai cách cho Π_noise = 5,78 và 5,64 ở 4 Mb/s. File này dùng 5,78 (công thức trên).

Giá trị tham chiếu (cùng tham số):

| Tốc độ link | S | Π_noise | T_relax | Π_relax | K = 100 tương ứng |
|---|---:|---:|---:|---:|---:|
| 4 Mb/s | 3,024 ms | 5,78 | 1,15 s | 0,115 | 302 ms |
| 100 Mb/s | 0,121 ms | 1,16 | 0,046 s | 0,005 | 12,1 ms |
| 1 Gb/s | 0,012 ms | 0,37 | 0,005 s | 0,0005 | 1,2 ms |

## Phần 6 — Chỉ số cho H2 (K17)

Tính trong MỘT ô cấu hình, trên các epoch e = 1…N của một run, rồi trung bình qua seed.

- **Tập cân nhắc** E_κ = {e : p+_e > κ}: epoch mà luật K2 có thể đổi. Ngoài E_κ, không luật K2 nào đổi.
- **log-odds** = log(max(p+, 1/(M+1))) − log(max(p−, 1/(M+1))).
- **`rd_kappa`** = 1 − Spearman(Î, log-odds) trên E_κ (hạng trung bình khi hoà). Bằng 0 khi thứ tự theo Î trùng thứ
  tự theo odds; nếu |E_κ| < 3 thì đặt 0.
- **`sd_log_s_cond`** = trung bình có trọng số (theo số epoch) của sd(log s) trong 20 bin phân vị của Î.
- **`sd_log_s`** = sd(log s) trên mọi epoch (phụ).
- **Bản oracle** dùng p±, s của oracle (phân tích H2a). **Bản twin** (`_twin`) dùng p±, s do twin tính; người vận hành
  tính được, không cần oracle (RQ1-op, H2c).
- **Không dùng** `rd_all` (Spearman trên mọi epoch). P03, thế giới C: rd_all = 0,195 dù khoảng cách = 0, vì kẹp p± ở
  sàn Monte Carlo tạo hoà hàng loạt.
- Bằng chứng: `experiments/pilot/p03_h2_indices.py` (exploratory). Chọn chỉ số chính giữa `rd_kappa` và
  `sd_log_s_cond` ở DP0 bằng seed pilot; khoá trong prereg RQ1.

## Phần 7 — Ví dụ tính tay

**VD1.** Đường hiện tại A. Trên khoảng giữ: A nhận 50/50 probe, trung bình 42,0 ms; B nhận 50/50, trung bình 35,0 ms.
ε = 2 ms. Twin dự đoán Î = 3 ms; ngưỡng tĩnh H = 5 ms.
→ I_D = 7 ms > ε. Ngưỡng tĩnh: Î = 3 < H → giữ → **missed**. Một ngưỡng "an toàn" có thể bỏ lỡ cải thiện lớn.

**VD2.** Đường hiện tại A; D_A = 20,4 ms, D_B = 21,1 ms; policy đã đổi. Với ε = 0,5 ms và ε = 1 ms, lần đổi có gây hại?
→ I_D = −0,7 ms. ε = 0,5: −0,7 < −0,5 → **harmful**. ε = 1: vùng chết → không harmful, không missed. Nhãn phụ thuộc ε,
nên phải báo trên cả lưới ε.

**VD3.** Đường hiện tại A; policy đã đổi. A nhận 95/100 probe, trung bình 30 ms; B nhận 80/100, trung bình 20 ms.
ε = 2 ms, δ = 0,01.
→ I_D = +10 ms (tốt về delay). loss_A = 0,05; loss_B = 0,20; I_L = −0,15 < −δ → **harmful về loss**. B trông tốt về
delay một phần vì 20% probe bị drop (thường là những gói lẽ ra chờ lâu nhất) không được tính: survivorship.

**VD4.** Một run 1000 epoch. Policy đổi 120 lần, 9 lần harmful; 60 epoch giữ trong khi I_D > ε; κ = 0,01.
→ `harmful_switch_rate` = 0,9% (≤ α = 1% ✓); `harmful_per_switch` = 7,5% (✗ nếu hiểu α theo precision);
`missed_improvement_rate` = 6,0%; `switch_rate` = 12%; `objective_j` = 6,0% + 0,01 × 12% = 6,12%.

**VD5.** W = 0,5 s, T_poll = 0,5 s, d = 0,1 s, a = 0,05 s, H_hold = 0,5 s; quyết định không đồng bộ với telemetry.
→ t − t_m ∈ [0,1; 0,6) → z ∈ [0,35; 0,85) s → z_eff ∈ [0,65; 1,15) s, trung bình 0,9 s. Jitter tuổi rộng đúng
T_poll = 0,5 s. Nếu quyết định ngay khi telemetry tới: z = d + W/2 = 0,35 s cố định, không có jitter.

**VD6.** Cùng tham số Phần 5: Π_noise = 5,78 ở 4 Mb/s và 1,16 ở 100 Mb/s. K = 100 gói tương ứng 302 ms ở 4 Mb/s nhưng
12,1 ms ở 100 Mb/s. "Buffer sâu" phải nói theo đơn vị S (hoặc thời gian), không theo số gói trần.

**VD7.** Ba quyết định (ε ≈ 0; odds = Φ(Î/s)/Φ(−Î/s)): A (Î 1, s 1) → odds 5,3; B (Î 4, s 2) → 43,0; C (Î 8, s 16) → 2,2.
Hạng theo Î: A 1, B 2, C 3. Hạng theo odds: C 1, A 2, B 3. Hiệu hạng d = (−1; −1; 2), Σd² = 6.
Spearman = 1 − 6·Σd² / (n(n² − 1)) = 1 − 36/24 = −0,5 → rd = 1,5. Chỉ với {A, B}: Spearman = 1 → rd = 0.
C có Î lớn nhất nhưng bất định lớn hơn hẳn, nên đảo thứ tự. Đó là loại heterogeneity làm ngưỡng tĩnh thua.
