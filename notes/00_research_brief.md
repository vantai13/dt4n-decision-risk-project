# Research brief — v2 (2026-09-25)

> Bản nháp do Claude (AI) soạn ngày 2026-09-25 theo yêu cầu tác giả; tác giả kiểm từng mục trước khi dùng
> làm căn cứ. Thay đổi so với v1 (`notes/archive/v1_trust_gate/00_research_brief.md`): đơn vị quyết định là
> đổi/giữ; câu hỏi "khi nào ngưỡng tĩnh là đủ"; H2 dùng mức đảo thứ tự; RQ2 lấy sai mô hình làm trục chính.
> Lý do: `02_decision_log.md` (PIVOT-v14, K17, K22). Thuật ngữ: `06_definitions.md` (v2).

## 1. Problem

Một luồng nhỏ nhạy độ trễ đang đi trên đường A. Network Digital Twin nhìn mạng qua telemetry đã cũ
(đếm gói theo cửa sổ, có tuổi và nhiễu) và dự đoán đường B tốt hơn Î ms. Vận hành thường quyết định
đổi/giữ bằng một ngưỡng tĩnh (hysteresis, dampening) tune một lần; ngưỡng đó có thể quá thận trọng ở
quyết định ít bất định và quá liều ở quyết định nhiều bất định. Chưa rõ khi nào cái giá này đáng kể.

## 2. Gap — mức: strong candidate

- Seshadri–Katz 2003: ngưỡng H phù hợp thay đổi GIỮA các cấu hình; đề xuất H động kiểu MIMD; không so
  với oracle. [chưa có note, chưa đọc full text]
- Liyanage et al. 2026 (arXiv 2604.21483): μ+kσ kèm hysteresis Δ, N cố định; adaptive tuning nằm ngoài
  phạm vi. [chỉ qua báo cáo AI, chưa tự đọc]
- OpenTwin v2, CERT: bất định hiệu chỉnh từ dữ liệu (conformal) cho cổng/chứng nhận; không so với bất định
  lan truyền qua mô hình dưới dịch chuyển. [OpenTwin: full text, D17; CERT: §1–7, note L1.2]
- Fischer–Vöcking 2005/2009: vòng kín, hội tụ quần thể, không phải tỉ lệ lỗi từng quyết định. [chưa có note]
→ Chưa thấy công trình đo khoảng cách giữa ngưỡng tĩnh tốt nhất và oracle cùng thông tin cho quyết định
đổi/giữ dưới telemetry cũ, theo cơ chế hàng đợi và telemetry. Chốt ở DP1 (tiêu chí DP1-v2).

## 3. Thesis

Twin có nên thay ngưỡng tĩnh bằng quyết định theo từng lần hay không phụ thuộc vào việc bất định có đảo thứ tự
các quyết định so với cải thiện dự đoán; mức đảo thứ tự đó do cơ chế hàng đợi và telemetry của chính mạng
quyết định và ước lượng được từ output của twin.

## 4. Mục tiêu tối ưu — ĐỀ XUẤT, chờ GVHD (ADR K2, K3, K21; L0.3)

Tối thiểu hoá tỉ lệ missed improvement (giữ khi I_D > ε) cộng κ × tỉ lệ đổi (κ = 0,01), với ràng buộc tỉ lệ
harmful switch (đổi khi I_D < −ε) ≤ α; cả ba chia cho MỌI epoch quyết định. Mọi luật hiệu chỉnh bằng cùng tiêu chí;
luật xác suất dùng λ ≥ 0 nhỏ nhất đạt harm ≤ α (không tiêu hết ngân sách khi ràng buộc lỏng). Loss là nhãn riêng,
δ = 1 điểm % (K3). Mặc định phân tích: α = 1%, ε/S = 0,5; báo thêm α ∈ {0,5; 2}%, ε/S ∈ {0,25; 1; 2},
ε ∈ {0,5; 1; 2; 5; 10} ms, κ = 0. Nếu GVHD chọn delay kỳ vọng: RQ2 chuyển trọng tâm sang sửa tâm E[I_D | F].

## 5. Research questions

