# Experiment log

Mẫu cho mỗi thí nghiệm (copy khối dưới):

## eNN — tên
- **RQ / hypothesis:**
- **Dự đoán (viết TRƯỚC khi chạy):**
- **Config + seed:** experiments/configs/...
- **Kết quả:** results/eNN/...
- **Diễn giải:** (khớp / không khớp dự đoán — vì sao?)
- **Bước tiếp theo:**

## 2026-09-23 — Exposure và chuẩn bị L0.3/L0.4

- Agent được người dùng yêu cầu tự kiểm tra và điền choices/brief/design.
- Đã xem đáp án VD2–VD6; lời giải được ghi là tham khảo, không phải tự làm mù.
- Đã chạy Monte Carlo exact/naive ở lượt trước, seed 0, n=2.000.000.
  z/tau=0,3: 56.030 mẫu trong bin, observed=0,023219703730144564,
  exact=0,023223298670823258, naive=0,006115615880504457.
- Đã đọc pilot do người viết lesson cung cấp: W hữu hạn làm calibration dao động;
  D0 phi tuyến có thể gây underprediction lớn. Các số pilot này chưa được agent
  tái chạy bằng wsim.py/nl.py. Không gán chúng cho artifact của đồ án.
- Lượt hiện tại chỉ kiểm data summary, ví dụ số và existing tests; chưa chạy e01–e12.
- Dự đoán thiết kế nằm trong brief/design v1; trước confirmatory phải bổ sung
  config, seed list, contrast và family Holm cụ thể. Hướng đã thấy ở pilot không
  được gọi là phát hiện mù; e03 nhắm ranh giới calibration và hành vi D1.

## 2026-09-23 — Sanity check D12 trước khi sửa W_ref

- Review ngoài chỉ ra W_ref v1 có κ≈2,256 và H2 suy biến; đây là exposure trước test.
- Agent chọn trước κ_ref=0,5 vì còn path ưu thế nhẹ nhưng always-trust không tự đạt
  harmful budget trong cell tham chiếu ở tuổi trung bình.
- Chạy NumPy seed 20260923, n=4.000.000, Gaussian OU exact, σ_D=2,437490,
  z/tau=0,3: pair flip=0,2054485; harmful@2ms=0,03101175;
  mean regret=0,22203761 ms.
- Mục đích chỉ là kiểm câu hỏi có khả năng phân biệt phương pháp; không dùng batch
  này làm confirmatory evidence và không tune κ tiếp theo kết quả phương pháp.

## 2026-09-24 — P01 load information (EXPLORATORY)

- **RQ / hypothesis:** Trạng thái tải cũ mà NDT quan sát có giúp xếp hạng quyết định
  nguy hiểm tốt hơn các cổng không dùng trạng thái hiện tại không; và chuẩn hoá
  theo độ nhạy có khác chuẩn hoá theo độ lớn không?
- **Dự đoán (viết TRƯỚC khi chạy):** Trên M/M/1, `sens(delta)` sẽ hơn
  `magnitude` vì T'/T thay đổi mạnh. Trên đường cong Mininet poisson/6 Mbps/q=13,
  hai cách sẽ gần ngang nhau vì T'/T gần hằng; `history` sẽ thua các cổng dùng
  trạng thái tải trong các cell không suy biến. Cell z=0,5, sigma_f=0,03 có thể
  suy biến do harm rate gần ngân sách 1%.
- **Dự đoán chưa chạy:** Với buffer 200 gói, dải T'/T có thể biến thiên
  rộng hơn q=13 trước khi bão hoà, nên `sens(delta)` có thể tách khỏi `magnitude`.
  Baseline Mondrian theo bin tải dự kiến hơn `history` và gần `magnitude`, nhưng
  chưa kết luận hơn/kém `PROPAGATED`.
- **Config + seed:** `experiments/pilot/p01_load_information.py`; seed 9001–9003 chỉ
  dùng cho pilot; không dùng lại cho thí nghiệm chính.
- **Trạng thái trước chạy:** Chưa chạy tại thời điểm ghi các dự đoán trên.
- **Kết quả (chạy 2026-09-24):** Chạy thành công bằng `.venv/bin/python`
  (Python 3.14.5, NumPy 2.5.3, SciPy 1.18.1). Output đầy đủ lưu tại
  `experiments/pilot/results/p01_load_information_output.txt`. T'/T của M/M/1
  tăng 2,2→66,7; của đường cong đo chỉ dao động 5,5–8,3. Hai cell
  z=0,5, sigma_f=0,03 có harm=0,013 và được đánh dấu suy biến. Với
  measured z=0,5, sigma_f=0,06, T_reg=20: history=0,599, magnitude=0,718,
  sens(delta)=0,723, PROPAGATED=0,761. Toàn bộ bảng khớp output tham chiếu
  trong hướng dẫn đến 3 chữ số thập phân.
- **Diễn giải:** Khớp dự đoán trước chạy. Tương phản trạng thái so với
  lịch sử có tín hiệu, nhưng claim độ nhạy hơn độ lớn không được ủng hộ
  rõ trên đường cong Mininet hiện tại. Chưa được suy diễn các số pilot này
  thành bằng chứng confirmatory.
- **Bước tiếp theo:** K1 trên cả 9 đường cong và K2 neo tham số vào log thực tế;
  sau đó mới mở rộng CERT-lite/Mondrian hoặc chạy Mininet buffer lớn.
- **Giới hạn sử dụng:** Pilot khám phá; không dùng các số này làm bằng chứng
  trong thuyết minh, báo cáo hay paper.

---

## Từ đây: hướng v2 (switch-or-stay), xem decision log PIVOT-v14. Các mục trên thuộc hướng v1 hoặc pilot chuyển tiếp.

## 2026-09-25 — Cứu artefact số liệu của thuyết minh v12/v14 (Phase 0 v2, L0.1)

- **Loại:** pilot/chẩn đoán trước plan; KHÔNG phải kết quả chính.
- **Tìm thấy:** `/home/vantai/dacn/thuyet_minh_nckh/measurements/switch_or_stay_diagnostic.py` và
  `/home/vantai/dacn/thuyet_minh_nckh/results/switch_or_stay_diagnostic.txt`.
