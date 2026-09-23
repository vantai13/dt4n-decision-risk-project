# Definitions — v1 draft (2026-09-23)

Nguồn sự thật DUY NHẤT cho ký hiệu, đơn vị, estimand. Code, `summary.json` và
§III paper phải dùng đúng các tên ở đây. Thêm/đổi định nghĩa: ghi decision log
TRƯỚC.

> Trạng thái: bản nháp Lesson 0.3, chưa khóa. Các mục `[BẠN CHỌN]` và lời giải
> VD2–VD6 phải do tác giả nghiên cứu tự điền trước khi commit.

## 1. Ký hiệu

| Ký hiệu | Tên | Định nghĩa | Đơn vị | Tên trong code |
|---|---|---|---|---|
| Δt | bước mô phỏng | — | s | `dt_s` |
| T_dec | chu kỳ quyết định | controller ra 1 quyết định/OD mỗi T_dec | s | `dt_decision_s` |
| l, k, K | link, path ứng viên, số path | P[k,l]=1 nếu path k dùng link l | — | `link`, `path`, `k_paths` |
| ρ_l(t) | utilization link l | tải / capacity | — | `rho` |
| τ | thời gian tương quan của tải (thế giới synthetic) | r(z)=e^(−z/τ) cho OU | s | `tau_s` |
| u(t), z(t) | thời điểm sinh telemetry mới nhất twin có; tuổi | z = t − u | s | `age_s` |
| z/τ | tuổi không thứ nguyên | — | — | `age_over_tau` |
| C_k(t) | chi phí THẬT của path k tại t | f(ρ(t)), delay model của sự thật | ms | `cost_true_ms` |
| Ĉ_k(t) | chi phí TWIN của path k tại t | f̂(ρ(u(t))) với last-value hold (D6) | ms | `cost_twin_ms` |
| e_k(t) | sai số twin | C_k − Ĉ_k (THẬT trừ TWIN) | ms | `err_ms` |
| â, â₂ | path tốt nhất, thứ hai theo twin | argsort ổn định của Ĉ, tie → index nhỏ | — | `a_twin`, `a_twin2` |
| a* | path tốt nhất thật | argmin C, tie → index nhỏ | — | `a_true` |
| m̂ | margin twin | Ĉ_â₂ − Ĉ_â ≥ 0 | ms | `margin_twin_ms` |
| m | margin thật GIỮA CẶP TOP-2 CỦA TWIN | C_â₂ − C_â (có thể âm) | ms | `margin_true_ms` |
| s_pair | score cặp | \|m − m̂\| | ms | `score_pair_ms` |
| s_all | score mọi path | max_a \|e_a − e_â\| (K ≥ 3 BẮT BUỘC dùng cái này) | ms | `score_all_ms` |
| D_ij(t) | hiệu chi phí cặp có thứ tự | C_j − C_i | ms | `diff_ms` |
| W | cửa sổ lịch sử để ước lượng tham số | [BẠN CHỌN: giá trị và lý do] | s | `hist_window_s` |
| μ̂, σ̂, r̂(z) | tham số ước lượng của D_{â,â₂} từ lịch sử twin | ước lượng theo cặp có thứ tự | ms, ms, — | `mu_hat_ms`, `sigma_hat_ms`, `r_hat` |
| m̃_exact, p̂_exact | normalized margin và xác suất đảo cặp theo luật | c/v, Φ(−c/v) | — | `margin_norm`, `p_flip_pred` |
| m̃_naive, p̂_naive | bản bỏ hồi quy về trung bình (ablation) | m̂/ŝ(z), Φ(−m̃_naive) | — | `margin_norm_naive`, `p_flip_pred_naive` |
| q̂(z) | ngưỡng conformal theo bin tuổi | — | ms | `qhat_ms` |
| α | mức lỗi mục tiêu của gate | — | — | `alpha` |
| ε | ngưỡng regret coi là “có hại” | [BẠN CHỌN: giá trị và cách neo] | ms | `eps_ms` |

Với cặp có thứ tự `(i, j)`:

```text
D_ij(t) = C_j(t) − C_i(t)
c = μ̂_ij + r̂_ij(z)·(m̂ − μ̂_ij)
v = σ̂_ij·sqrt(1 − r̂_ij(z)^2)
m̃_exact = c/v
p̂_exact = Φ(−m̃_exact)
```

Các tham số được ước lượng từ lịch sử telemetry của twin trong cửa sổ W,
không dùng ground truth. `r̂_ij(z)` được ước lượng trực tiếp tại độ trễ z.

## 2. Estimand

Estimator mặc định: tính trong từng run trên các quyết định hợp lệ (§3), lấy
trung bình qua S seed và CI 95% theo t, ngoại trừ khi được ghi khác bên dưới.