| RQ | Câu hỏi | Loại | Bằng chứng |
|---|---|---|---|
| RQ1 | Khoảng cách theo tiêu chí K2 (missed + κ·đổi) tại α giữa ngưỡng tĩnh tốt nhất (họ tuyệt đối + tương đối, tune từng ô) và oracle một bước cùng thông tin lớn đến đâu; thay đổi thế nào theo độ sâu buffer (tính theo S), độ gần knee, burstiness, jitter tuổi, nhiễu đếm? | characterization + mechanism | Quét có kiểm soát + OFAT; decision-level; CI paired theo seed |
| RQ1-op | Chỉ số đảo thứ tự tính từ output twin có dự báo được khoảng cách trước khi chạy oracle không? | characterization vận hành | Tương quan hạng chỉ số–khoảng cách qua các ô; chỉ số khoá ở DP0 |
| RQ2 | Ở ô có khoảng cách ≥ SESOI, luật posterior-odds dùng bất định lan truyền qua twin chịu được bao nhiêu sai mô hình và dịch chuyển chế độ (ngưỡng đóng băng) trước khi vượt α hoặc mất lợi thế so với luật học từ dữ liệu và luật lai? | comparative + robustness | Baseline tune công bằng; knowledge parity; ≥ 1 thực tế ngoài họ mô hình |

## 6. Hypotheses — số là dự thảo, khoá ở DP0 / prereg (sau F3)

SESOI_claim: khoảng cách ≥ max(0,5 điểm %; 20% × J của ngưỡng tĩnh). SESOI_DP0: ≥ 2 điểm % HOẶC ≥ 20%.
"Vượt ngân sách": cận dưới CI95 của harm thực tế > 1,25α; "giữ ngân sách": cận trên ≤ 1,25α.

- **H1 (đối chứng):** Thế giới tuyến tính–Gaussian với s không đổi → |khoảng cách| ≤ 2 SE Monte Carlo, cả ở
  surrogate lẫn pipeline thật (e01). Vi phạm = lỗi triển khai, không phải phát hiện.
- **H2 (cơ chế + RQ1-op):** (a) Qua ≥ 16 ô, Spearman(chỉ số đảo thứ tự bản oracle, khoảng cách) ≥ 0,6.
  Bác bỏ nếu cận trên CI95 (bootstrap theo ô) < 0,3. (b) Ô dự đoán "ngưỡng tĩnh đủ" (K = 11, tuổi cố định,
  ρ̄ ≤ 0,7) có khoảng cách < SESOI_claim. Bác bỏ nếu cận dưới CI95 của một ô như vậy > SESOI_claim.
  (c) Spearman(bản twin, bản oracle) ≥ 0,8. Bác bỏ nếu cận trên CI95 < 0,5.
- **H3 (phương pháp + độ bền):** (a) Ở ô khoảng cách ≥ SESOI_claim: G ≥ 0,7 dưới M0 (verification, không
  claim); G ≥ 0,5 dưới M1 (twin sai K). Bác bỏ (M1) nếu cận trên CI95 của G < 0,5. (b) Dịch chuyển với η đóng
  băng: luật lai giữ ngân sách ở mọi cặp chế độ đã đăng ký; twin thuần vượt ngân sách ở ≥ 1 thực tế ngoài họ.
  Bác bỏ vế đầu nếu luật lai vượt ở ≥ 1 cặp; vế sau nếu twin thuần giữ ngân sách ở mọi thực tế ngoài họ.

## 7. Candidate contributions — cần literature xác nhận ở DP1

(a) Empirical finding: bản đồ khoảng cách ngưỡng tĩnh–oracle kèm cơ chế mạng. (b) Chỉ số đảo thứ tự tính được
từ output twin (RQ1-op). (c) Empirical finding: độ bền của bất định lan truyền qua mô hình, hiệu chỉnh từ dữ liệu
và luật lai dưới dịch chuyển/sai mô hình. (d) Phụ: giao thức đánh giá (oracle cùng thông tin, decision-level,
knowledge parity).

## 8. Không claim

Stale state làm routing lỗi (Shaikh 2001; Mitzenmacher 2000) · diễn giải tải theo tuổi (Dahlin 2000; CERT) ·
hysteresis và hysteresis thích nghi (RON 2001; Seshadri–Katz 2003; handover MRO; SD-WAN dampening) · lý thuyết
hysteresis dưới bất định (Dixit 1989) · chống dao động do thông tin cũ (Khanna–Zinky 1989; Fischer–Vöcking) ·
μ+kσ kèm hysteresis cố định (Liyanage 2026) · fallback theo độ tin cậy của twin (OpenTwin; Almohammedi 2026) ·
conformal gate, risk trên ACCEPT, risk theo action được chọn (OpenTwin; CERT; LEC; Zhu 2026) · tối ưu của luật
posterior-odds (Neyman–Pearson; Lekeufack 2024) · probabilistic twin (Kapteyn et al. 2021) · "tổng quát cho mọi mạng".