- **Không tìm thấy:** script riêng cho pilot fixed-vs-scaled v12; phần phân tích này nằm chung trong
  `switch_or_stay_diagnostic.py`, seed 42.
- **Chạy lại:** output trùng byte với file gốc; lệnh chạy được ghi trong header script.
- **Kiểm độc lập (nghiệm + 12 seed):** loss M/D/1/K, K=11: ρ=0,8 → 0,235337% (12 seed:
  TB 0,238306%, SD 0,019628%, max 0,274333%); ρ=1,0 → 4,615385% (TB 4,648667%,
  SD 0,114709%, max 4,909000%). Số trong thuyết minh v14 = max của 12 seed.
- **Không dùng cho:** claim RQ1/RQ2.

## 2026-09-25 — P02 objective rules (EXPLORATORY, Phase 0 v2 / L0.3)

- **Câu hỏi:** ba mục tiêu (a)/(b)/(c) cho luật khác nhau thế nào; hai bẫy hiệu chỉnh (tiêu hết ngân sách,
  đổi vô ích) có xuất hiện không?
- **Dự đoán trước khi chạy:** các khẳng định về (a), (b), (c) và Bài 1–3 đã có trong PHASE_0 v2 L0.3 (lý thuyết).
  Hai bẫy hiệu chỉnh được PHÁT HIỆN khi chạy, không có dự đoán đăng ký trước. Ghi đúng như vậy.
- **Config + seed:** `experiments/pilot/p02_objective_rules.py`; seed 9101–9103, chỉ cho pilot này.
- **Kết quả:** `experiments/pilot/results/p02_objective_rules_output.txt`. A: gap ngưỡng tĩnh–oracle 8,30 điểm %;
  B: 0,055 điểm % (thứ tự không đảo); B: (c) vô nghiệm; C: tiêu hết ngân sách cho harm 1,000% vô ích; κ = 0,01 giảm
  đổi 84,83% → 10,00%.
- **Repeatability:** output trên Python 3.14.5, NumPy 2.5.3, SciPy 1.18.1 trùng byte với bản in trong L0.3;
  MD5 `79ff41710627db1e220b6b55a3a9df3c`.
- **Diễn giải:** ủng hộ K2 (b) có hiệu chỉnh KKT, K17 (đại lượng H2 là mức đảo thứ tự), K21 (κ). Thế giới đồ chơi,
  không nói gì về độ lớn hiệu ứng trong mạng.
- **Không dùng cho:** claim RQ1/RQ2.

## 2026-09-25 — P03 H2 indices (EXPLORATORY, Phase 0 v2 / L0.4)

- **Câu hỏi:** chỉ số nào theo đúng khoảng cách ngưỡng tĩnh–oracle (K17)?
- **Dự đoán trước khi chạy:** sd_log_s báo động giả ở thế giới B (s tăng cùng Î) — đã dự đoán trong L0.2.
  Lỗi của Spearman trên mọi epoch ở thế giới C (do kẹp p±) được PHÁT HIỆN khi chạy, không có dự đoán trước.
- **Config + seed:** `experiments/pilot/p03_h2_indices.py`; dùng lại thế giới và luật P02 (seed 9101–9103), thêm D (9104).
- **Kết quả:** `experiments/pilot/results/p03_h2_indices_output.txt`. Khoảng cách (điểm %): A 8,181; B 0,054; C 0; D 0,042.
  rd_kappa: 0,104; 0; 0; 0,004. sd_log_s_cond: 0,699; 0,068; 0; 0,082. sd_log_s: 0,699; 0,565; 0; 0,228.
  rd_all: 0,078; 0; 0,195; 0,005.
- **Repeatability:** output trên Python 3.14.5, NumPy 2.5.3, SciPy 1.18.1 trùng byte; MD5
  `4c0b95cadc42c3b6b156c52b19a09d0d`.
- **Diễn giải:** ủng hộ định nghĩa rd_kappa và sd_log_s_cond; loại rd_all; sd_log_s chỉ là biến phụ. Thế giới đồ chơi,
  không nói gì về độ lớn trong mạng.
- **Không dùng cho:** claim RQ1/RQ2.

## 2026-09-25 — P04 evaluation protocol (EXPLORATORY, Phase 0 v2 / L0.5)

- **Câu hỏi:** (1) hai tầng đánh giá có thể cho thứ hạng khác nhau không, và vì sao; (2) luật có nhiều thông tin hơn
  oracle có thắng oracle không.
- **Dự đoán trước khi chạy:** (2) đã được dự đoán trong PHASE_0 v2 L0.5. (1) chỉ dự đoán "có thể lệch"; việc đảo thứ hạng
  hoàn toàn khi tham chiếu ngẫu nhiên, và cách sửa bằng tham chiếu thực tế, được PHÁT HIỆN khi chạy thử (1 seed → 10 seed
  → thêm tham chiếu thực tế) trước khi chốt script. Ghi đúng như vậy: đây là ngã rẽ ở mức pilot, dùng để thiết kế giao thức.
- **Config + seed:** `experiments/pilot/p04_evaluation_protocol.py`; seed 9105–9114.
- **Kết quả:** `experiments/pilot/results/p04_evaluation_protocol_output.txt`. Tham chiếu ngẫu nhiên: J_dl ext < orc 10/10,
  nhưng J_tr ext < orc 0/10, delay 0/10. Tham chiếu thực tế: J_dl ext < orc 10/10, orc < fix 10/10; J_tr ext < orc 7/10,
  orc < fix 8/10; delay ext < orc 8/10.
- **Repeatability:** output trùng byte; MD5 `c8823fd5e37851f424a436964a5f67c9`.
- **Diễn giải:** ủng hộ K16 (tham chiếu thực tế), K10 và điều kiện F_oracle ⊇ F_policy. Thế giới đồ chơi; chênh lệch delay rất
  nhỏ; không nói gì về độ lớn trong mạng.
