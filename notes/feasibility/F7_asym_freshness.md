# F7 — Path bất đối xứng về rủi ro (F7b); độ tươi bất đối xứng (F7a) chuyển Phase 2

> Tên file giữ nguyên vì lịch sử commit. §1 soạn ở L1.6; §2 chốt và khoá ở L1.7; §3–4 ở L1.8.

## §1 Hiệu chỉnh từ dữ liệu cũ (POST HOC)

> KHÁM PHÁ trên seed cũ của f05, định nghĩa D1–D11 khoá trong log trước khi tính (AI ghi 01:14Z, trước khi chạy).
> Không đổi F6. Provenance: Claude (AI) soạn `f05c` và diễn giải; tác giả chạy lại, kiểm. Mọi phân tích đã thử đều ở
> `experiments/results/f05c_kappa_des_output.txt` (không có phân tích bị bỏ).

- **Đối chứng:** tái lập chính xác f05 F20x2 (thuần, λ, H) ở P2 và K100/0,95/0,03/10, A0 và A1; thế giới A0 = f04b.
- **κ thật:** κ̂_pure = P1 0,036; P2 0,165; K100/0,85 0,271; K100/0,95/0,03/10 0,151 (A1 ≈ A0); sàn ≤ 0,037. `t07` (không
  DES) đoán 0,131 / 0,273 / 0,166 → nguyên lý mức tải × độ cong (T5 §4) sống sót qua DES ở đối chứng (±26%).
- **Luật bậc hai:** dự đoán 0,000–0,060 ms nằm trong CI quan sát ở 6/6 chế độ → không mâu thuẫn; không phân giải
  (CI ±0,11–0,14 ms ở 8 seed; cần ~82–89 seed để CI ±0,03 ms).
- **Cơ chế:** biên t₀ ở ~phân vị 95 của Ī trên quỹ đạo tham chiếu (P(Ī > t₀) = 4,9%; P2: sd Ī 76 ms, trung vị −64 ms) ⇒
  f₀ = 0,001–0,007/ms (toy 0,198), bù một phần bởi λ = 51–151 (β lớn). Dải biên 3–14 ô oracle ⇒ a′, β chỉ là bậc độ lớn.
- **Đường (ii):** a′ < 1 ở 3/5 ô λ > 0; u TB không đơn điệu ở P2 (5 lần giảm) — nhưng nhiễu p− × λ (~2 ms) đủ giải thích.
  Chưa kết luận.
- **Tâm vs quy trình:** K100/0,85: tâm f05 0,076 = sạch 0,008 + quy trình 0,068 ± 0,053; P2/A1: 0,558 là tâm sạch.
- **Dùng cho §2:** κ_pred lấy từ `t07`; đăng ký chiều giảm của κ̂ theo T_probe; không đăng ký chiều gap thuần (f₀ có thể
  tăng khi alt cũ); tỉ lệ dự đoán dạng khoảng; S0age báo hai bản (tune như SC, và theo J); power cho gap thuần.

## §2 Tiền đăng ký — v2 (CHỐT với GVHD 2026-09-30; KHOÁ tại commit có tag `prereg-f7`)

> Thay bản nháp 29/09 (commit f0f76b9). Lý do, ghi TRƯỚC mọi output F7: (1) bản nháp so W1 với W0 = P2, hai thế giới
> khác nhau hai yếu tố (t08b: +0,145 trong +0,209 do mức tải của A); (2) κ_chung = 0,351 đo so với MỘT ngưỡng, trái yêu
> cầu ngưỡng theo chiều của F6 câu hỏi 2; so với ngưỡng theo chiều, κ_chiều(AB) = 0,193 < κ(AA) = 0,286; (3) "cùng delay
> TB" khớp bằng PSA; trong DES, ρ̄_B = 0,931 cho E[D_B] = 29,53 ± 1,14 ms, lệch A +6,0 ms; khớp DES là 0,918 (t09).
> Provenance: thiết kế do Claude (AI) đề xuất khi review L1.7 (t08b, t09, t10) và làm rõ khi chốt; tác giả viết §2.5(b);
> GVHD duyệt (biên bản 2026-09-30). Phán quyết VoIP của F6 (PIVOT; m = 8,1 ms, r = 10%) giữ nguyên. F7a → Phase 2 (T5 §4).

