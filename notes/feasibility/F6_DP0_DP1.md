# F6 v2 — DP0 + DP1: đề xuất quyết định (gửi GVHD trước họp 20/10/2026)

> Soạn 2026-09-30; gửi ≥ 24 giờ trước họp. Bản v1 (27/09): `git show f27dfe5:notes/feasibility/F6_DP0_DP1.md`.
> Provenance: Claude (AI) soạn; tác giả kiểm từng số với output đã commit. Mọi quyết định trỏ tới luật khoá TRƯỚC kết quả:
> f04b luật 3 (`cdcea06`) · f05 luật 1 (`9056ac1`) · F7 §2 (tag `prereg-f7`) · F8 §2B, §2C (`1cc9390`) · D18 · DP1-v2 · DP1-v3.

## 0. Thay đổi so với 27/09
1. **F7 (path khác rủi ro — đe doạ số 1), theo tiền đăng ký:** ô (ii) — dị loại được ngưỡng theo chiều hấp thụ; độ rộng
   thuần ≤ 1,5% headroom; VoIP không đáng kể ở cả ba thế giới (F7 §3).
2. **F8 (twin có lịch sử):** cổng oracle hỏng ở ô chính ⇒ KHÔNG kết luận xác nhận; khám phá: lịch sử tăng thông tin, không
   tăng κ̂; delay DES phụ thuộc backlog (F8 §3–4).
3. **Lý thuyết cho kết quả âm (T4, T5):** thông tin làm đổi thứ tự (Mệnh đề 1–2); luật bậc hai gap ≈ f₀β²κ²/(2a′), lần đầu
   phân giải ở F7 (AA: 0,063 ± 0,023 ms so với dự đoán 0,051).
4. **Literature (L1.10):** phép so "luật dùng phân phối vs luật tĩnh đã tune" đã có tiền lệ (Veeravalli–Kelly 1997; Jewson
   2003) ⇒ DP1 vẫn NARROW, đóng góp thu về tách kênh độ rộng khi κ > 0 + phân rã (positioning v2).
5. **Sai lệch đã ghi:** Phần A làm một phần trước khi chạy F7 (log 30/09); mục (12) của f08 thêm sau khi trợ lý thấy validity
   sandbox (chỉ phần báo). Không sai lệch nào chạm tiền đăng ký.
6. **Minh bạch AI:** phần lớn phép dẫn, script và diễn giải do Claude (AI) soạn; tác giả chạy lại, kiểm; provenance trong file.

## 1. Quyết định đề xuất

| # | Quyết định | Đề xuất | Căn cứ |
|---|---|---|---|
| 1 | DP0 — claim VoIP | **PIVOT, giữ nguyên**: ngưỡng tĩnh đủ trong phạm vi đã kiểm (m = 8,1 ms, r = 10%) | brief v2.1 §10: GO không đạt; NARROW (buffer sâu) đã kiểm qua các ô K = 100 (f04b, f05, F7) vẫn không đáng kể; F7 §3; F8 §3 (cận thấu thị 6,84 < m) |
| 2 | DP1 (D18) | **NARROW** | positioning v2; DP1-v3 |
| 3 | K24 — câu hỏi trung tâm | Duyệt RQ-I (thông tin, trục chính) và RQ-W (ranh giới độ rộng) — §4 câu 2 | F7 ô (ii); F8 khám phá; f05 (Q) |
| 4 | Phạm vi Phase 2 | **A**, có cổng mở đầu: kiểm tính mới RQ-I | §4 câu 3 |
| 5 | K15 — đầu ra | NCKH trước (đủ nội dung từ Phase 1); paper dạng đặc trưng hoá + kết quả âm có cơ chế, venue chọn khi có CFP | venue_notes |