- **Không dùng cho:** claim RQ1/RQ2.

## 2026-09-25 — P05 token bucket so với testbed (EXPLORATORY, Phase 0 v2 / L0.6)

- **Câu hỏi:** mô hình token bucket kiểu HTB có giải thích số đo testbed tốt hơn M/D/1/K không (ứng viên X1′, K20)?
- **Dự đoán trước khi chạy:** L0.1 đã suy ra testbed là token bucket từ OWD của CBR; dự đoán token bucket khớp tốt hơn.
  Mức khớp cụ thể không được dự đoán trước. Một lần chạy thử với seed 0–2 trước khi chốt script (không lưu).
- **Config + seed:** `experiments/pilot/p05_token_bucket_testbed.py`; seed 9115–9117; poisson, 4 Mb/s, q = 10.
- **Kết quả:** `experiments/pilot/results/p05_token_bucket_testbed_output.txt`. |OWD| lệch: token bucket TB 3,3%, max 6,3%;
  M/D/1/K TB 57,0%, max 135,8%. Loss của token bucket thấp hơn số đo ở tải vừa (ρ = 0,8: 0,129% so với 0,221%), hội tụ ở tải cao.
- **Diễn giải:** ủng hộ K20 đề xuất sửa (X1′); giải thích phần lệch nêu ở thuyết minh v14. Mới kiểm một cấu hình.
- **Không dùng cho:** claim RQ1/RQ2.

## 2026-09-26 — L1.1 bước 0: kiểm Numba trên Python 3.14

- **Mục đích:** kiểm rủi ro công cụ trước khi viết `mdk.py`; chưa phải thí nghiệm RQ1/RQ2.
- **Trước cài:** Python 3.14.5, NumPy 2.5.3; Numba chưa có. `pip --dry-run` dự kiến Numba 0.67.0 và
  llvmlite 0.49.0, giữ nguyên NumPy 2.5.3 (`numpy<2.6,>=1.22`).
- **Sau cài:** Numba 0.67.0, llvmlite 0.49.0, NumPy vẫn 2.5.3; không bị hạ phiên bản.
- **Smoke test:** `njit(lambda x: x + 1)(41)` trả về `42`.
- **Kết luận:** Numba chạy được trong virtualenv hiện tại; chưa dùng Numba trong code nền móng của L1.1.

## 2026-09-26 — L1.2 khởi động: OU, cửa sổ đo và nhiễu đếm

- **Trạng thái:** tác giả xác nhận đã tự tính và nháp sáu kết quả lý thuyết bên ngoài repository; đã hệ thống hóa thành
  `notes/theory/T2_ou_measurement.md` và sửa đính chính `z_eff` trong definitions. Chưa chạy `t02_ou_check.py` tại
  thời điểm ghi các dự đoán dưới đây.
- **Dự đoán NT-1 (TRƯỚC khi chạy):** (a) chỉ hai dòng đối chứng âm Euler phải báo LỆCH; 17 dòng kiểm công thức phải
  khớp, ngoại trừ báo động giả do lấy mẫu; (b) với 17 phép kiểm ở mức 95%, kỳ vọng `17 × 0,05 = 0,85` dòng LỆCH
  do may rủi; (c) ở `τ = 10 s`, 4 Mb/s, `Var(G|y)` có nhiễu dự kiến lớn hơn không nhiễu khoảng `5,75` lần
  (`7,803×10⁻⁴ / 1,357×10⁻⁴`).
- **Config + seed:** `experiments/t02_ou_check.py`; seed 9201–9220, 9401–9420, 9501–9520 và 9601–9620;
  `μ = 0,9`, `σ = 0,03`, `W = H = 0,5 s`, `g = 0,5 s`, `Δt = 0,002 s`, 20.000 quỹ đạo/seed.
- **Kết quả:** `experiments/results/t02_ou_check_output.txt`; 17/17 phép kiểm công thức khớp CI 95%; 2/2 đối
  chứng âm Euler báo LỆCH như dự đoán. Ở `τ = 10 s`, phương sai MC là `1,3581×10⁻⁴` khi không nhiễu và
  `7,8254×10⁻⁴` khi có nhiễu, tỉ số `5,76`, gần dự đoán `5,75`.
- **Diễn giải:** xác nhận bằng mô phỏng các công thức OU rời rạc chính xác, `V(L)`, nhiễu đếm và phân phối hậu
  nghiệm tuyến tính trong cấu hình pilot. `z_eff` không đủ cho kỳ vọng khi có nhiễu; đề xuất F1 báo thêm `R/V(W)`,
  tỉ lệ phương sai giải thích và độ không đồng đều do tuổi (không tạo ADR, theo K23).
- **Phạm vi:** không thêm code OU vào `ndtrisk/`; đây là kiểm công thức, không phải thí nghiệm RQ1/RQ2.

## 2026-09-26 — L1.1 · t01 kiểm `mdk.py` bằng DES workload

- **Điều kiện lý thuyết:** tác giả xác nhận đã tự tính và nháp sáu phần dẫn xuất ngoài repository; T1 ghi lại các
  kết quả và provenance triển khai.
- **Dự đoán NT-1 (TRƯỚC khi chạy):** nghiệm giải tích phải nằm trong CI 95% của loss và `W_q` ở `(ρ,K)` bằng
  `(0,5;2)`, `(0,8;11)`, `(1,0;11)` và `(0,9;30)`. Loss ở `(0,95;100)` và `(0,8;30)` sẽ không đủ sự kiện để
  kiểm: số drop kỳ vọng lần lượt là `8,18` và `2,60`; `(0,9;30)` có khoảng `920,59` drop nên kiểm được.
- **Seed/config:** 9001–9020, 200.000 arrival/seed, `S=1`; tại thời điểm ghi dự đoán chưa chạy `t01`.
- **Kết quả:** `experiments/results/t01_mdk_des_check_output.txt`; nghiệm giải tích nằm trong CI 95% ở mọi đại
  lượng có đủ sự kiện. `(0,95;100)` và `(0,8;30)` được đánh dấu đúng là không đủ drop; `(0,9;30)` kiểm được cả
  loss và `W_q`. Output chạy lặp lại phải trùng byte vì seed cố định.