### 2.1 Câu hỏi
Khi hai path có cùng delay TB nhưng khác rủi ro, luật dùng độ rộng từng quyết định (K2) có vượt đáng kể ngưỡng tĩnh
theo chiều (S0dir), và sự dị loại có tạo thêm bất định trực giao trong từng chiều so với thế giới đối xứng biến động không?

### 2.2 Thế giới (DES f04b; 4 Mb/s, S = 3,024 ms, K = 100; telemetry A0: W = T_poll = H = 0,5 s, lag 0,37 s, a = 0,05 s)
Path loại A: ρ̄ 0,85 / σ 0,10 / τ 2 s (biến động). Path loại B: ρ̄ 0,918 / σ 0,03 / τ 10 s (ổn định).
- AA = cha biến động (= ô f04b K100_r0.85_s10t2) · BB = cha ổn định · AB = dị loại.
- ρ̄_B = 0,918 chốt từ t09 (seed thiết kế 11801–11848, chỉ tính chất từng path: E[D_A] = 23,50 ± 0,94 ms; khớp 0,9178,
  khoảng 0,9152–0,9203). Không đổi sau khoá.
- CRN: ba thế giới dùng cùng seed và khoá luồng 720; hai khe path = SeedSequence([seed, 720]).spawn(2) (như f04b).
  AB trùng khe 1 với AA; AB trùng khe 2 với BB.
- Nợ kỹ thuật: epoch đầy buffer suốt khoảng giữ → NaN, báo n_nan (definitions §4.4). Nhãn giữ lưới 251 điểm như f04b.

### 2.3 Luật (F = (ρ̂_cur, ρ̂_alt, path hiện tại); α = 1%; ε = 0,5·S; c = 0; tune chỉ trên seed calibration)
- S0: một ngưỡng abs|rel trên Î plug-in, tune theo J (đúng `f02.tune_static`).
- S0dir: hai ngưỡng (A→B, B→A), cùng họ abs|rel (họ chọn theo J). Tune theo J với harm thực ≤ α, mở rộng đúng khuôn
  `tune_static`: lưới tích 81 × 81, mỗi chiều = {0} ∪ 80 phân vị trong [0,3; 0,9995] của điểm theo chiều đó trên cal
  (A→B: Î_A; B→A: −Î_A; họ rel chia cho Ĉ của path hiện tại); tinh chỉnh một vòng lưới 21 × 21 giữa hai điểm lưới kề quanh
  cặp tốt nhất; chỉ thay khi J tốt hơn.
- SC, SCdir: ngưỡng trên Ī của oracle (chung / theo chiều), tune bằng harm dự đoán như f05 (`tune_center`, mỗi chiều một).
- K2(α): u = Ī − λp− > 0, λ nhỏ nhất đạt harm dự đoán ≤ α trên calibration. K2(∞): λ = 0.
- Quỹ đạo tham chiếu = quỹ đạo của S0dir. Mọi so sánh decision-level trên các cặp (epoch, cur) của nó (K16).
- Oracle bin (ρ̂_cur, ρ̂_alt, chiều) = 20 × 20 × 2; biên phân vị gộp ρ̂ dọc tham chiếu; ≥ 30 mẫu/ô; dữ liệu 597 seed.

### 2.4 Estimand
- Cơ chế: κ̂_chung (D4 của L1.6: 20 bin phân vị của Ī gộp hai chiều, detrend, sd có trọng số) và κ̂_chiều (D4 trong
  từng chiều, trung bình có trọng số theo số epoch). Báo HAI dạng: (i) theo từng seed test — dùng cho CI của M1, M2;
  (ii) gộp 90 seed — nối với f05c và anchor. Báo sàn D6 của mỗi thế giới.
- Phân rã decision-level: S0dir | SCdir − S0dir (tâm) | K2(α) − SCdir (thuần) | K2(∞) − K2(α) (an toàn) |
  headroom − K2(∞) (thông tin); kèm S0, SC để đối chiếu.