## 2. Claim có phạm vi và cơ chế
**Claim.** Một luồng nhỏ trên tải nền ngoại sinh OU-Poisson, M/D/1/K FIFO, telemetry đếm gói có tuổi và nhiễu, 4 Mb/s,
K ∈ {11, 100}, α = 1%: ngưỡng tĩnh đã tune thua oracle cùng thông tin ít hơn SESOI ở mọi ô đã kiểm — path đối xứng (F2,
f04b, f05), tuổi dao động (f05), path khác rủi ro (F7), twin có lịch sử (F8, trừ ô cổng hỏng).
**Vì sao — bốn tầng.**
1. *Cận trên:* K = 11 có headroom < m kể cả khi biết trước tương lai (18/24 ô/biến thể, f02b).
2. *Phân rã:* headroom = thông tin 59–84% + an toàn 6–14% + tâm 1–4% + độ rộng thuần ≤ 1,5% (F7 §4; P2 f04b: 9,418 +
   1,289 + 0,149 + tĩnh 3,700 = 14,556 ms).
3. *Cơ chế:* ngưỡng tĩnh chỉ thua khi có thông tin làm đổi thứ tự (Mệnh đề 2); khi có, thiệt hại là bậc hai theo κ và tỉ lệ
   mật độ epoch gần biên f₀ — ở DES f₀ nhỏ hơn toy 30–200 lần, nên κ̂ = 0,15–0,27 có thật mà độ rộng gần vô giá trị (T4 §3;
   f05c; F7 §1).
4. *Mạng:* κ = mức tải × độ cong trên hai chiều thông tin (T5 §4; t07 khớp DES ±26%); dị loại rủi ro bị ngưỡng theo chiều
   hấp thụ (F7); lịch sử tăng thông tin, không tăng κ̂ (F8, khám phá).
**Toán cổ điển, không claim** (flat maximum, điều kiện margin, Radner–Stiglitz, EVPI/VSS, REV); **phép so đã có tiền lệ**
(V–K 1997; Jewson 2003). Ứng viên mới: tách kênh độ rộng khi κ > 0 + phân rã với oracle cùng thông tin.
**Phát hiện phương pháp.** (i) PSA lệch DES có hệ thống, thổi phồng khoảng thích nghi ở P2 (f04b). (ii) Oracle bin không
luôn là cận trên — lần thứ ba ở F8 T10/FH ⇒ K10′.

## 3. Mối đe doạ (cập nhật)
| # | Đe doạ | Trạng thái 30/09 | Còn lại |
|---|---|---|---|
| 1 | Hai path đối xứng | ĐÃ KIỂM (F7): dị loại rủi ro không mở đường cho độ rộng | dị loại độ tươi (F7a) → Phase 2 |
| 2 | Mục tiêu trung bình | toy t10: dưới SLO không ràng buộc, phần thuần ≈ 0 ở thế giới đối xứng | chưa kiểm trong DES |
| 3 | Một luồng nhỏ | ngoài phạm vi (họ tập thể: Fischer–Vöcking, Seshadri–Katz, Keralapura) | ghi giới hạn |
| 4 | Oracle | bin không luôn là cận trên (F8) | K10′ |
| 5 | Mô hình tải | OU một thang thời gian | burst/đuôi nặng chưa kiểm |
| 6 | Thang thời gian | đề tài ở thang giây; SD-WAN mặc định 10–60 phút (Cisco AAR) | ghi phạm vi |

## 4. Câu hỏi cho GVHD (mỗi câu có đề xuất)
1. **DP0, DP1:** thầy đồng ý PIVOT (claim VoIP giữ nguyên) và NARROW? *Đề xuất: có.*
2. **K24 — câu hỏi trung tâm.** NGUỒN GỐC: rút ra SAU kết quả Phase 1; sẽ kiểm trên seed chưa dùng (test 20000–29999,
   oracle 30000–39999), tiền đăng ký mới.
   > Trong quyết định đổi/giữ đường dưới telemetry cũ và nhiễu, giá trị của một NDT nằm ở đâu — ước lượng trạng thái (tâm),
   > luật dùng bất định (độ rộng), giá của ràng buộc an toàn, hay telemetry giàu và tươi hơn (thông tin) — và cơ chế
   > hàng đợi–telemetry nào quyết định phân chia đó?
   - **RQ-I (trục chính):** lịch sử số đo (bộ lọc trên trạng thái backlog–tải), telemetry hàng đợi và độ tươi thu hẹp khoảng
     thông tin bao nhiêu (tỉ lệ headroom, ms), và phần thu được đi qua tâm hay qua độ rộng?
   - **RQ-W:** ở vùng nào (α chặt, telemetry ít nhiễu, nhiều quyết định gần biên) độ rộng vượt r = 10% headroom, và luật bậc
     hai đã hiệu chỉnh có dự đoán đúng ranh giới đó trên seed mới không?
   *Trung thực:* bảng "kết quả F7 → phạm vi" của kế hoạch viết cho F7a; F7 đã chạy là F7b. Ánh xạ theo nghĩa: luật đã hiệu
   chỉnh dự đoán tỉ lệ nhỏ (AA 2,1%, AB 0,6%) và quan sát nhỏ ⇒ ô (iii) "κ không đủ ⇒ thông tin thành trục chính". Đây là
   suy luận sau kết quả, xin thầy xác nhận.