- **Diễn giải:** lát cắt ổn định phân phối nhúng; `poisson.sf`, tổng đuôi, dạng toàn số dương khi `ρ≥1` và Little
  trực tiếp lần lượt chặn các lỗi triệt tiêu số. Đây là kiểm công thức/nền DES, không phải kết quả RQ1/RQ2.

## 2026-09-26 — L1.3 · t03 luật K2 + t03b minh họa Jensen

- **Điều kiện lý thuyết:** tác giả xác nhận đã tự làm phần chứng minh/tính nháp ngoài repository và yêu cầu hiện
  thực hóa pseudocode. Vì vậy không mô tả `t03` là code tự viết không có AI; `T3_objective.md` ghi provenance.
- **Dự đoán (TRƯỚC khi chạy):** `λ>0` ở A và B vì ràng buộc harm cắn; `λ=0` ở C vì luật `Î>0` đã an toàn.
  Khoảng cách K2 − ngưỡng tĩnh chỉ dương ở A: `s` độc lập với `Î` làm đảo thứ tự. B có `s` thay đổi nhưng điểm
  K2 vẫn tăng theo `Î`; C có ngân sách thừa. Tại thời điểm ghi dự đoán chưa chạy `t03` hoặc `t03b`.
- **Seed/config:** 9101–9103 cho ba thế giới, 9301 cho Jensen; `N=400.000`, `ε=0,5 ms`, `α=1%`, `c=0`;
  ngưỡng tĩnh tìm bằng sắp xếp và tổng tiền tố, không dùng lưới.
- **Kết quả t03:** `experiments/results/t03_k2_rule_output.txt`; A: tĩnh `0,8616`, K2 `0,9568`, `λ=9,91`, gap
  `0,0952 ms`; B: hai gain `0,9435`, `λ=38,90`, gap đúng `0`; C: hai gain `0,1193`, `λ=0`, gap `0`.
  Sáu nhóm tự kiểm đạt; `α=100%` trùng `Î>0` từng epoch.
- **Kết quả t03b:** `experiments/results/t03b_jensen_demo_output.txt`; Jensen ở K=11 là `+0,07`, `+0,05`,
  `+0,02 ms`; ở K=100 là `+0,40`, `+5,90`, `+25,91 ms` cho tải trung bình 0,85/0,93/0,97.
- **Sự cố khi chạy:** lần đầu dừng sau A vì bộ tự kiểm áp nhầm dung sai gain `0,002 ms` cho `λ` chỉ được báo
  đến hai chữ số. Ban đầu tách dung sai `λ` thành `0,02 ms`, không đổi thuật toán/dữ liệu; review L1.4 siết tiếp
  xuống `0,005 ms`, đúng nửa đơn vị chữ số cuối của đáp án in đến `0,01 ms`. Hai giá trị `9,9113` và `38,8953`
  vẫn đạt; việc siết chỉ làm phép kiểm khó hơn.
- **Đính chính:** B có gap đúng bằng 0 (`0,0008` là artefact lưới); mức giảm missed `8,3 điểm %` thuộc mục tiêu
  cũ, còn K2 là khoảng `7,9 điểm % ≈ 0,095 ms` ở A.
- **Đề xuất F2:** báo bốn bậc tĩnh, K2 có ràng buộc, K2 không ràng buộc và headroom để tách giá trị thích nghi,
  giá của an toàn và giá trị thông tin; không tạo ADR (K23). Đây vẫn là toy/minh họa, không phải claim RQ1/RQ2.

## 2026-09-26 — L1.4 bước 0: trạng thái luyện sở hữu

- Chưa có bằng chứng trong repository rằng tác giả đã làm bài luyện kín sách 30 phút để viết lại `static_best` và
  `k2_rule`. Không ghi đạt thay cho tác giả; cần bổ sung kết quả thật trước buổi vấn đáp 2026-10-13.

## 2026-09-26 — L1.4 · F1 điểm vận hành

- **Đính chính 2026-09-26:** ba mục dưới đây **không phải dự đoán mù**; output f01 đã xuất hiện trong phiên hướng
  dẫn L1.4 khi mentor kiểm script, trước khi chúng được ghi vào log. Kết quả F1 không đổi; rút nhãn “dự đoán trước”.
- **Kỳ vọng đã biết trước khi chạy lại f01:** (1) tại anchor CLEAN 4 Mb/s, `σ=0,03`, `τ=10 s`, `Π_noise` lớn hơn
  tham chiếu 5,78, khoảng 6,00, vì `z_eff≈0,919 s<1 s`; (2) tại 8 Mb/s, tỉ số `sd_p95/sd_p05` lớn nhất ở
  `(σ,τ)=(0,10;2 s)`, khoảng 1,142 nên vượt 1,10; (3) tại 8 Mb/s, `Π_relax>1` chỉ ở `(ρ̄,τ)` bằng
  `(0,95;0,5 s)` và `(0,95;2 s)`.
- **Dữ liệu:** `data/aoi_measured/aoi_v7_estimates.json`, lấy byte-exact bằng `git show archive-2026-09`, SHA-256
  `5f3e6a01173bb82802a397b260251bc8098b7bbffdb8571966655fd071fca64f`; không seed.
- **Time-box raw:** không tìm thấy `rho_offered_long.csv` hoặc thư mục `aoi_v7_campaign` trên máy hiện tại; dừng,
  không suy tỉ lệ đuôi khi thiếu raw.
- **Kết quả:** `experiments/results/f01_operating_point_output.txt`; cả ba dự đoán đạt. CLEAN/PROD có
  `d=0,1181/0,0995 s`, `T_poll=W=H=0,5003 s`; CLEAN có TB răng cưa dự đoán `0,3682 s` so với đo `0,3689 s`.
  Anchor `(4 Mb/s,σ=0,03,τ=10 s)` cho `Π_noise=6,00`; cực đại tuổi tại 8 Mb/s là `1,142` ở `(0,10;2 s)`;
  tại 8 Mb/s chỉ `(ρ̄=0,95,τ∈{0,5;2 s})` có `Π_relax>1`.