## 9. Assumptions · Limitations · Scope

- **Assumptions:** tải nền ngoại sinh; luồng điều khiển là probe ảo không chiếm tải; telemetry = đếm gói trên
  link theo cửa sổ W, có tuổi z; tải OU một thang thời gian; oracle một bước; hai path rời, mỗi path một link nghẽn.
- **Limitations:** bằng chứng chính là DES; testbed Mininet là HTB token bucket (≠ M/D/1/K), 4–8 Mb/s; tham số OU
  phải neo bằng dữ liệu (F1); tốc độ link đổi nguồn bất định chiếm ưu thế (Π_noise); pilot hiện có là exploratory.
- **Scope (không làm):** vòng kín, hiệu ứng bầy đàn; nhiều luồng lớn; TE toàn mạng; telemetry probe-delay kiểu SD-WAN;
  gộp loss vào một utility.
- **Ứng dụng khớp giả định:** quyết định cho từng luồng thời gian thực nhỏ (VoIP, control traffic), kiểu chọn relay cho
  từng cuộc gọi; không phải steer cả một lớp ứng dụng.

## 10. Kill criteria ↔ điểm quyết định

| DP | Khi nào | GO nếu | Nếu không |
|---|---|---|---|
| DP0 | 13/10/2026 | ≥ 1 ô gần điểm neo F1 có khoảng cách ≥ SESOI_DP0 (α = 1%, ε/S = 0,5) và P(I_D < −ε) ≥ 2α; lưới lõi ≤ 3 CPU-ngày; hai cách tính oracle chênh < SESOI_DP0/2 | NARROW nếu chỉ đạt ở K = 100 hoặc cửa sổ dài; PIVOT sang "ngưỡng tĩnh đủ, và vì sao", RQ2 rút gọn |
| DP1 | 20/10/2026 | Tiêu chí DP1-v2 (khung D18) đạt PASS | NARROW/PIVOT theo D18; so trực tiếp với bài trùng |
| DP2 | 01/12/2026 | Có ô khoảng cách ≥ SESOI_claim | Kết luận chính "ngưỡng tĩnh đủ trong phạm vi đã kiểm"; RQ2 thành kiểm phụ; không đổi metric |
| DP3 | 15/12/2026 | Kết quả RQ2 báo được theo prereg | Twin vượt α khi dịch chuyển → báo như phát hiện về giới hạn |

## 11. Phép thử ngược · Câu hỏi mở · Elevator test

- **Nếu RQ1 cho khoảng cách < SESOI ở mọi nơi:** báo "ngưỡng tĩnh (tuyệt đối/tương đối) đủ trong phạm vi đã kiểm,
  vì mức đảo thứ tự thấp", kèm chỉ số RQ1-op để người vận hành biết khi nào không cần twin xác suất.
- **Nếu RQ2 cho twin thuần vượt α, luật lai giữ:** "mô hình cho hình dạng bất định, dữ liệu cho thang đo".
  Nếu cả hai giữ: "mô hình twin đủ tốt trong các thực tế đã thử". Nếu cả hai vượt: giới hạn của hiệu chỉnh online.
- **Câu hỏi mở:** K2 (mục tiêu, GVHD); K21 (lần đổi vô ích); điểm neo tốc độ link (F1); vai trò Mininet (K14/K20);
  pilot v14 rút s độc lập với I nên có thể phóng đại hiệu ứng so với mạng.
- **Elevator test (kịch bản):** "Khi mạng chọn đường cho một cuộc gọi, nó dựa vào số đo đã cũ vài giây. Người ta thường
  đặt luật đơn giản: chỉ đổi đường nếu đường mới tốt hơn ít nhất X mili giây hoặc X phần trăm. Em hỏi: khi nào luật
  đơn giản đó đã đủ, và khi nào nên tính riêng cho từng lần đổi, vì có lần số đo cũ vẫn đáng tin, có lần không. Em dùng
  mô phỏng để đo luật đơn giản thua cách tốt nhất có thể bao nhiêu, ở loại mạng nào."
  **Kết quả:** chưa làm (cần một người thật nhắc lại câu hỏi; không điền thay).