| Tên | Estimand | Đơn vị | Vai trò |
|---|---|---|---|
| `harmful_error_rate@eps` | P(C_â − C_a* > ε), báo cáo tại nhiều ε | tỉ lệ | CHÍNH |
| `regret_mean_ms` | E[C_â − C_a*] | ms | CHÍNH |
| `regret_p95_ms` | phân vị 95% của regret | ms | phụ (đuôi) |
| `decision_error_rate` | P(â ≠ a*) (= harmful tại ε=0 khi không tie) | tỉ lệ | phụ |
| `pair_flip_rate` | P(m < 0) | tỉ lệ | RQ1a — thứ luật dự đoán |
| `contender_rate` | P(a* ∈ {â, â₂}) (=1 khi K=2) | tỉ lệ | RQ1b, đo bẫy K ≥ 3 |
| `coverage` | P(ACCEPT) | tỉ lệ | RQ2 |
| `selective_pair_flip_rate` | P(m < 0 \| ACCEPT) | tỉ lệ | RQ2 |
| `selective_harmful_rate@eps` | P(regret > ε \| ACCEPT) | tỉ lệ | RQ2 |
| `selective_risk_pred` | E[p̂ \| ACCEPT] | tỉ lệ | RQ1a/RQ2 |
| `selective_risk_ratio` | selective_pair_flip_rate / selective_risk_pred | — | calibration chính [BẠN CHỌN: hoặc cách 2] |
| `ece_logbins` | ECE của p̂ với biên bin [1e-4, 1e-3, 1e-2, 1e-1, 1] | tỉ lệ | calibration phụ |
| `auroc` | AUROC của p̂ với nhãn pair_flip | — | discrimination |
| `e2e_cost_ms` | E[chi phí action được thực thi]: â nếu ACCEPT, fallback nếu ABSTAIN | ms | RQ2; định nghĩa riêng theo fallback ở L5.1 |
| `tie_rate` | tỉ lệ quyết định có tie (twin hoặc thật) | tỉ lệ | vệ sinh |
| `n_decisions`, `n_accept` | số quyết định hợp lệ, số ACCEPT | đếm | vệ sinh |

Tỉ lệ có điều kiện (`selective_*`):
`[BẠN CHỌN: mean of per-run ratios / pooled ratio + bootstrap theo run]`.
Luôn báo cáo số run có `n_accept = 0`.

## 3. Quy ước

- Đơn vị phân tích: 1 quyết định = (1 OD, 1 thời điểm quyết định).
- Đơn vị lặp độc lập: 1 run (seed).
- Chu kỳ quyết định: `T_dec = [BẠN CHỌN]`, với lý do ghi trong decision log.
- Quyết định hợp lệ: K ≥ 2, t − z ≥ 0, đủ W giây lịch sử twin. Báo cáo `n_decisions`.
- OU khởi tạo từ phân phối dừng `[BẠN XÁC NHẬN: hoặc chọn burn-in]`.
- Tie-break: index nhỏ nhất, cho cả twin và thật. Báo cáo `tie_rate`.
- Dấu: e = thật − twin; m̂ ≥ 0; m < 0 nghĩa là cặp bị đảo.
- Chi phí đánh giá tại thời điểm quyết định t; hợp lệ khi T_dec ≪ τ.
- Luật normalized margin được đánh giá trên `pair_flip_rate`, KHÔNG trên `decision_error_rate`.
- K ≥ 3: gate dùng `s_all`; báo cáo `contender_rate`.
- Nhiều OD: trung bình đều trên các OD có ≥ 2 path; kèm phân bố theo OD.
- Mọi tên có đơn vị mang hậu tố `_s`, `_ms`; không thứ nguyên ghi rõ.

## 4. Ví dụ tính tay

Làm VD2–VD6 trước khi đọc đáp án trong tài liệu lesson. Ghi cả phép tính và chỗ
sai ban đầu; không chỉ chép kết quả cuối.

### VD1 — đã giải

Twin: A=10,0; B=10,2. Thật: A=10,3; B=10,1.

â=A, â₂=B, m̂=0,2; a*=B; decision error=1; regret=0,2 ms;
m=−0,2; s_pair=0,4.

### VD2

Twin: A=10; B=50. Thật: A=13; B=48. Tính decision error, regret, m̂, m,
s_pair, sai số state từng path. So sai số state với VD1.

**Lời giải của tôi:**

### VD3

Twin: A=10,00; B=10,02. Thật: A=10,03; B=10,01. ε=0,5 ms: có harmful không?

**Lời giải của tôi:**

### VD4

Twin: A=10; B=12; q̂=1,5. C1: ACCEPT hay ABSTAIN? Thật A=11; B=11,4:
đúng hay sai? s_pair có ≤ q̂ không? Điều đó nói gì về quan hệ “score vượt q̂”
và “quyết định sai”?

**Lời giải của tôi:**

### VD5 — K=3

Twin: A=10; B=11; C=13. Thật: A=12; B=12,5; C=11. q̂=0,8. Tính m̂, m,
s_pair, s_all, contender, decision error, regret. C1 dùng s_pair và C1 dùng
s_all cho kết luận gì?

**Lời giải của tôi:**

### VD6 — C1 vs C2

Twin: A=10; B=10,6; q̂=1,0; ε=0,5. C1 và C2 quyết định gì? Nếu thật A=10,8;
B=10,4: kiểm s_pair ≤ q̂, decision error, regret, harmful.

**Lời giải của tôi:**

## 5. Các lựa chọn cần khóa trước khi commit

- W = …; lý do: …
- T_dec = …; lý do: …
- ε ∈ {…}; cách neo và lý do: …
- Estimator cho tỉ lệ có điều kiện = …; lý do: …
- Metric calibration chính = …; lý do: …
- Khởi tạo dừng hay burn-in = …; lý do: …