- **Tải:** dt4n chỉ có tải tự sinh AR(1)/M/G/∞; `τ,σ` vẫn là giả định. Với M/G/∞,
  `R/σ²=L/(r_fW)` không phụ thuộc `C`; `σ=0,03` tại 4 Mb/s tương ứng khoảng `r_f=4 kb/s`, nên kết luận L1.2
  “gần như toàn nhiễu” là có điều kiện. X2 từ dt4n không khả thi; giữ phương án Pareto/MAWI cho GVHD.
- **Construct:** AoI asset là `t−t_m`, nên `z=AoI+W/2`; `txRate` là tải đi qua, còn definitions cần tải đề nghị.
- **Phạm vi:** F1 là spike định hướng, không claim RQ1/RQ2; các đề xuất K7/K8/K9/K20 chưa thành ADR (K23).

## 2026-09-26 — L1.5 · KHOÁ SESOI (trước mọi output F2)

- **Ứng dụng mục tiêu:** VoIP; ITU-T Y.1541 (12/2011) lớp 0 và E-model ITU-T G.107 (06/2015) §7.4 với lớp
  nhạy trễ mặc định (`sT=1`, `mT=100 ms`).
- **Sàn tuyệt đối:** `m=8,1 ms`. Đường chọn: E-model ở vùng nhạy nhất, với lựa chọn thiết kế bảo thủ
  `ΔR_min=1` điểm; `m=ΔR_min/max(dIdd/dTa)`. ITU cung cấp mô hình, không quy định `ΔR_min=1`. Quy đổi:
  `2,68 S @ 4 Mb/s`, `5,36 S @ 8 Mb/s`, `66,97 S @ 100 Mb/s` cho gói 1512 byte.
- **Sàn tương đối:** `r=10%`, là phán đoán thiết kế: thích nghi phải thu hồi ít nhất một phần mười headroom mới
  đáng chi phí tính `Ī,p−` mỗi epoch; không trình bày như ngưỡng ITU.
- **Quy tắc CI:** theo seed paired, `D_abs=gap−m`, `D_rel=gap−r·headroom`. “Có ý nghĩa” khi cả hai cận dưới
  CI95 lớn hơn 0; “không đáng kể” khi ít nhất một cận trên nhỏ hơn 0; còn lại là “chưa kết luận” và chỉ được thêm
  seed theo F3, không đổi `m,r`.
- **Ô chính DP0 (khóa trước F2):** P1 anchor gần nhất trong lưới: `4 Mb/s, K=11, ρ̄=0,85, σ=0,03, τ=10 s`,
  tuổi cố định tại trung bình CLEAN (`z_eff≈0,919 s`); P2 contrast cơ chế đã dự đoán: `4 Mb/s, K=100, ρ̄=0,95,
  σ=0,10, τ=2 s`, cùng tuổi. Các ô còn lại chỉ lập bản đồ mô tả và không quyết định DP0.
- **Báo phụ, không dùng quyết định:** `m/2=4,05 ms`, `2m=16,2 ms`; `r∈{5%;20%}`.
- **Kiểm trước khóa:** tại commit `fd26a99`, `git log --all` và tìm tên file đều không thấy `experiments/f02*`,
  `notes/feasibility/F2*` hoặc `experiments/results/f02*`.
- **Vấn đáp sở hữu:** chưa thực hiện trong phiên này; không ghi đạt thay tác giả.
- **Kiểm t04:** `experiments/results/t04_emodel_floor_output.txt`; độ dốc lớn nhất `0,1231 điểm R/ms` tại
  `Ta=241,5 ms`, suy ra `1/0,1231=8,1 ms` cho `ΔR_min=1`. Không seed; đây là kiểm lý thuyết, không phải F2.

## 2026-09-26 — L1.6 · TIỀN ĐĂNG KÝ F2 (trước khi chạy `--mode grid`)

- **Đã chạy trước đăng ký:** chỉ `--mode control` và `--mode check`; không có output lưới. Control cho gap đúng 0
  tại P1/P2. Ô check ngoài lưới xác nhận nested MC lệch trên quỹ đạo luật tĩnh do path hiện tại mang thông tin;
  oracle bin dọc cùng tham chiếu không lệch và hiệu chỉnh harm đúng.
- **Sửa thiết kế trước grid:** (1) tune luật tĩnh bằng trễ người dùng trải qua `J` trên quỹ đạo riêng, harm thực
  `≤α`, không tối đa gain decision-level; (2) oracle chính là bin dọc quỹ đạo tham chiếu. Nested MC chỉ dùng cho
  control/check và sau này chỉ được so khi cùng loại tham chiếu hoặc đã điều kiện hóa lịch sử.
- **Làm rõ ô chính, không đổi khóa:** P1 dự kiến không đáng kể vì K=11 chặn sojourn gần `33 ms`; P2 có
  `P(ρ>1)≈31%`, `Π_relax≈2,4`, nên PSA có thể phóng đại các burst quá tải. F2 tại P2 chỉ định hướng và phán quyết
  DP0 cần PSA-vs-DES ở L1.7.
- **Dự đoán nhóm ô:** mọi ô K=11 và mọi ô `ρ̄≤0,7` sẽ không đáng kể theo `m=8,1 ms`. Tín hiệu nếu có tập trung
  tại K=100, `ρ̄∈{0,85;0,95}`; bộ `(σ=0,10,τ=2 s)` có gap lớn hơn `(0,03;10 s)`, nơi nhiễu đếm che tín hiệu.
  P1: không đáng kể. P2: dự đoán có ý nghĩa trong surrogate nhưng chỉ là ứng viên GO chờ DES. Tắt nhiễu dự kiến
  làm gap tăng vì lộ khác biệt do tuổi; tắt tuổi dự kiến làm gap giảm. `self_gap_twin` dự kiến có Spearman tốt nhất
  vì gần trực tiếp estimand gap; `rd_score` thứ hai, `sd_log_s_cond` kém đặc hiệu hơn.