- Quỹ đạo: D = J(S0) − J(S0dir) (ms trễ trải qua); tỉ lệ đổi; flap.
- Kiểm thao tác: E[D_A] − E[D_B] trên seed test của AB; tỉ lệ epoch mỗi chiều; ô thưa theo chiều.
- Báo kèm, không quyết định: phán quyết VoIP (m, r); share_info; share_safety; p95 delay mỗi path.

### 2.5 Dự đoán
(a) Tham chiếu — do script tính, tái lập bằng t08b và t10. Mô hình dừng, cur ngẫu nhiên, chưa có quỹ đạo tham chiếu;
    tỉ lệ DES/mô hình ở f05c là 0,91–1,26 nên chỉ dùng CHIỀU và bậc độ lớn:
    κ: AA 0,286 · BB 0,217 · AB chung 0,351 / chiều 0,193 → M1 ≈ +0,16; M2 ≈ −0,09.
    Share thuần (toy, lạc quan khoảng 15–20%): AA 2,1% · AB 0,6%. Twin plug-in (t09): lệch +19,8 ms (A), +37,5 ms (B).
(b) Của tác giả — Tôi dự đoán M1 vẫn dương và ở cùng bậc với tham chiếu, khoảng +0,1 đến +0,2, vì hai chiều A→B
    và B→A có độ lệch plug-in khác nhau nên gộp hai chiều sẽ tạo thêm dị biệt mà ngưỡng theo chiều có thể hấp thụ. Với
    M2, tôi nghiêng về dấu âm, khoảng −0,05 đến −0,1: sau khi đã condition theo chiều, sự dị loại A/B không tạo thêm
    nhiều bất định trực giao so với thế giới AA biến động; tuy nhiên DES có thể làm độ lớn lệch do bộ nhớ hàng đợi và
    quỹ đạo S0dir không phân bố đều giữa hai path. Tôi không kỳ vọng V đạt mức 10%; share_adapt ở AB nhiều khả năng chỉ
    ở mức vài phần trăm. Tôi dự đoán D = J(S0) − J(S0dir) dương ở AB nhưng nhỏ, có thể dưới vài ms, và gần 0 ở AA.
    Vì vậy tôi đặt cược kết quả vào ô (ii): M2 đạt nhưng V không đạt.

### 2.6 Phép kiểm (CI95 t theo 90 seed test; ghép cặp theo seed giữa các thế giới)
- Cổng hợp lệ lúc outcome (không đạt thì estimand dựa trên oracle của thế giới đó không được diễn giải): harm ≤ α trên
  calibration cho mọi luật; ô thưa < 1% ở từng chiều; K2(α) − S0dir ≥ −2SE; đối xứng AA: CI95 của
  κ̂_chung(AA) − κ̂_chiều(AA) chứa 0, HOẶC |hiệu gộp| < 0,02.
- M1 (kiểm thao tác): κ̂_chung(AB) − κ̂_chiều(AB) > 0, cận dưới CI > 0. Không đạt ⇒ thiết kế không tạo được biến Z theo
  chiều trong DES; vẫn báo mọi thứ và ghi rõ.
- M2 (CHÍNH, cơ chế): κ̂_chiều(AB) − κ̂_chiều(AA) < 0, cận trên CI < 0 VÀ |hiệu| > tổng sàn D6 của hai thế giới.
- V (thực dụng; quy tắc SESOI tương đối đã khoá): cận dưới CI của (K2(α) − S0dir) − 0,10·headroom > 0 ở AB.
- D (phụ): cận dưới CI của J(S0) − J(S0dir) > 0 ở AB; CI ở AA chứa 0 (đối chứng).
- L (mô tả): gap thuần dự đoán theo D7 (tính từng chiều, cộng có trọng số) so với quan sát K2 − SCdir ± CI, mỗi thế giới.