3. **Phạm vi Phase 2.** *A (đề xuất):* RQ-I + RQ-W + một tầng thực tế time-box (X1′ hoặc Mininet); cổng mở đầu: kiểm tính mới
   RQ-I (họ VoI / thiết kế telemetry) — trùng nặng ⇒ rơi về B. *B (tối thiểu):* NCKH viết từ Phase 1; Phase 2 chỉ RQ-W.
   *C (không đề xuất):* RQ2 cũ (bền khi dịch chuyển chế độ) — trùng OpenTwin/LEC/CERT, có tiền lệ V–K 1997.
   Thứ tự cắt khi trễ (A): tầng thực tế → F7a → một phần lưới RQ-W.
4. **K15 — đầu ra:** NCKH trước; paper khi có CFP thật (CNSM 2027 main vẫn là ứng viên).
5. **Phần A:** log 30/09 ghi còn thiếu o01, CI tay, bảng tay 10 epoch, kín sách bấm giờ ×2, Q1–Q5. Thầy chọn (a) vấn đáp
   15–20 phút đầu buổi thay cho các bài còn thiếu, hay (b) em nộp đủ trước buổi họp?
6. **Chế độ tuổi:** F6 v1 đề xuất A1 chính; F7, F8 chạy A0 (A1 không đổi kết luận ở f05; giữ neo bit-exact f04b).
   *Đề xuất: A0 chính, A1 độ nhạy.*

---
## Phụ lục A — Rủi ro → spike → kết quả → quyết định (bổ sung bảng v1)
| Rủi ro | Spike | Kết quả (số) | Quyết định |
|---|---|---|---|
| "Vì sao" chỉ là phát biểu lại H1 | T4, t03c, t05 | Mệnh đề 1–2; gap ∝ κ² (độ dốc 2,29); κ* ≈ 0,82 cho 10% (toy) | Có lý thuyết; toán cổ điển, không claim |
| Cơ chế mạng nào tạo κ | T5, t06, t07, t08/t08b | κ = mức tải × độ cong; t07 khớp DES ±26%; dị loại: κ_chiều nằm giữa hai cha | Chọn F7b; F7a sang Phase 2 |
| Luật bậc hai trên DES | f05c (POST HOC) | Không mâu thuẫn 6/6 chế độ; f₀ = 0,001–0,007/ms | Hiệu chỉnh dự đoán F7 |
| Path khác rủi ro (đe doạ 1) | F7 (tiền đăng ký, 90 seed) | Ô (ii): M1 +0,082 ± 0,002; M2 −0,076 ± 0,002; V −0,268 ± 0,049 ms; D không đạt | Claim âm đứng vững; không claim offset theo chiều |
| Lịch sử mở đường cho độ rộng? | F8 (tiền đăng ký) + f08b (khám phá) | Cổng T10/FH hỏng (−3,1 SE) ⇒ không kết luận; khám phá: κ̂ không tăng; share_info −24,5 điểm % trên quỹ đạo chung | K10′; giả thuyết trạng thái (backlog, tải) |
| Gap literature khung mới | L1.10 | V–K 1997, Jewson 2003 đã so; chưa thấy ai tách kênh độ rộng khi κ > 0 | DP1 = NARROW |