- **Tiêu chí:** GO định hướng nếu P2 có ý nghĩa và `frac_harm_possible≥2α`, sau đó DES xác nhận; NARROW nếu chỉ
  buffer sâu/gần bão hòa có tín hiệu; PIVOT “ngưỡng tĩnh đủ, và vì sao” nếu không ô nào có ý nghĩa.
- **Seed/config:** calibration 9701–9708; test 9711–9718; oracle 9801–9999; `N_EPOCH=1500`, bin `20×20`,
  `M_MC=128`. Đây là surrogate PSA định hướng, không phải claim RQ1/RQ2.
- **Dòng phương pháp K23:** quỹ đạo tham chiếu dùng luật tĩnh tune theo `J`; oracle bin học dọc chính quỹ đạo đó.
  Chú thích definitions “self_gap_twin đúng theo cấu trúc dưới M0” không áp dụng khi twin mô hình bỏ lịch sử chọn path.
- **Grid (chạy sau commit tiền đăng ký `e2de7aa`):** 16 ô hoàn tất trong 165 s. Không ô nào vượt `m=8,1 ms`;
  gap lớn nhất `0,957±0,736 ms` tại `K=100,ρ̄=0,95,σ=0,10,τ=2 s`. P1 base `−0,000±0,002 ms`, P2 base
  `+0,358±0,751 ms`; cả hai “KHÔNG ĐÁNG KỂ”. P2 `frac_harm_possible=0,586≥2α`, nên P2 trượt GO vì SESOI,
  không phải vì thiếu cơ hội harm.
- **Biến thể:** P2 age_only `1,413±0,594 ms`, noise_only `1,063±0,809 ms`, control 0; tất cả không đáng kể.
  Dự đoán bỏ tuổi làm gap giảm bị bác bỏ. Chỉ số Spearman: `self_gap_twin=0,665`, `sd_log_s_cond=0,524`,
  `rd_score=0,132`; dự đoán chỉ số chính đúng.
- **Sự cố phụ:** lần grid đầu có 6 `NaN` ở `rd_score` với `c=0,25S` do mảng hạng hằng; metric chính `c=0`
  không ảnh hưởng. Quy ước suy biến `rd_score=0`, chạy lại cùng seed; JSON cuối không có non-finite và gap không đổi.
- **Đề xuất sau F2:** PIVOT định hướng “ngưỡng tĩnh đủ trong miền surrogate”; chưa chốt DP0 cho tới khi L1.7 kiểm
  PSA-vs-DES tại P2. F2 là feasibility, không claim RQ1/RQ2.

## 2026-09-26 — f02b/f02c: chẩn đoán độ ổn định F2 (VALIDITY, post hoc; phán quyết F2 KHÔNG đổi)

- **Câu hỏi:** công cụ đo F2 có đủ độ phân giải cho các diễn giải ở F2 §4–§7 không? SESOI có đạt được ở từng ô không?
- **Loại:** chẩn đoán sau khi thấy kết quả; không có dự đoán mù; không đổi `m`, `r`, ô chính hoặc tiêu chí.
- **Seed/khoá:** tái dùng seed F2; khoá luồng 902 (tái lập gap `+0,358` trùng F2) và 950–953 (cùng seed, luồng mới).
- **f02b:** 18/24 ô/biến thể có trần chặt `<m`; 5/24 có trần xấp xỉ `<m`; 1/24 kiểm được
  (`K100_r0.95_s10t2`; cùng cấu hình ở luồng P2 thì trần xấp xỉ `7,156<m`). P2: thích nghi `0,358` | an toàn
  `6,798` | thông tin `26,983 ms`.
- **f02c:** khoảng 3% epoch bất đồng; đóng góp TB `+12,3`, sd `153,5 ms`; 5 luồng cùng cấu hình cho gap
  `−0,274…+0,768 ms`; họ tĩnh nhảy `abs/rel` giữa luồng. CRN: `age_only−base=+0,147±0,546`;
  `noise_only−base=+0,182±0,937 ms`.
- **Diễn giải:** phán quyết SESOI tại P1/P2 vững; so sánh tinh (biến thể, xếp hạng ô, H2) không phân giải được.
  H2(b) và dự đoán “K=11 không đáng kể” không bác bỏ được dưới `m=8,1 ms` ở 4 Mb/s.
- **Provenance:** mã được cung cấp trong tài liệu hướng dẫn do AI soạn; Codex tích hợp nguyên mẫu, chạy lại và lưu
  output. Không ghi thay rằng tác giả đã tự viết hoặc tự kiểm từng dòng.

## 2026-09-26 — L1.7 · f04: số đếm có phải nhiễu? PSA vs DES tại P2 (một link)

- **Không mù:** output đã xuất hiện trong tài liệu hướng dẫn trước khi ghi mục này.
- **Seed:** 9721–9724; `4×1500 s`; 11.824 epoch. R² ngoài mẫu (fit 2 seed, chấm 2 seed).
- **Kết quả:** `R²(D|m)=0,583`; `R²(D|ρ̂)=0,445`; `R²(D|V)=0,827`; `corr(ρ̂−m,D−E[D|m])=+0,191`;
  `corr(DES,PSA)=0,607`; `R²(D|ρ̂)` DES `0,445` so với PSA `0,236`; DES−PSA `+19,3/+13,2/−76,7 ms`.
- **Diễn giải:** tại P2, PSA không dùng được để kết luận; nhiễu đếm mang một phần tín hiệu hàng đợi. Kết luận F2
  tại P2 phải được kiểm lại bằng DES hai path (L1.7 bước 2).
- **Provenance:** mã được cung cấp trong tài liệu hướng dẫn do AI soạn; Codex tích hợp, chạy và lưu output; đây là
  spike định hướng, không phải `e00` hay kết quả RQ.

## 2026-09-27 — L1.7 · f04b TIỀN ĐĂNG KÝ: gap và phân rã ba khoảng trong DES, ghép cặp với PSA (TRƯỚC outcome)