### 2.7 Bảng diễn giải (viết trước để mọi kết cục đã có nghĩa)
| | V đạt | V không đạt |
|---|---|---|
| **M2 đạt** | (i) κ trong chiều không tăng mà giá trị vẫn lớn → xem f₀, β (thừa số khác của luật bậc hai) | (ii) DỰ ĐOÁN THAM CHIẾU: dị loại rủi ro được ngưỡng theo chiều hấp thụ; độ rộng vẫn bậc hai → claim âm đứng vững trước đe doạ 1 |
| **M2 không đạt** | (iv) dị loại tạo bất định trực giao có giá trị → GO bản đồ dị loại ở Phase 2 | (iii) chiều của κ sai trong DES (bộ nhớ hàng đợi?) nhưng giá trị vẫn nhỏ → sửa T5; claim âm vẫn đứng |

### 2.8 Seed
Thiết kế 11801–11848 (đã dùng, chỉ t09) · calibration 11001–11008 · test 11011–11100 (90, chính thức) ·
oracle 11101–11697 · neo: seed của f04b (cal 9701–9708, test 9711–9718, oracle 9801–9999) với khoá luồng 712.

### 2.9 Thứ tự, và khi chưa kết luận
Khoá → `f07 --mode anchor`: chạy code f07 ở CẤU HÌNH f05c (quỹ đạo S0 một ngưỡng; oracle F20x2 KHÔNG có chiều, dữ liệu
seed 9801–9999 với khoá 712 và 712 + EXTRA của f05; seed cal/test của f04b) để tái lập f05c K100_r0.85_s10t2/A0 đến chữ số
in ra: λ 51,29; t₀ 11,56; K2 − SC +0,103 ± 0,119; κ̂_pure gộp 0,271. JSON được phép lệch cỡ 10⁻¹⁴ (khác máy/NumPy)
→ `--mode validity` (cổng trên calibration; commit) → `--mode outcome` (commit).
Không thêm seed ngoài 90; phép kiểm không phân giải thì ghi "chưa kết luận". Không đổi thế giới, luật, estimand, tiêu chí.
Lỗi code phát hiện sau outcome: sửa, chạy lại toàn bộ, báo cả hai bản.

## §3 Kết quả (outcome commit 719f351; code 9507a9f; tiền đăng ký tag prereg-f7)

> Provenance: Claude (AI) soạn diễn giải từ output đã commit; tác giả kiểm từng con số. Nhãn [F] fact · [I] suy luận ·
> [H] giả thuyết. Cách hiện thực hoá 1–8 (docstring f07) được commit trước mọi lần chạy chính thức.

**Hợp lệ.** Anchor tái lập f05c bit-exact. Validity đạt ở AA, BB, AB. Cổng outcome đạt ở cả ba thế giới (harm cal theo
tiêu chí tune; ô thưa ≤ 0,04%/chiều; K2 − S0dir ≥ −2SE; đối xứng AA qua |hiệu gộp| = 0,008 < 0,02). Harm thực của luật
oracle trên cal 0,97–1,14% (báo, không cổng); trên test K2 0,97–1,00%.

Sai lệch cài đặt (8) so với §2.2 ("đầy buffer → NaN"): code giữ K·S như f04b để anchor tái lập; n_nan = 0 ở cả ba thế
giới (`f07_outcome.json`) ⇒ không ảnh hưởng số nào.

**Kiểm thao tác.** AB: E[D₁] − E[D₂] = −0,36 ± 0,91 ms (cùng trung bình), p95 92,9 so với 66,6 ms (khác rủi ro).

**Phép kiểm (90 seed test, CI95 t, ghép cặp theo seed).**
| | Kết quả | Kết luận | (a) tham chiếu | (b) tác giả |
|---|---|---|---|---|
| M1 κ̂_chung(AB) − κ̂_chiều(AB) | +0,082 ± 0,002 | ĐẠT | ≈ +0,16 | +0,1…+0,2 |
| M2 κ̂_chiều(AB) − κ̂_chiều(AA) | −0,076 ± 0,002; tổng sàn 0,072 | ĐẠT (sát sàn) | ≈ −0,09 | −0,05…−0,1 |
| V (K2 − S0dir) − 0,10·headroom, AB | −0,268 ± 0,049 ms | KHÔNG ĐẠT | không đạt | không đạt |
| D J(S0) − J(S0dir) | AB +0,009 ± 0,024; AA −0,170 ± 0,078 ms | KHÔNG ĐẠT | — | AB dương, AA ≈ 0 |
| Ô bảng 2×2 | **(ii)** | | (ii) | (ii) |

