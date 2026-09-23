# Research brief — v1 (2026-09-23)

Agent soạn theo yêu cầu người dùng; đã được Claude (AI) review theo D14–D15,
nhưng chưa được GVHD người thật xác nhận. So với v0
(`119b5ee`): tách RQ1a/b, validity khỏi hypothesis; thêm baseline forecast+Gaussian.
Lịch sử quyết định: `02_decision_log.md`.
Thay đổi so với v1 (2026-09-23, D15): D5 có điều kiện định lượng; RQ1b thu gọn.

## 1. Problem
Controller chọn đường bằng telemetry cũ có thể chọn sai, nhưng không phải mọi
lần chọn sai đều gây thiệt hại đáng kể. Cần biết khi nào nên tin quyết định và
khi nào nên từ chối, dựa trên thông tin có sẵn trước hành động.

## 2. Gap — potential
Các nhận định sau dựa trên workbook nội bộ, chưa xác minh full text mới:
routing dưới state cũ/bất định đã có ở Shaikh và Guérin–Orda (Novelty Matrix,
dòng 5,9); age × margin × harmful routing risk là khoảng trống cần kiểm.
Conformal cho quyết định đã có ở Kiyani/Zhu (dòng 13–14), nên không claim nền
tảng guarantee mới. OpenTwin gần nhất (dòng 8); khác biệt về conditioning theo
age vẫn là suy luận theo workbook, cần đọc §VI trước DP1.

## 3. Thesis
Độ đáng tin của quyết định phụ thuộc cả tuổi thông tin, khoảng cách chi phí
và mức regret chấp nhận được, chứ không chỉ sai số state.

## 4. Research questions
- RQ1a — characterization/mechanism: operational Gaussian law lệch calibration
  bao nhiêu khi W hữu hạn, cost phi tuyến, traffic heavy-tail, model sai?
  Evidence: fixed two-path OFAT và factorial nhỏ e02–e05.
- RQ1b — generalization: kết luận giữ thế nào qua Abilene/GÉANT, OD, K={2,3}
  và tuổi A1? Evidence chính: e06 thu gọn, báo cáo từng context và contender_rate;
  tách pair/global risk. K=5 và trace T3 là mở rộng nếu còn thời gian.
- RQ2 — comparative: gate C2 có tăng coverage tại cùng selective harmful risk
  so với forecast-to-now + Gaussian gate và các baseline đã định?
  Evidence: paired seeds/CRN, calibration budget bằng nhau, regime luật lệch.
- RQ3 ngoài paper 1: closed-loop routing làm thay đổi tải cần bài toán riêng.

## 5. Validity
Oracle Gaussian, affine cost, cặp cố định phải phù hợp xác suất Gaussian;
Sheppard kiểm khi mean margin=0. Kiểm Monte Carlo theo run, không đòi mọi CI
pointwise đồng thời phủ. Operational fit hữu hạn mẫu không phải định lý exact.

## 6. Hypotheses và ngưỡng thiết kế
- H0-approx: naive dưới zero-mean OU đánh giá thấp risk; là đối chứng lý thuyết
  đã xem Monte Carlo, không claim confirmatory mới.
- H1-break: W ngắn làm ratio biến động hơn; D0/heavy-tail dự đoán có vùng
  underprediction ở risk thấp, nhưng không đoán cùng hướng ở mọi margin.
  Mismatch có thể lệch hai hướng theo bias. Link chung triệt tiêu trong cặp cố
  định, không là cơ chế phá luật. Effect đáng kể: ratio ngoài [0,8;1,2],
  CI theo run đủ precision; ±20% là SESOI thiết kế. Không thấy vùng như vậy
  trên grid khóa trước với CI nằm trong band thì bác bỏ phiên bản “vỡ đáng kể
  trên grid”; thiếu events thì chưa kết luận. Contrast cụ thể đăng ký trước batch.
- H2: coverage tăng ≥5 điểm phần trăm so baseline mạnh tại selective harmful
  risk≤1%, ε=2 ms. Bác bỏ effect-size nếu upper CI paired dưới +5 điểm; upper
  CI risk vượt 1% thì chưa đủ bằng chứng đạt budget. 5 điểm là SESOI coverage,
  không phải kết quả mong đợi; chốt protocol threshold ở L5.1 trước test.

## 7. Candidate contributions
Research: bản đồ giới hạn operational law và evaluation gate harmful-aware
trước baseline mạnh. Cả hai cần literature xác nhận. “State error không đồng
nghĩa decision error” là framing, không contribution độc lập.

## 8. Không claim
Theo Novelty Matrix hiện tại (mức đọc full text giữ nguyên trong workbook):
- Stale state gây routing lỗi là mới — Shaikh, Levin (dòng 5,12).
- Routing xét bất định là mới — Guérin–Orda (9).
- Age chưa đủ mô tả task performance là mới — Shisher (6).
- Conformal cho quyết định được chọn là mới — Kiyani, Zhu (13–14).
- Conformal gate cho NDT là đầu tiên — OpenTwin (8).
- Metric freshness cho DT là mới — AoT/AoS/EAP (17,21).

## 9. Assumptions · Limitations · Scope
Assumptions: exogenous traffic được review AI chấp thuận có điều kiện
f≤0,1σ capacity (D15); additive delay; tuổi chung; labels
calibration chỉ dùng sau khi nhận. Limitations: D1 176 dòng, dải link hẹp,
SE/nội suy khác sự thật vật lý; bằng chứng chính là simulation; 10 run còn ít
cho rare events. Điều kiện f phải được kiểm trong mọi config có controlled flow;
closed-loop feedback và route flapping thuộc RQ3. Scope: instantaneous routing
decision; không claim SLA ứng dụng, universal temporal guarantee hoặc closed-loop TE.

## 10. Kill criteria và checkpoint dự kiến
DP1: nếu không còn ≥1 điểm khác biệt kiểm được sau đọc các full text gần nhất,
thu hẹp/đổi câu hỏi trước mở rộng code. DP2: nếu cả e02–e05 nằm band calibration
±20% với precision đủ, chuyển trọng tâm sang analytic sufficiency.
DP3: nếu upper CI coverage gain dưới +5 điểm ở các contrast đăng ký, bỏ claim
gate cải thiện thực dụng. DP4: nếu direction đảo giữa contexts, bỏ claim transfer
chung, báo cáo phạm vi. Đây là mapping đề xuất, chưa đối chiếu plan riêng tư.

## 11. Còn mở
GVHD người thật chưa xác nhận D5/ε; full-text novelty; fallback và protocol nhãn thực;
chi phí trace/history. Elevator test với người ngoài ngành: chưa thực hiện.
W_ref đã sửa theo D12 để κ_ref=0,5 trong D_lin; κ realized dưới D0/D1/clipping
và phân phối κ ở e06 phải được đo, không giả định đã giữ nguyên.
Mọi thuật ngữ và đại lượng: xem `notes/06_definitions.md`.