- **Đã chạy trước khi ghi:** `f04_benchmark`; `f04b --mode validity` (chỉ phép kiểm công cụ). Chưa chạy
  `--mode power` hoặc `--mode outcome`; chưa tồn tại `f04b_results.json`. Output `f04` một link đã biết trước,
  nên Q1–Q2 là dự đoán có thông tin, không phải mù hoàn toàn.
- **Ô và lý do chọn:** P1 (neo đã khoá), P2 (tương phản đã khoá), `K100_r0.85_s10t2`,
  `K100_r0.95_s03t10` — chọn theo trần chặt surrogate `≥m` trong f02b, không theo gap.
- **Seed:** như F2 (calibration 9701–9708, test 9711–9718, oracle 9801–9999), khoá luồng 710–713;
  benchmark 9731–9740.
- **Validity trước outcome:** engine Numba trùng bit với Python và khớp `mdk.py`; mọi nhãn xác định, tải không bị
  kẹp, `Î` giống hệt giữa DES/PSA, oracle không có ô thưa. Bin `K100_r0.85_s10t2` DES thấp nhất có
  `0,067→0,120`, nhưng `n=50`, `SE=0,046`, nên độ lệch `0,053<2SE=0,092`: chưa đủ bằng chứng lệch reliability.
- **Dự đoán do Codex soạn theo ủy quyền của tác giả, trước outcome, dựa trên f04 và T1–T3:**
  - **Q1:** tại P2, headroom DES **nhỏ hơn** PSA. PSA phản ứng tức thì với burst và tạo chênh lệch path cực đoan;
    workload DES có quán tính nên làm trơn các cực trị trong khoảng giữ.
  - **Q2:** khoảng thông tin `headroom−K2(∞)` của DES **nhỏ hơn** PSA. Trong f04, số đếm dự báo DES tốt hơn PSA
    (`R²=0,445` so với `0,236`) vì phần dư đếm mang tín hiệu về workload.
  - **Q3:** gap thích nghi DES tại P2 thuộc khoảng **1–4 ms**. Trí nhớ hàng đợi tạo dị phương sai/trạng thái mà
    ngưỡng một chiều bỏ lỡ, nên dự kiến lớn hơn mức dưới 1 ms của surrogate nhưng vẫn thấp hơn SESOI `8,1 ms`.
  - **Q4:** dự đoán **0 ô K=100** có phán quyết “CÓ Ý NGHĨA”; DES có thể tăng gap nhưng chưa đủ vượt đồng thời
    sàn tuyệt đối và `10%` headroom với chỉ 8 seed test.
  - **Q5:** **có**, P1 trong DES vẫn không thể đạt `m`: buffer nông, dao động tải nhỏ và telemetry gần như chỉ
    cung cấp một thứ tự một chiều, nên headroom khả dụng dự kiến vẫn dưới `8,1 ms`.
- **Luật quyết định (khoá trước outcome):**
  1. Ít nhất một ô K=100 “CÓ Ý NGHĨA” trong DES → đề xuất NARROW có tín hiệu: RQ1 thu về vùng `K·S≫m`, chỉ dùng DES.
  2. Không ô nào có ý nghĩa nhưng ít nhất một ô “CHƯA KẾT LUẬN” → thêm seed theo `--mode power`, không đổi `m`,
     `r` hoặc ô.
  3. Mọi ô “KHÔNG ĐÁNG KỂ” → đề xuất PIVOT “ngưỡng tĩnh đủ, và vì sao”; phần “vì sao” là bảng phân rã DES.
  4. Bất kể kết quả: khoảng nào có DES−PSA với CI loại trừ 0 → ghi vào F2 rằng PSA không dùng làm bằng chứng cho
     khoảng đó.
- **Provenance:** phần dự đoán này do Codex soạn theo yêu cầu thực hiện thay của tác giả; không trình bày là bài
  tự viết của tác giả. Quyền sở hữu lý thuyết/vấn đáp vẫn cần tác giả tự luyện riêng.

## 2026-09-27 — L1.7 · f04b MỞ NIÊM PHONG: power và outcome DES-vs-PSA

- **Thứ tự:** validity/reliability commit `7a3e190`; prereg commit `cdcea06`; chỉ sau đó mới chạy `--mode power`
  và `--mode outcome`. Output và JSON đều hữu hạn; seed/config giữ nguyên prereg.
- **Power:** mọi ô cần 3 seed để phân giải ±`m/2=4,05 ms`; đích ±1 ms cần nhiều nhất 5 seed (P2 PSA), nên 8 seed
  hiện có đủ cho quyết định SESOI. ACF đóng góp gap nhỏ (`−0,037…+0,102`), trong khi ACF `(I)⁺` tới `0,866`.
- **Outcome:** cả bốn ô, ở cả DES và PSA, đều “KHÔNG ĐÁNG KỂ”. Gap DES: P1 `−0,010±0,016`; P2
  `+0,149±0,400`; K100/0,85/0,10/2 `+0,215±0,140`; K100/0,95/0,03/10 `+0,082±0,163 ms`.
- **Đối chiếu Q1–Q5:** Q1 đúng (`headroom` P2 DES `14,556<37,699` PSA); Q2 đúng (thông tin
  `9,418<24,348 ms`); Q3 sai (dự đoán 1–4 ms, quan sát `0,149±0,400`); Q4 đúng (0 ô K100 có ý nghĩa);
  Q5 đúng (P1 có trần `headroom−gain_tĩnh=1,488<m`).
- **Quyết định khóa:** áp luật 3 → đề xuất **PIVOT “ngưỡng tĩnh đủ, và vì sao”**; không thêm seed. Áp luật 4:
  PSA không làm bằng chứng định lượng cho các khoảng có hiệu DES−PSA loại trừ 0; chi tiết ở `F3_F4_budget.md`.
- **Provenance:** Codex chạy và diễn giải theo ủy quyền; không ghi thay rằng tác giả tự làm dự đoán hoặc phép tính.

## 2026-09-27 — L1.8 · f05 TIỀN ĐĂNG KÝ: độ mạnh oracle và tuổi dao động (TRƯỚC outcome)

