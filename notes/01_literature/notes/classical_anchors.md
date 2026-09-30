# Mốc toán cổ điển dùng trong T4/T5 — KHÔNG claim, chỉ trích

> 2026-09-30 (P1v2/L1.10). Provenance: Claude (AI) tìm và soạn; tác giả kiểm. [?] = chưa kiểm hôm nay.

| Mốc | Nói gì (lời của tôi) | Ánh xạ trong đề tài | Mức kiểm |
|---|---|---|---|
| Flat maximum — von Winterfeldt & Edwards 1973 (TR 011313-4-T, U. Michigan); sách 1986 (Cambridge UP) | Quanh tối ưu, mặt lợi ích phẳng: lệch ít gần như không mất | Luật bậc hai (T4 §3); AR(1) ≈ hiệp phương sai chính xác (F8 §1) | thư mục (Deep Blue hdl 2027.42/8138) |
| Radner & Stiglitz 1984 (Boyer & Kihlstrom eds., Bayesian Models in Economic Theory); Chade & Schlee 2002 (JET 107(2):421–452) | Giá trị biên của lượng thông tin rất nhỏ thường bằng 0; giá trị thông tin lồi gần 0 | gap ∝ κ²; độ dốc log–log 2,29 (t05) | thư mục + abstract |
| Điều kiện margin — Mammen & Tsybakov 1999; Tsybakov 2004; Audibert & Tsybakov 2007 (AoS 35(2):608–633) | Tổn thất luật plug-in phụ thuộc lượng mẫu sát biên; lỗi tập trung gần biên | f₀; DES 0,001–0,007/ms vs toy 0,198 (F7 §1) | abstract |
| EVPI / VSS — Birge 1982 (Math. Prog. 24(1):314–325) | EVPI: giá của thông tin hoàn hảo; VSS: lợi của dùng phân phối so với cắm kỳ vọng; WS ≤ RP ≤ EEV (min) | thông tin ≈ EVPI; thích nghi ≈ VSS nhưng so ngưỡng ĐÃ TUNE; thêm bậc an toàn và tâm | ≥ 3 nguồn thứ cấp |
| Spread–skill — Houtekamer 1993 (MWR 121(6)); Whitaker & Loughe 1998 (MWR 126) | Tương quan spread–skill cực đại khi spread biến thiên mạnh; mô hình spread log-normal | s = s₀e^η, η ~ N(0, κ²) của T4 §3 chính là spread log-normal | abstract / thứ cấp |
| Karlin & Rubin 1956 [?] | Dưới MLR, thủ tục đơn điệu (ngưỡng) là đầy đủ | Mệnh đề 1 (T4 §1) | chưa kiểm |
| Blackwell 1951, 1953 [?] | Thí nghiệm A tốt hơn B cho MỌI bài toán ⇔ B là bản làm nhiễu của A | oracle nhiều thông tin không tệ hơn; F và Q không so được | chưa kiểm |
| REV — Richardson 2000 (QJRMS 126(563):649–667); Murphy 1977 [?] | Giá trị của dự báo cho quyết định nhị phân, chuẩn hoá 0 = khí hậu, 1 = dự báo hoàn hảo | "Tỉ lệ headroom" (share) của đề tài là một dạng REV | abstract + ≥ 3 nguồn thứ cấp |
| Tương đương ràng buộc ↔ Bayes — Veeravalli–Kelly 1997, Thm 1 (trong handoff); cùng dạng Neyman–Pearson | Nghiệm bài toán có ràng buộc là nghiệm Bayes với giá thích hợp | λ của K2 (T3, T4 §3) | FULL TEXT (V–K) |

Mẫu câu cho paper: "Our quadratic law is an instance of the flat-maximum and margin-condition geometry [refs]; we do
not claim it. What we measure is where the operating point of a switch-or-stay decision under stale telemetry falls."
