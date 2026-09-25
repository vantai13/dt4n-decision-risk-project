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