- **Đã chạy trước khi ghi:** `f05 --mode validity`; ba phép kiểm neo đều `True` ở cả hai ô. Chưa chạy
  `--mode outcome`; chưa tồn tại `f05_results.json` hoặc output outcome.
- **Ô và lý do:** P2 và `K100_r0.95_s03t10`, hai ô có trần chặt DES lớn hơn `m` trong f04b, lần lượt khoảng
  `10,86` và `10,09 ms`.
- **Seed:** như F2; khoá luồng 711/713 cho A0 và thế giới A1 ghép cặp; lô oracle thứ hai dùng 811/813; tuổi dùng
  `SeedSequence([seed, khoá, 99])`.
- **Bài tính trước outcome:** với τ=10 s, A1 có `z_eff∈[0,67;1,17) s`, nên `exp(−z_eff/τ)` chạy từ khoảng
  `0,890` đến `0,935`; A0 có `z_eff=0,92 s`, cho khoảng `0,912`.
- **Dự đoán do Codex soạn theo ủy quyền, trước outcome:**
  - **Q1:** tại A0, `max |gap−gap_F20|` qua F10/F20x2/F40x2 dưới `0,5 ms`, nên đạt tiêu chí DP0 `<m/2`.
    Tiêu chí `4,05 ms` khá yếu so với gap đã quan sát dưới 1 ms, nên vẫn phải báo độ phân tán thực tế.
  - **Q2:** với F20x2, `SC−S0` lớn hơn về trị tuyệt đối so với `K2−SC`; phần thuần dương nhưng gần 0. Cơ chế
    chính dự kiến là sửa tâm điều kiện, không phải dùng độ rộng khác nhau theo epoch.
  - **Q3:** Q20x2 cho `K2(∞)−S0` lớn hơn oracle đếm vì workload dự báo delay tốt hơn, nhưng không ô nào đạt
    “CÓ Ý NGHĨA” với K2 có ràng buộc; nếu có tín hiệu thì đó là giá trị telemetry hàng đợi, không phải RQ1 hiện tại.
  - **Q4:** jitter làm gap F20x2 A1−A0 dương nhưng nhỏ hơn `1 ms`, và lớn hơn tại P2 vì τ=2 s khiến tương quan
    thay đổi mạnh hơn; với τ=10 s, tương quan chỉ chạy khoảng `0,890–0,935` quanh A0 `0,912`.
  - **Q5:** ở A1, oracle FZ làm phần thuần lớn hơn F20x2 vì tuổi giải thích độ rộng điều kiện; mức tăng dự kiến
    rõ hơn tại P2 nhưng vẫn không đủ vượt SESOI.
- **Luật quyết định (khóa trước outcome):**
  1. Mọi tổ hợp ô/chế độ tuổi/oracle đếm F hoặc FZ đều “KHÔNG ĐÁNG KỂ” → PIVOT vững trong phạm vi đã thử.
  2. Có oracle đếm “CÓ Ý NGHĨA” → chưa được PIVOT; DP0 NARROW về đúng điều kiện đó.
  3. Có oracle đếm “CHƯA KẾT LUẬN” → thêm seed test theo power, không đổi `m`, `r`, ô hoặc oracle.
  4. Chỉ Q20x2 “CÓ Ý NGHĨA” → ghi telemetry hàng đợi là hướng ứng viên, không gọi là kết quả RQ1; cần literature.
  5. Luôn báo tỉ lệ tâm/thuần ở F20x2 A0 và FZ A1. Nếu `|thuần|<|tâm|` mọi nơi, cơ chế PIVOT là cần sửa tâm,
     không phải dùng độ rộng.
- **Provenance:** tác giả nói đã tự tính ngoài repository nhưng không cung cấp giá trị hay dự đoán nguyên văn;
  các con số và Q1–Q5 ghi tại đây do Codex soạn theo yêu cầu thực hiện thay. Không ghi đây là dự đoán tự viết của tác giả.

## 2026-09-27 — L1.8 · f05 MỞ NIÊM PHONG: oracle adequacy, tâm/thuần và tuổi dao động

- **Thứ tự:** validity commit `1b84fa2`; prereg commit `9056ac1`; outcome chạy sau prereg. JSON có 16 khóa và
  mọi số hữu hạn; seed, ô, oracle và luật quyết định giữ nguyên.
- **Ổn định oracle:** `max|gap−gap_F20|` là `0,315 ms` tại P2 và `0,183 ms` tại ô τ=10 s, đạt tiêu chí DP0
  `<m/2=4,05 ms`. Mọi oracle F/FZ ở A0/A1 đều “KHÔNG ĐÁNG KỂ”.
- **Tuổi:** A1−A0 của gap F20x2 là `+0,425±0,317 ms` ở P2 và `−0,202±0,191 ms` ở ô τ=10 s; jitter không làm
  kết luận đổi. FZ không tăng phần thuần nhất quán theo độ mịn bin.
- **Telemetry Q:** Q20x2 cho gap `4,125±1,206` và `3,458±1,741 ms`, vẫn không đáng kể; đây là kênh thông tin
  khác, không phải cận trên chứa F và không phải kết quả RQ1.
- **Tâm/thuần:** tại A0/F20x2 là `0,048|0,086 ms` ở P2 và `0,099|0,000 ms` ở ô τ=10 s. Qua mọi FZ, phần thuần
  chỉ từ `−0,122` tới `+0,154 ms`; không có giá trị thực dụng so với `m=8,1 ms`.
- **Đối chiếu prereg:** Q1 và Q3 đúng; Q2 sai một phần; Q4 đúng một phần; Q5 không được ủng hộ nhất quán.
- **Quyết định:** luật 1 kích hoạt → **PIVOT vững trong phạm vi đã thử**. Luật 2–4 không kích hoạt; điều kiện luật
  5 không đúng tuyệt đối tại P2/A0 nhưng kết luận cơ chế vẫn là phần thuần gần 0, không phải nguồn lợi ích thực dụng.
- **Provenance:** outcome và diễn giải do Codex thực hiện theo ủy quyền; không ghi là phần tác giả tự viết.
