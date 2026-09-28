# T4 — Thông tin làm đổi thứ tự (§1–2)

> Ngày 2026-09-29 (P1v2/L1.3). Provenance: Claude (AI) soạn chứng minh, ví dụ và `t03c`; tác giả chạy lại, kiểm và
> chịu trách nhiệm. Kiểm lý thuyết trên toy, không đổi phán quyết F6. §3 (luật bậc hai) thêm ở L1.4.
> Ký hiệu theo definitions v2.1: Ī = E[I_D | F], p− = P(I_D < −ε | F), u = Ī − λ·p−; c = 0 trong mọi ví dụ.

## 1. Khi nào ngưỡng tĩnh đã tune là tối ưu

**Luật là một tập.** Luật = tập epoch được đổi. Họ tĩnh trên thống kê T = các tập mức trên {T > t}. K2 = A* = {u > c},
λ* nhỏ nhất đạt harm ≤ α. Tương đương cái túi phân số (T3 §4): K2 xếp theo Ī/p− (ms trên mỗi đơn vị harm), luật tĩnh
xếp theo T; cả hai lấy từ trên xuống tới khi hết ngân sách. gain(A) − gain(B) chỉ phụ thuộc các epoch hai luật bất đồng.

**Mệnh đề 1 (đủ).** Nếu A* = {T > t*} (trừ tập xác suất 0) thì ngưỡng tốt nhất trên T đạt gain của K2.
Chứng minh: A* thuộc họ tĩnh và khả thi ⇒ tốt nhất của họ ≥ gain(A*); K2 tối ưu trong mọi luật khả thi (T3 §3)
⇒ gain(A*) ≥ tốt nhất của họ. ∎ Điều kiện đủ thường dùng: u tăng ngặt theo T. Không đòi s hằng hay bất định đồng đều.

**Mệnh đề 1′ (cần, khi P(u = c) = 0).** Đẳng thức trong chuỗi T3 §3 buộc mọi luật tối ưu trùng A* hầu khắp nơi. Vậy
gap = 0 ⇔ A* là tập mức trên của T ⇔ dọc T, dấu của u − c đổi đúng một lần (cắt biên đơn, single crossing).
Thứ tự theo u KHÔNG cần trùng thứ tự theo T ở mọi nơi: đảo thứ tự xa biên không tốn gì (H2).

**Mệnh đề 2.** gap > 0 ⇔ có (xác suất dương) cặp cắt ngang: e được K2 đổi, e′ bị K2 giữ, T(e′) ≥ T(e). Hai đường:
(i) thông tin ngoài T — (a) Z ∈ F: mức tải chung dọc đường mức của Î, tuổi A1; (b) Z ∉ F: hàng đợi V, lịch sử, tuổi
riêng từng path (F7). (ii) u không đơn điệu theo chính T: du/dĪ = 1 − λ·dp−/dĪ < 0, cần độ co giãn
e_s = (ε + Ī)·s′/s > 1 và λ đủ lớn. Thế giới D (s = 0,3 + 0,25Ī²): thuần 0,429 ms = 37% headroom, κ ở mức sàn.
Giả thuyết mạng (chưa kiểm): gần knee, T′ ≈ 2(T − S)²/(ρ²S) nên s có thể ∝ Î².

**Hệ quả.** 1.1 Ī = h(Î), h tăng ngặt ⇒ {Î > t} = {Ī > h(t)}: cùng một họ, sửa tâm đơn điệu vô ích với luật đã tune
(áp cho ngưỡng tốt nhất S_Î* tune cùng quy trình với SC, không trực tiếp cho S0 tune theo J). 1.2 Họ tịnh tiến
⇒ p− = G(−ε − Î) giảm ⇒ u tăng (H1 là trường hợp riêng). 1.3 Thế giới B, Ī > 0: (ε + Ī)/s có đạo hàm
0,05/(0,3 + 0,5Ī)² > 0 ⇒ p− giảm, u tăng; Ī ≤ 0 ⇒ u ≤ 0. s tăng ~10 lần mà gap = 0 chính xác. Tổng quát
s = a + bĪ: p− giảm ⇔ a > bε. 1.4 λ* = 0 ⇒ K2 ≡ SC, phần thuần bằng 0 theo cấu trúc (7/16 ô F2).

**Ví dụ tay** (ngân sách Σp− ≤ 0,25; Î = Ī; `t03c` phần 1; khớp duyệt 64 tập con):