**Phân rã (ms; % headroom).** AA: thuần +0,063 ± 0,023 (1,1%), tâm +0,163, thông tin 59%. BB: thuần +0,006 ± 0,019,
thông tin 84%. AB: tâm +0,244 ± 0,047, thuần +0,091 ± 0,028 (1,5%), K2 − S0dir = 0,335 (5,6%), thông tin 64%.
VoIP (m, r): KHÔNG ĐÁNG KỂ ở cả ba. κ̂ (gộp): AA 0,276/0,268; BB 0,150/0,143; AB 0,266/0,189 (chung/chiều).

**Diễn giải.**
1. [F] Dị loại rủi ro không tăng bất định trực giao trong chiều: κ̂_chiều(AB) nằm giữa hai cha, như T5 Đính chính 2 dự
   đoán; dấu vững, độ lớn chỉ vượt tổng sàn 0,004 (CI của κ̂ có điều kiện trên oracle; sàn D6 là phép bảo vệ).
2. [F] Luật bậc hai phân giải được lần đầu: AA thuần 0,063 ± 0,023 so với dự đoán 0,051; BB khớp; AB dự đoán thiếu ~2×.
3. [F] Ngưỡng theo chiều trên twin plug-in không cải thiện J ở AB; ở AA tệ hơn 0,17 ms. [I] AA: quá khớp hai tham số trên
   8 seed calibration (J cal tốt hơn 0,11 ms, test tệ hơn 0,17 ms). [I] AB: ngưỡng vận hành ở 233–237 ms, lệch plug-in
   theo chiều (~18 ms, t09) không đổi quyết định. Offset theo chiều KHÔNG được ủng hộ ở điểm vận hành này.
4. [F] M1 bằng ~½ tham chiếu: mô hình dừng đoán κ path B quá cao (0,217 so với 0,139–0,146 DES); ~0,012 của M1 là
   thiên lệch mẫu nhỏ của ước lượng trong chiều (thấy ở AA đối xứng); M2 so hai ước lượng cùng loại nên không bị.
5. [H] Phần thuần AB > AA dù κ̂_chiều nhỏ hơn có thể một phần do SCdir mỗi chiều tự thoả α (cài đặt 3) trong khi K2 dùng
   ngân sách chung — chỉ ảnh hưởng phân rã và L, không ảnh hưởng M1, M2, V, D. Kiểm bằng f07b (POST HOC).

**Giới hạn.** Một cặp path; một điểm vận hành (α = 1%, ε = 0,5·S, 4 Mb/s, K = 100); oracle bin; tải OU giả định.

## §4 Đề xuất cho DP0/DP1 (GVHD quyết 20/10)

- Claim âm (ngưỡng tĩnh + tâm tốt ≈ đủ; độ rộng có giá trị bậc hai, nhỏ) đứng vững trước đe doạ số 1 (path khác rủi ro):
  phần thuần ≤ 1,5% headroom; K2 − S0dir ≤ 5,6%; VoIP không đáng kể ở cả ba thế giới.
- Phân rã headroom (AA / AB / BB): thông tin 59% / 64% / 84%; an toàn — giá của ràng buộc α với lượng thông tin hiện có,
  K2(∞) − K2(α) — 14% / 14% / 6%; tâm 3% / 4% / 1%; độ rộng thuần ≤ 1,5%. Phần an toàn giảm khi thông tin tăng (thông tin
  hoàn hảo ⇒ 0). Ủng hộ câu hỏi trung tâm "lợi ích đến từ tâm, độ rộng, an toàn hay thông tin" cho DP0, và chạy F8.
- Không claim "ngưỡng/offset theo chiều là thực hành tốt" (D không đạt).
- Khám phá có nhãn: f07b (SCdir ngân sách chung) để kiểm diễn giải 5.