## Phụ lục B — ADR đề xuất (ghi SAU họp, theo K23)
| ID | Đề xuất | Căn cứ |
|---|---|---|
| SESOI | Giữ m = 8,1 ms, r = 10% | khoá 504677e trước F2 |
| K7 | 4 Mb/s, S = 3,024 ms; báo buffer theo K·S (ms) | F1; f02b |
| K8 | W = H = 0,5 s; a = 0,05 s; lag TB 0,37 s; A0 chính, A1 độ nhạy | f05; F7; F8 |
| K9 | τ ∈ {2, 10} s; σ ∈ {0,03; 0,10} | F1 |
| K10′ | Oracle bin cùng F dọc quỹ đạo tham chiếu, ≥ 20 bin/chiều; kiểm K2 − tĩnh ≥ −2SE trên seed oracle GIỮ RIÊNG trong validity; báo độ nhạy đặc tả | f05; F8; f08b |
| K11 | DES đầy đủ (Numba); PSA chỉ định hướng | f04; f04b |
| K12 | ≥ 90 seed test cho phép kiểm cơ chế; 8 seed đủ cho phán quyết SESOI | F3; F7 |
| K17′ | Chỉ số cơ chế chính κ̂ = D4 (L1.6); `sd_log_s_cond` (D5) phụ | log 2026-09-29 |
| K6′ | F mở rộng: chiều (F7); lịch sử Kalman (F8); tuổi riêng từng path (Phase 2) | F7; F8 |
| K24 | Câu hỏi trung tâm + RQ-I, RQ-W | §4 câu 2 |
| K25 | Estimand phân rã: share_info, share_center, share_pure, share_safety (+ ms); V giữ r = 10% | F7 §2.4 |
| K15 | Đầu ra | §4 câu 4 |
| DP0 / DP1 | PIVOT / NARROW | §1 |

## Phụ lục C — Gate Phase 1 v2 (trạng thái trung thực)
| Validity | Trạng thái |
|---|---|
| O1 do tác giả viết; phân rã tự dựng; kín sách lần hai | ⚠️ O1 §1–3 có (ee66775); còn thiếu các mục ở §4 câu 5 |
| T4, T5; t05, t06 tự viết lại khớp đáp án | ⚠️ Claude (AI) soạn phép dẫn và script; tác giả chạy lại, kiểm — dùng AI theo cho phép của GVHD |
| κ̂ khoá trước f05c; f05c ghi POST HOC | ✅ nội dung: AI đóng dấu D1–D11 lúc 2026-09-29T01:14Z, trước khi chạy · ⚠️ chứng cứ git: tác giả commit (4e3addd) sau khi đã đọc kết quả — ghi trong log; f05c là POST HOC |
| Tiền đăng ký F7 khoá trước mọi output; thầy đã đọc | ✅ tag `prereg-f7`; tại commit khoá không có file f07; biên bản 30/09 |
| F7: anchor, validity, cổng outcome | ✅ anchor bit-exact; mọi cổng đạt ở AA, BB, AB |
| F8: cổng outcome | ❌ T10/FH ⇒ ô đó không diễn giải (đúng luật khoá) |
| Forward citation; mỗi họ mới ≥ 1 full text | ⚠️ F–V ✅; Seshadri–Katz ✗ (không lập chỉ mục); full text Tiwari, Li, V–K, Jewson ✅; SD-WAN chỉ có tài liệu Cisco |

## Phụ lục D — Seed
Đã dùng: 9000–9999 (pilot, spike v1, t01–t05; F2/f04b/f05: cal 9701–9708, test 9711–9718, oracle 9801–9999) và 11000–11999
(spike, toy v2; F7/F8: cal 11001–11008, test 11011–11100, oracle 11101–11697). **Chưa dùng:** 10000–10999, 12000–19999,
20000–29999 (test), 30000–39999 (oracle) ⇒ tập test Phase 2 còn "mù". Đề xuất protocol §7 mới: xem ADR sau họp.