| Bộ | p− của e1…e6 (Î = 6…1) | Tĩnh | K2 (λ*) | gap | Spearman(Î,u) |
|---|---|---|---|---|---|
| H1 đơn điệu | .02 .04 .06 .10 .15 .25 | e1–e4: 18 | e1–e4: 18 (13,33) | 0 | 1,000 |
| H2 đảo xa biên | .08 .02 .06 .10 .15 .25 | e1–e3: 15 | e1–e3: 15 (30) | 0 | 0,943 |
| H3 cắt ngang | .02 .04 .20 .10 .03 .25 | e1–e2: 11 | e1,e2,e4,e5: 16 (20) | 5 | 0,771 |

## 2. Tâm, độ rộng, hình học, thước đo

**Hai kênh.** K2 − S_Î = (SC − S_Î) tâm + (K2 − SC) thuần; Mệnh đề 1–2 áp từng bậc với T = Î rồi T = Ī.

| `t03c` phần 2 | tâm | thuần | κ_Î | κ_Ī | κ_Ī detrend | rd | K2≠SC |
|---|---:|---:|---:|---:|---:|---:|---:|
| A độ rộng trực giao | 0 | 0,0952 | 0,699 | 0,699 | 0,699 | 0,078 | 12,8% |
| B cùng hướng | 0 | 0 | 0,068 | 0,068 | 0,003 | 0 | 0% |
| D u không đơn điệu | 0 | 0,4293 | 0,097 | 0,097 | 0,005 | 1,085 | 51,3% |
| E tâm trực giao | 0,1008 | 0 | 0,358 | 0,070 | 0,004 | 0,176 | 0% |
| F cả hai | 0,1290 | 0,0891 | 0,701 | 0,701 | 0,701 | 0,228 | 12,0% |

**Bài học đo lường.** (1) rd_score mù vị trí (A: 0,078 mà thuần > 0). (2) κ bin theo Î lẫn tâm vào độ rộng (E); phần
thuần cần κ theo Ī — đúng thiết lập L1.4. (3) Sàn bin ≈ |d log s₀/dĪ|·(độ rộng bin)/√12: B cho 0,132/0,068/0,028/0,014
ở 10/20/50/100 bin, detrend ≤ 0,010; median F2 là 0,099, cùng bậc với sàn. Sàn lấy mẫu ≈ 1/√(2(n − 1)) (n = 30: 0,13).
(4) κ mù đường (ii). Thước đo trực tiếp: gap và tỉ lệ K2 ≠ luật tĩnh tốt nhất trên cùng T.

**Hình học.** Mặt phẳng (ρ̂_cur, ρ̂_alt): họ abs = đường mức T(x) − T(y) = H; họ rel = T(y) = (1 − r)T(x). Dọc đường
mức Î = 5 ms (K = 100): (0,85; 0,70) có Î/s_thô ≈ 1,0 và tỉ số rel 0,43; (0,95; 0,94) có Î/s_thô ≈ 0,09 và rel 0,16
(s_thô: chỉ nhiễu đếm, bỏ shrink). Mức tải chung là Z loại (a) nằm trong F. Họ rel tự đòi nhiều hơn ở tải cao: hiệu
chỉnh bất định thô có sẵn trong thực hành (F2: 13/16 ô chọn rel). Suy luận, chưa kiểm.

**Toán cổ điển (không claim).** Mệnh đề 1 = T đủ cho quyết định tại λ*; cùng tinh thần Karlin–Rubin (MLR ⇒ kiểm định
ngưỡng tối ưu) và single crossing. Blackwell: nếu Y là bản làm nhiễu của X thì oracle trên X không tệ hơn (tổng thể);
F và Q không so được theo Blackwell. Nguồn cần tự kiểm ở L1.10.

**Bốn con số.** K2 ≠ SC 0,00–0,98% (f05b): kênh độ rộng gần cắt biên đơn theo Ī (toy A: 12,8%); 0,00% một phần do
độ phân giải oracle. SC − S0 P2/A0 +0,048 ± 0,370 ms: không phát hiện đổi thứ tự tâm ở độ chính xác này. P2/A1
+0,558 ± 0,323 ms: dấu hiệu tâm trong cùng F (một trong ~68 CI, bằng chứng yếu). A1: e^(−z_eff/τ) 0,890–0,935
(τ = 10 s), 0,557–0,715 (τ = 2 s); thuần FZ −0,122…+0,154 ms. Q: 4,125 = tâm 4,107 + thuần 0,018 ms.

**Đề xuất trước L1.6 (chưa hiệu lực, cần GVHD):** κ̂_pure = sd(log s | Ī), 20 bin, detrend tuyến tính trong bin, kèm
đối chứng sàn; `sd_log_s_cond` (theo Î) làm phụ; t07 dùng cùng ước lượng; báo dấu a′ trên toàn E_c; báo S_Î* để tách
tâm sạch (SC − S_Î*) khỏi quy trình tune (S_Î* − S0).
