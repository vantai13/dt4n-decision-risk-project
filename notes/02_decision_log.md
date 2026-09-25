# Decision log

| Ngày | Quyết định | Lý do | Thay thế đã cân nhắc |
|---|---|---|---|
| 2026-09-23 | Tách sang repo mới; repo dt4n archive tại `70d0e635b818` | Lõi khoa học ~1.2k dòng bị chìm trong ~150k dòng quy trình | Dọn dẹp tại chỗ (rủi ro kéo theo nợ cũ) |
| 2026-09-23 | Simulation là evidence chính; Mininet chỉ để validation | Thí nghiệm nhân quả cần biết ground truth và vặn tham số độc lập | Tiếp tục ép Mininet sinh tải có kiểm soát (S19–S25) |
| 2026-09-23 | ĐÍNH CHÍNH dòng 2026-09-23 ("repo dt4n archive tại `70d0e635b818`"): khi đó CHƯA archive. `70d0e635` là commit nguồn của snapshot, không phải điểm archive. Tag local `archive-2026-09` đã chuẩn bị tại commit `d45cf4ff26d8c6204a181f0fa77887e087a4d381`; push còn chờ xác thực GitHub. | Ghi chép đi trước thực tế (F0-1) | — |
| 2026-09-23 | Lấy lại `reference/` từ tag local `archive-2026-09` (5/10 file đổi). Dữ liệu giữ nguyên, checksum trùng tag. | Snapshot cũ lấy từ commit chậm 243 commit so với GitHub; con số "55" trước đó được tính trên `origin/main` chưa fetch (F0-2) | Giữ snapshot `70d0e635` (bỏ lỡ các sửa lỗi DEFAULT_TAU, perfect-twin, số block conformal) |
| 2026-09-23 | Tên repo chính thức hiện tại: `dt4n-decision-risk-project`; remote `https://github.com/vantai13/dt4n-decision-risk-project.git` | Giữ tên đang tồn tại trên GitHub vì máy hiện tại không có xác thực để rename; đồng bộ tiêu đề README với remote (F0-4) | Đổi thành `ndt-decision-risk` khi có xác thực GitHub |
| 2026-09-23 | Novelty matrix đổi tên thành `novelty_matrix.xlsx`; test kiểm cấu trúc thay cho checksum | Tài liệu sống không khóa checksum; test cũ báo sai khi file được lưu bằng Excel | Giữ checksum (phải sửa hash sau mỗi lần cập nhật) |
| 2026-09-23 | Kiểm kê trước archive: laptop có 489 thay đổi/file được đưa vào commit `d387f4df6` trên nhánh local `wip-before-archive`; stash được neo tại nhánh local `wip-stash-before-archive`. VM `dt4n-research-01` không kiểm được vì máy hiện tại chưa đăng nhập `gcloud`. | Chain of custody ghi đúng phần đã kiểm; hai nhánh và tag còn chờ push do thiếu xác thực GitHub | — |
| 2026-09-23 | Hạ tầng: mọi phase chạy trên máy cá nhân; chỉ L6.3 (`e12`, Mininet) cần server; VM GCP stop sau khi kiểm | Tầng A/B chỉ cần NumPy; chi phí server đáng kể với sinh viên | Giữ VM chạy suốt đồ án |
| 2026-09-23 | Đã push tag `archive-2026-09`, README archive và `wip-stash-before-archive`; `wip-before-archive` được backup bằng git bundle đã verify, có bản off-machine trên Google Drive nhưng chưa push vì token thiếu scope `workflow` | Không ghi “đã push 2 nhánh” khi GitHub chỉ nhận một; bundle bảo toàn commit `d387f4df6` trong lúc chờ bổ sung scope | Bỏ qua lỗi push hoặc sửa lịch sử WIP để né workflow |
| 2026-09-23 | D2–D10 và L0.3/L0.4: tiếp nhận bộ lựa chọn kỹ thuật do agent soạn theo yêu cầu trực tiếp; xem ADR bên dưới và definitions/design v1 | Người dùng yêu cầu tự kiểm tra và điền; không coi đây là bài tự giải hoặc xác nhận của GVHD | Tiếp tục để trống phiếu |
| 2026-09-25 | PIVOT-v14: đổi sang switch-or-stay (ADR "Phase 0 v2" cuối file) | Vùng trust gate đã có OpenTwin v2, CERT, LEC; câu hỏi mới có kết quả giá trị ở cả hai chiều | Giữ v1, thu hẹp novelty |
| 2026-09-25 | L0.2: brief v2 (bản nháp AI, tác giả kiểm); K17, K22, DP1-v2 (ADR cuối file) | Chuyển câu hỏi v14 thành RQ/H bác bỏ được; sửa đại lượng H2 và họ ngưỡng tĩnh theo pilot đã cứu | Giữ nguyên H2 theo thuyết minh v14 |
| 2026-09-25 | L0.3: đề xuất K2 (mục tiêu b, hiệu chỉnh KKT), K3 (loss nhãn riêng), K21 (κ = 0,01); pilot P02 | Oracle là nghiệm của mục tiêu; kiểm bằng số phát hiện hai bẫy hiệu chỉnh | Tune η để "đạt" α (tiêu hết ngân sách) |
| 2026-09-25 | L0.4: definitions v2; K6 (F chính), K7 (đơn vị S, tham số link), K17 bổ sung (rd_kappa, loại rd_all); pilot P03 | Một tên = một estimand; chỉ số H2 được kiểm trước khi định nghĩa | Định nghĩa trong code |

## ADR — L0.3/L0.4, ngày 2026-09-23

Các quyết định sau được ghi trước khi triển khai thí nghiệm chính. Chúng là cấu hình
thiết kế v1 có điều kiện xem lại; chưa phải bằng chứng rằng hypothesis đúng.

### D2 — Nhịp quyết định và đơn vị lặp
- Context: traffic exogenous; lấy mẫu dày tạo tương quan, đồng bộ chu kỳ có thể khóa pha.
- Options: T_dec=0,1τ hoặc 0,5τ; cố định hoặc jitter.
- Decision: T_dec danh nghĩa=0,1τ; mỗi epoch lấy một thời điểm uniform độc lập;
  run là đơn vị lặp, dùng cùng lịch quyết định cho mọi phương pháp.
- Consequences: phủ pha telemetry trong một run; T_dec không còn là chu kỳ cứng.
- Revisit when: L5.1 định nghĩa sticky/wait, hoặc traffic không dừng.

### D3 — Hàm chi phí và thế giới đối chứng
- Context: null Gaussian cần cost affine; hệ số loss 2500 của repo cũ chưa có cơ sở ứng dụng.
- Options: delay-only; delay + trọng số loss; loss-only.
- Decision: delay-only (ms), loss báo cáo riêng. e01 và W_ref dùng D_lin là tiếp tuyến
  M/M/1 tại tải trung bình từng cell. e03 đổi sang D0/D1.
- Consequences: D_lin là đối chứng toán, có thể cho giá trị không vật lý ở đuôi;
  e01 không clip Gaussian. D1 không được coi chỉ khác D_lin ở độ cong.
- Revisit when: có SLA/nguồn cho trọng số loss hoặc phải mô hình hóa biên tải.

### D4 — Harmful error và ε
- Context: decision error đếm cả regret nhỏ; D1 có bất định đo.
- Options: ms tuyệt đối, phần trăm cost, hoặc ngưỡng ứng dụng.
- Decision: ε chính=2 ms; sensitivity {0; 0,5; 1; 5} ms; regret_mean_ms đồng chính.
- Consequences: đây là ngưỡng phân tích theo thang đo D1, chưa phải SLA; không suy
  từ SE từng link thành cận path khi chưa biết covariance. Luôn báo cáo tie riêng.
- Revisit when: e06 đổi thang topology hoặc có yêu cầu ứng dụng/GVHD.

### D5–D9 — Phạm vi và cách nhìn của twin
- Context: cần cô lập staleness trước khi xét phản hồi routing lên tải.
- Options: exogenous/closed-loop; hold/forecast; tuổi chung/per-link; link/OD traffic.
- Decision: D5 exogenous (chờ GVHD xác nhận); D6 last-value hold, forecast là baseline;
  D7 tuổi chung; D8 link-independent cho RQ1a, OD traffic cho evaluation RQ1b/RQ2;
  D9 trình bày z/τ và p̂, kèm đơn vị ms khi diễn giải regret.
- Consequences: không claim closed-loop hoặc tuổi bất đồng bộ; forecast chọn action
  khác phải được đánh giá theo chính action đó, không dùng lại nhãn của hold.
- Revisit when: L5.1, trace không có τ duy nhất, hoặc đánh giá per-link age.

### D10 — Suy luận và thời lượng
- Context: selective ratios không xác định nếu không ACCEPT; dừng khi đủ lỗi tạo optional stopping.
- Options: mean run ratios hoặc pooled ratio; run cố định hoặc dừng theo số lỗi.
- Decision: S=10 seed, CRN, CI t theo run cho metric vô điều kiện; selective dùng
  pooled counts trong từng OD, bootstrap nguyên run 10.000 lần, sau đó trung bình đều OD.
  Horizon cố định 100.000 quyết định đánh giá/run; không kéo dài theo lỗi test.
- Consequences: pooled nhắm quyết định được ACCEPT trong hỗn hợp run, không trung bình
  đều risk từng run. CI với 10 run là xấp xỉ; ít lỗi thì kết luận chưa đủ chính xác.
- Revisit when: pilot độc lập báo precision kém; chỉ đổi horizon cho một batch mới,
  không gộp pilot vào confirmatory. Holm cho tối đa 6 claim được đăng ký cụ thể trước test.

### D11 — Venue (đề xuất, chờ GVHD chốt)
- Context: ICC 2027 đóng bài ngày 2026-10-02, không đủ thời gian tạo evidence;
  CFP CNSM/GLOBECOM 2027 chưa công bố tại ngày 2026-09-23.
- Options: CNSM 2027; GLOBECOM 2027; ICC 2027; lùi sang vòng sau.
- Decision: đề xuất CNSM 2027 là venue chính và GLOBECOM 2027 là dự phòng;
  không nộp ICC 2027. Đây chưa phải quyết định của GVHD và phải kiểm lại CFP 2027.
- Consequences: thiết kế giữ RQ1a/RQ1b/RQ2 cho khổ CNSM dài; nếu chọn GLOBECOM
  phải thu hẹp RQ1b hoặc chuyển validation mở rộng sang bản sau, không cắt evidence cốt lõi.
- Revisit when: CFP 2027 xuất bản hoặc GVHD chọn venue/yêu cầu tốt nghiệp khác.

### D12 — Độ khó quyết định κ = μ_D/σ_D
- Context: W_ref v1 có κ≈2,256 (P1/P2, rho_bar=0,70, sigma=0,05), khiến
  harmful@2ms≈0,33% ở z/tau=0,3 theo pilot được review cung cấp; always-trust đã
  dưới budget 1%, nên H2 suy biến. κ cũng đổi khi quét tải, gây confound e03.
- Options: (a) giữ nguyên; (b) cộng propagation offset hằng số vào P1 để giữ κ_ref;
  (c) đổi cặp path hoặc bandwidth.
- Decision: chọn (b), κ_ref=0,5. Trong mỗi cell, đặt
  b=μ_D(rho_bar)−0,5σ_D(rho_bar) và cộng b vào P1. κ=0,5 vẫn có path ưu thế nhẹ,
  nhưng tạo đủ lỗi để phân biệt gate; pilot độc lập 4.000.000 mẫu tại z/tau=0,3
  cho pair flip=20,54% và harmful@2ms=3,10%.
- Consequences: cô lập độ khó khỏi tải trong đối chứng D_lin, không đổi phương sai,
  tương quan hoặc độ cong; offset là tham số tổng hợp chứ không phải topology vật lý
  nguyên bản và phải khai trong paper. Với clipping/D0/D1 phải báo κ thực hiện được.
- Revisit when: e06 trên topology thật; không chỉnh κ để làm đẹp kết quả mà đo,
  phân tầng/báo cáo phân phối κ và so residual sau khi điều kiện hóa theo κ.

### W, calibration và khởi tạo
- Context: tham số ước lượng hữu hạn không được đảm bảo exact ngay trong null Gaussian.
- Options: W là validity hoặc một trục nghiên cứu.
- Decision: chọn B; W_ref=200τ, e02 quét {10,50,200}τ; hồi quy trễ trên lịch sử twin.
  Dùng selective_risk_ratio chính; OU khởi tạo dừng; trace giữ thứ tự thời gian.
- Consequences: e01 kiểm oracle, operational là đối chứng hữu hạn mẫu; không tăng W
  đến khi test đẹp. Link chung chuyển thành unit test khi viết simulator ở Phase 2.
- Revisit when: trace thiếu lịch sử hoặc đổi chế độ; công bố W thực tế, không mượn dữ liệu tương lai.

## ADR — Phase 1

### D13 — Điều chỉnh L1.1 (2026-09-23)
- Plan tham chiếu: `notes/private/PHASE_1.md`; SHA256 **chưa ghi** vì file private
  không có trong workspace tại thời điểm kiểm. Không dùng hash của bản hướng dẫn
  được dán thay cho hash plan gốc.
- Thay đổi: (1) lượt 3 phần gate OpenTwin dời tới sau L1.5 vì cần kiến thức
  conformal; L1.1 chỉ làm lượt 1–2 và bảng tương ứng biến. (2) Mẫu ghi chú thêm
  Five Cs, bảng claim–evidence, nhãn [F]/[I]/[?]; mục 8 thêm "X quan trọng vì…,
  kiểm bằng…". (3) `.gitignore` chặn `notes/private/` và PDF. (4) Trích OpenTwin
  theo v2, có thứ tự tác giả khác v1.
- Lý do: tránh tái hiện gate khi chưa có nền; claim–evidence là kỹ năng chính;
  tránh rò plan/PDF vào public repository và tránh trích nhầm phiên bản.
- Phương án bị loại: giữ nguyên thứ tự plan.
- Revisit when: file `PHASE_1.md` gốc có mặt local; tính SHA256, chỉ ghi hash vào
  decision log và không commit nội dung plan.

### D14 — Không có GVHD người; AI đóng vai người hướng dẫn thay thế (2026-09-23)
- Context: đồ án hiện không có GVHD; gate Phase 0 yêu cầu người hướng dẫn duyệt
  research contract.
- Options: (a) treo Phase 0 tới khi có GVHD; (b) Claude (AI) đóng vai người hướng
  dẫn, ghi rõ trong hồ sơ; (c) bỏ bước duyệt.
- Decision: chọn (b). Mọi quyết định "người hướng dẫn" ở Phase 0–1 là khuyến nghị
  của AI; tác giả chấp nhận và chịu trách nhiệm. Biên bản luôn ghi rõ `(AI)`.
- Consequences: đồ án có thể tiến tiếp với quyết định có lý do và provenance,
  nhưng review không có thẩm quyền học vụ và không phải góc nhìn độc lập. Tài liệu
  do agent AI soạn rồi AI khác duyệt có thể sai cùng hướng.
- Revisit when: có GVHD/giảng viên thật hoặc trường yêu cầu; trình lại D5, D11,
  D15 để xác nhận. Trước khi nộp paper, xin ít nhất một người đọc độc lập.

### D15 — Kết luận review Phase 0 (2026-09-23; người hướng dẫn thay thế theo D14)
- Scope: chấp thuận RQ1a (e01–e05, gồm trục W) và RQ2; kết quả âm của RQ2 là
  kết quả hợp lệ. RQ1b thu gọn cho paper 1: Abilene + GÉANT, K thuộc {2,3}, age A1;
  T3 và K=5 là mở rộng. Ưu tiên e01 → e02–e05 → e07–e09 trên W_ref → e06 thu gọn.
- D5: chấp thuận exogenous cho paper 1 nếu luồng được điều khiển chiếm
  f≤0,1σ capacity (σ=0,05 thì f≤0,5%). Ghi System model và Limitations;
  closed-loop/route flapping thuộc RQ3.
- ε: giữ 2 ms và sensitivity {0;0,5;1;5}. Vì σ_D giữa các cell e03 thay đổi khoảng
  0,9–22 ms khi σ=0,05, claim e03 dùng DV không phụ thuộc ε là
  `selective_risk_ratio`; harmful@ε chỉ mô tả và luôn in kèm ε/σ_D.
- D11 được chốt: CNSM 2027 main track full paper là chính, GLOBECOM 2027 dự phòng.
  Mốc nội bộ: xong thí nghiệm 2026-12-31, bản thảo đầy đủ 2027-02-15. Khi CFP ra,
  nếu deadline trừ 6 tuần sớm hơn khả năng hoàn thành thì chọn vòng sau, không nén.
- AI: tác giả tự làm ghi chú paper, đạo hàm, dự đoán trước chạy, diễn giải và lý do
  ADR. AI được tìm tài liệu, định dạng, sửa ngôn ngữ và viết code có test khi tác
  giả đọc từng dòng. Khai báo theo policy IEEE.
- Gate Phase 0: ĐẠT CÓ ĐIỀU KIỆN C1–C4 trong `phase0_closeout.md`; DP1 không được
  PASS khi C1–C3 chưa đạt.
- Plan tham chiếu: SHA256 MASTER_PLAN/PHASE_0/PHASE_1 chưa khả dụng vì ba file
  private không có trong workspace. Không thay bằng hash của bản hướng dẫn chat.
- Revisit when: CFP 2027 công bố; có GVHD thật theo D14; hoặc tại DP1.

### D16 — Đính chính hồ sơ sau review D15 (2026-09-23)

Ghi bởi Codex (AI) khi tác giả yêu cầu rà soát và sửa sai; đây chưa phải phần
lý do do tác giả tự viết theo yêu cầu học tập ở D15. D14–D15 giữ nguyên như lịch sử.

- Nguồn review: tài liệu chat do tác giả cung cấp, attachment
  `b03d102d-d6d9-4527-bc21-a912b69b53a2/Pasted text.txt`, tự ghi bên review là
  Claude (AI). Biên bản là bản nhập từ nguồn này; không xác minh độc lập một
  cuộc họp, danh tính reviewer hoặc việc tác giả không có GVHD học vụ.
- D5: f_l=R_flow/capacity_l, áp ngưỡng 0,1σ_l từng link chịu đổi tải. Đây là
  ngưỡng thiết kế chưa validation; không suy ra traffic exogenous hay ổn định
  closed-loop chỉ từ bất đẳng thức. Exogeneity trong simulation là giả định
  cấu trúc; áp dụng vận hành cần sensitivity/validation riêng.
- e03: selective_risk_ratio không chứa ε trực tiếp nhưng có thể phụ thuộc ε
  qua ACCEPT của C2. Khóa quy tắc ACCEPT không phụ thuộc ε cho contrast calibration;
  báo C2 riêng. Ghi rõ cost map, cặp path và nguồn SD khi báo ε/σ_D.
- Closeout: “mỗi eNN một chiều” không chính xác (e05 là factorial M×age);
  e06–e12 còn thiếu config chi tiết. Các điều kiện có thể được giữ cố định trong
  từng contrast, không đồng nghĩa mọi thí nghiệm chỉ có một biến.
- Lịch: giữ hai mốc nội bộ 2026-12-31 và 2027-02-15. Quy tắc D15 cụ thể là
  deadline trừ 6 tuần phải không sớm hơn ngày bản thảo; tương đương deadline
  từ 2027-03-29 trở đi theo lịch hiện tại. Đây là dự phòng sau bản thảo,
  không phải deadline đã công bố hay ngày hoàn thành thí nghiệm.
- Nguồn soạn, trạng thái bài tự làm và kiểm tra chưa thực hiện tiếp tục được
  công khai trong hồ sơ. Không diễn giải tag có điều kiện thành hoàn tất C1–C4.

### D17 — Hoàn thành Lesson 1.1 theo xác nhận của tác giả (2026-09-23)

- Evidence: `notes/01_literature/notes/opentwin_2026_v2.md` có Five Cs,
  5 claim–evidence, bảng biến, tám câu hỏi, câu định vị và §/trang cho kết quả số;
  dòng OpenTwin trong `novelty_matrix.xlsx` đã chuyển các điểm CHƯA kiểm/SUY LUẬN
  thành kết quả đọc full text có dẫn §VI, §VII-C và §VIII.
- Author check: tác giả xác nhận đã tự đọc §VI, Theorem 3, Fig. 5–6, kiểm note và
  trình bày gate trong 3 phút. Đây là self-attestation, không phải kiểm tra độc lập.
- Decision: L1.1 DONE; pass 3 rút gọn đã đủ, pass 3 đầy đủ phần gate chờ L1.5
  theo D13. Kết luận “age+margin chưa ai làm” vẫn chưa khóa trước L1.2/DP1.
- Administrative exception: `notes/private/PHASE_1.md` không có trong workspace
  và không tìm thấy dưới `/home/vantai`, nên SHA256 ở D13 vẫn chưa khả dụng.
  Không tạo hash từ attachment hoặc bản hướng dẫn thay cho plan gốc.

### D18 — Tiêu chí DP1 (đăng ký MUỘN, 2026-09-23)

- Ghi chú trung thực: tiêu chí này lẽ ra phải ghi trước khi đọc paper đầu tiên;
  OpenTwin v2 đã được đọc (D17) trước khi ghi. Văn bản tiêu chí bên dưới được
  chép nguyên văn từ hướng dẫn L1.2 do tác giả cung cấp ngày 2026-09-23. File
  `notes/private/PHASE_1.md` không có trên máy, nên SHA256 vẫn **chưa khả dụng**;
  không thay bằng hash của attachment hoặc tự tạo một bản plan giả.
- DP1 = PASS nếu mỗi candidate contribution được giữ có >= 1 điểm khác biệt loại
  problem/method đã kiểm full text so với MỌI paper gần nhất (OpenTwin v2,
  Zhu et al., Guérin--Orda), VÀ lý thuyết L1.3--L1.5 cho thấy câu trả lời không
  hiển nhiên.
- DP1 = NARROW nếu chỉ characterization (RQ1) còn điểm khác biệt, còn gate (RQ2)
  trùng một paper gần nhất.
- DP1 = PIVOT nếu không contribution nào còn điểm khác biệt problem/method.
- Chỉ ``setting khác'' KHÔNG đủ cho PASS.
- Bổ sung từ L1.1: paper nào được phân loại ``rất gần'' trong search log cũng
  phải qua phép so này trước DP1.
- Trạng thái tại thời điểm ghi: **chưa quyết định DP1**; CERT và LEC đã được xếp
  rất gần, backlog snowballing và phần full text bắt buộc vẫn chưa hoàn tất.

## ADR — Phase 0 v2: pivot sang switch-or-stay (2026-09-25)

### PIVOT-v14 — Đổi đơn vị quyết định và câu hỏi trung tâm

- **Context:** Hướng v1 (brief v1, D2–D12) hỏi trust gate theo tuổi × top-2 margin có tăng coverage
  tại cùng selective harmful risk không. L1.1–L1.2 cho thấy các mảnh chính đã có: OpenTwin v2
  (conformal action gate cho NDT), CERT (route certificate theo tuổi), LEC (risk trên tập ACCEPT).
  Khác biệt còn lại hẹp; ngữ nghĩa ABSTAIN (static/sticky/wait) chưa có phương án vận hành rõ.
- **Options:** (a) giữ v1, thu hẹp novelty; (b) switch-or-stay: đơn vị quyết định là đổi/giữ, mốc là
  đường hiện tại; câu hỏi "khi nào hysteresis cố định là đủ" (thuyết minh v12 → v14); (c) dừng hướng này.
- **Decision:** (b).
- **Consequences:** metric chính là missed improvement tại ngân sách harmful switch (mục tiêu chờ chốt,
  K2); ground truth là DES M/D/1/K có verify; cần oracle cùng thông tin; top-2 margin, coverage,
  W_ref/κ_ref không còn dùng. Literature L1.1–L1.2 giữ nguyên giá trị.
- **Giữ nguyên:** simulation là bằng chứng chính; `data/mininet_calibration/`; `lessons_from_dt4n.md`.
- **Mốc:** tag `pre-pivot-v14` → `28ab59e951f3d579f0e16e84ab08dd26cbe8342c`.
- **Revisit when:** DP0 cho PIVOT (fixed đủ ở mọi nơi), hoặc DP1 tìm thấy bài trả lời đúng RQ1.

### Ghi nhận kèm pivot (2026-09-25)

1. **ĐÍNH CHÍNH thuyết minh v14 §6.1.** Loss/chờ "M/D/1/K" 0,274% và 4,909% là một lần mô phỏng
   (một seed, 300k gói), không phải nghiệm. Nghiệm chuỗi Markov nhúng, K = 11, S = 1:
   ρ = 0,8 → loss 0,235337%, chờ 1,878268 S; ρ = 1,0 → loss 4,615385%, chờ 4,836022 S. Kiểm độc lập bằng
   Monte Carlo 12 seed (0–11): TB 0,238306% / 4,648667%; 0,274333% và 4,909000% là giá trị LỚN NHẤT.
   Sửa ở v15; tự tái lập ở L2.1.
2. **Hiệu lực quyết định cũ.** D2–D12: hết hiệu lực, thay bằng khung K1–K21 (Phase 0 v2).
   D13, D16, D17, D18: lịch sử; phần literature vẫn dùng. D15: phần scope/ε/κ hết hiệu lực; venue
   (CNSM 2027 / GLOBECOM 2027) và ranh giới dùng AI giữ tạm, trình lại ở L0.6. D14: xem mục 3.
3. **Người hướng dẫn.** Thuyết minh NCKH ghi TS. Huỳnh Văn Đặng là cán bộ hướng dẫn; tính tới
   2026-09-25 chưa có buổi làm việc nào với GVHD người thật được ghi biên bản. D14 giữ hiệu lực tới buổi làm việc đầu tiên (L0.6).
4. **Điều kiện gate v1 (C1–C4).** C1, C3: đóng vì gắn với definitions và câu hỏi bảo vệ v1, không còn
   áp dụng. C2 (elevator test): chuyển sang brief v2 (L0.2). C4 (push `wip-before-archive`, kiểm VM):
   còn mở — `git ls-remote` ngày 2026-09-25 không thấy nhánh này trên GitHub; hạn trước Phase 7.
5. **Lưu trữ.** 7 tài liệu hợp đồng v1 → `notes/archive/v1_trust_gate/` (giữ tên); `margin.py` và
   `test_margin.py` → `reference/v1_trust_gate/`; stub v1 trong `ndtrisk/` đã xoá (xem tag).
6. **Plan private.** MASTER_PLAN v2 và PHASE_0 v2 không có trong `notes/private/` hoặc `/home/vantai`
   tại thời điểm kiểm, nên SHA256 chưa khả dụng; không dùng hash của attachment hay bản hướng dẫn thay thế.
7. **Artefact số liệu của thuyết minh.** Tìm thấy và commit tại
   `experiments/pilot/switch_or_stay_diagnostic.py` và `results/switch_or_stay_diagnostic.txt`;
   chạy lại ngày 2026-09-25: output trùng byte. Pilot fixed-vs-scaled dùng chung script, seed 42.
8. **Testbed không phải M/D/1/K.** Testbed dt4n = HTB token bucket (burst 1600 B) + bfifo q × 1512 B;
   CBR ρ = 0,6 cho OWD 0,142 ms < S = 3,024 ms. Câu "gói cố định nên hàng đợi lõi là M/D/1/K"
   (thuyết minh v14 §3) đúng cho DES, không đúng cho testbed. Sửa ở v15; vai trò Mininet chốt ở
   K7/K14/K20 (L0.4–L0.6). Ý nghĩa cột dữ liệu: `data/mininet_calibration/PROVENANCE.md`.

### Bổ sung mục 6 của "Ghi nhận kèm pivot" — 2026-09-25

Tác giả xác nhận MASTER_PLAN v2 và PHASE_0 v2 đã được lưu ở vị trí khác trên máy cá nhân.
Hai file này không cần sao chép vào `notes/private/` của repo, không yêu cầu SHA256 trong repo này.
Điều kiện quản lý plan local của L0.1 được đánh dấu **PASS theo xác nhận của tác giả**;
đây là self-attestation, không phải kiểm chứng byte độc lập. Mục 6 trước đó được giữ nguyên như lịch sử.

## ADR — Phase 0 v2 / L0.2 (2026-09-25)

### K17 — Đại lượng dự báo trong H2 (ĐỀ XUẤT; chọn ở DP0, khoá ở prereg RQ1)

- **Context:** H2 ở thuyết minh v14 dùng sd(log s). Họ tịnh tiến là điều kiện đủ, không cần: ngưỡng tĩnh vẫn tối ưu
  khi odds đơn điệu theo Î dù s thay đổi. Pilot v14 (`experiments/pilot/switch_or_stay_diagnostic.py`, phần [3]) rút
  `scale` độc lập với `truth`, nên chưa kiểm trường hợp s và Î cùng tăng gần knee.
- **Options:** (a) giữ sd(log s); (b) `rank_disagreement` = 1 − Spearman(Î, log-odds); (c) `sd_log_s_cond`.
- **Decision:** (b) và (c) là ứng viên chính, (a) là biến phụ. Chọn chỉ số chính ở DP0 bằng seed pilot (không dùng
  lại cho thí nghiệm chính); khoá trong prereg RQ1.
- **Consequences:** F2 tính cả ba; bản twin của chỉ số được báo cho RQ1-op.
- **Revisit when:** F2 cho thấy cả ba chỉ số không phân biệt được các ô.

### K22 — "Ngưỡng tĩnh" trong RQ1 gồm cả tuyệt đối và tương đối

- **Context:** Pilot P01 (exploratory, 2026-09-24): trên đường cong đo Mininet (poisson, 6 Mb/s, q = 13), T'/T chỉ
  5,5–8,3 khi ρ từ 0,55 tới 1,0 (M/M/1: 2,2 → 66,7). T'/T gần hằng nghĩa là bất định của delay tỉ lệ với độ lớn
  delay, nên ngưỡng tương đối kiểu RON bù phần lớn độ không đồng đều. So riêng với ngưỡng tuyệt đối có thể tạo
  "khoảng cách" chỉ do thiếu chuẩn hoá theo độ lớn.
- **Options:** (a) chỉ ngưỡng tuyệt đối H trên Î; (b) họ tĩnh = {H trên Î; r trên Î/Ĉ_cur}, lấy cái tốt hơn trong
  từng ô; (c) thêm ngưỡng kết hợp tuyệt đối + tương đối.
- **Decision:** (b). `gap_fixed_oracle` = missed(tốt nhất của họ tĩnh, tune từng ô) − missed(oracle), cùng α.
- **Consequences:** đối thủ khó hơn; kết luận "cần thích nghi" có nghĩa hơn. (c) là mở rộng nếu F2 cho thấy (b) yếu.
- **Revisit when:** F2 cho thấy ngưỡng tương đối không bao giờ tốt hơn ngưỡng tuyệt đối trong DES.

### DP1-v2 — Tiêu chí DP1 cho hướng v2 (cập nhật danh sách bài của D18)

- Khung giữ nguyên D18: PASS / NARROW / PIVOT; "setting khác" không đủ cho PASS.
- Ghi TRƯỚC khi đọc full text các bài mới. Bài gần nhất phải đối chiếu full text trước DP1: Seshadri–Katz 2003;
  Liyanage et al. 2026 (arXiv 2604.21483); Almohammedi et al. 2026 (arXiv 2607.22857); Fischer–Vöcking 2005/2009;
  OpenTwin v2; CERT; Lekeufack et al. 2024; Zhu et al. 2026.
- Forward citation của Seshadri–Katz và Fischer–Vöcking là bắt buộc trước DP1.

## ADR — Phase 0 v2 / L0.3 (2026-09-25)

### K2 — Mục tiêu chính (ĐỀ XUẤT — chờ GVHD, L0.6)

- **Context:** Oracle là nghiệm của mục tiêu. Delay kỳ vọng (a) cho luật không phụ thuộc độ rộng s; ngân sách harm
  trên mọi epoch (b) cho luật p+/p−; precision (c) cho luật p+/(p− − α). Hướng v1 dùng dạng (c) (selective harmful
  risk trên ACCEPT); LEC và Zhu et al. 2026 bảo đảm các dạng gần (c).
- **Options:** (a); (b); (c).
- **Decision (đề xuất):** (b) — tối thiểu missed + κ·tỉ lệ đổi với harm ≤ α, cả ba chia cho mọi epoch; α = 1% mặc định.
  Mọi luật hiệu chỉnh bằng cùng tiêu chí; luật xác suất dùng λ ≥ 0 nhỏ nhất đạt harm ≤ α (không tiêu hết ngân sách).
- **Consequences:** oracle = đổi ⇔ p+ − λ·p− > κ. Cách viết "tune η để đạt α" trong MASTER_PLAN L2.3/L4.5 được hiểu
  là "λ nhỏ nhất để harm ≤ α". Hàm `calibrated_threshold` trong pilot v14 chọn tập đổi lớn nhất thỏa ngân sách
  (tiêu hết ngân sách); code F2 không dùng lại cách đó. Delay trung bình báo như kết quả phụ ("giá của an toàn").
- **Bằng chứng:** P02 (exploratory). Thế giới C: tiêu hết ngân sách → harm 1,000%, đổi 95,64%, missed 0;
  KKT → harm 0, đổi 84,83%. Thế giới A: (a) cho harm 5,24%.
- **Revisit when:** GVHD chọn (a) hoặc (c); hoặc F2 cho thấy ràng buộc không cắn ở mọi ô gần điểm neo.

### K3 — Harm về loss (ĐỀ XUẤT — chờ GVHD)

- **Context:** Delay tính trên gói nhận được, nên path mất nhiều gói trông tốt hơn về delay (survivorship).
  Gộp delay và loss cần trọng số có nguồn; w_loss = 2500 của dt4n không có nguồn.
- **Options:** (a) nhãn phụ riêng: đổi gây hại về loss khi loss_alt − loss_cur > δ; (b) utility delay + w·loss; (c) bỏ loss.
- **Decision (đề xuất):** (a), δ = 1 điểm %; độ nhạy δ ∈ {0,5; 2} điểm %. `harmful_loss_rate` báo cạnh mọi kết quả delay.
- **Lý do δ:** 1% loss thường được dùng làm ngưỡng chất lượng thoại trong hướng dẫn thiết kế QoS (mở nguồn gốc trước khi trích).
- **Revisit when:** có trọng số vận hành có nguồn, hoặc F2 cho thấy harm về loss chiếm phần lớn harm.

### K21 — Lần đổi vô ích (ĐỀ XUẤT — chờ GVHD)

- **Context:** Khi p− ≈ 0, luật (b) thuần đổi cả khi p+ ≈ 0: không tốn ngân sách harm nhưng tốn chi phí thật
  (reordering, flap). P02 thế giới C: KKT với κ = 0 đổi 84,83% epoch, 76,64% epoch là lần đổi có p+ < 5%.
- **Options:** (a) κ = 0, chỉ báo switch rate; (b) κ nhỏ trong tiêu chí chung missed + κ·đổi; (c) c_switch có nguồn đưa
  vào I; (d) ngân sách switch rate thứ hai.
- **Decision (đề xuất):** (b), κ = 0,01; báo κ = 0 làm độ nhạy. Áp cho MỌI luật, kể cả ngưỡng tĩnh và oracle.
- **Consequences:** P02-C: đổi 84,83% → 10,00%, missed +0,010 điểm %. P02-A: đổi 42,55% → 42,51%, missed không đổi.
- **Revisit when:** có c_switch có nguồn cho ứng dụng mục tiêu (VoIP), hoặc κ làm đổi thứ tự các luật ở một ô.

## ADR — Phase 0 v2 / L0.4 (2026-09-25)

### K6 — Nội dung của thông tin F (CHỐT cho phase lõi)

- **Context:** Oracle chỉ là cận trên khi thấy ít nhất mọi thứ policy thấy (F_oracle ⊇ F_policy). Oracle ước lượng
  bằng bin thực nghiệm chỉ khả thi khi F nhỏ. Probe dùng để chấm điểm, không được rò sang policy.
- **Options:** (a) F đầy đủ (mọi cửa sổ quá khứ) cho mọi policy; (b) F chính rút gọn cho MỌI policy và oracle, F mở rộng
  là thí nghiệm phụ; (c) thêm telemetry độ dài hàng đợi.
- **Decision:** (b). F chính = {ρ̂ của mỗi link trên cur và alt ở cửa sổ mới nhất; z; path hiện tại}, cộng tri thức
  tĩnh {S, K, prop, tham số OU ước lượng trên đoạn calibration trước run} (mức tri thức theo K18, L0.5).
  ρ̂ = (gói truyền + gói drop trong W)·S/W (tải đề nghị). F mở rộng = F chính + 19 cửa sổ trước (tổng 20).
  Không có trong F: probe, độ dài hàng đợi, tải thật.
- **Consequences:** oracle bin trên (ρ̂_cur, ρ̂_alt, z, path) (bỏ z khi tuổi cố định); test không rò rỉ ở Phase 4
  kiểm policy không đọc probe.
- **Revisit when:** F4/F5 cho thấy F chính làm twin và oracle cùng "mù" ở vùng quan trọng (khoảng cách twin–oracle
  chủ yếu do thiếu lịch sử) → chạy F mở rộng.

### K7 — Đơn vị thời gian và tham số link (DỰ THẢO; khoá ở DP0)

- **Context:** Nhiễu đếm và bộ nhớ hàng đợi đều tỉ lệ với S, nên tốc độ testbed 4 Mb/s quyết định nguồn bất định chiếm
  ưu thế (Π_noise = 5,78 ở 4 Mb/s; 1,16 ở 100 Mb/s). Testbed là HTB token bucket, không phải M/D/1/K (PIVOT mục 8).
- **Options:** (a) DES tính bằng giây theo testbed 4 Mb/s; (b) DES tính theo đơn vị S, tham số thời gian chọn theo
  nhóm Π tại điểm neo F1.
- **Decision (dự thảo):** (b). S = 1; K ∈ {11 (nông), 100 (sâu)} theo đơn vị S; gói cố định. Testbed 4 Mb/s là một
  điểm trong không gian Π (K = 100 ↔ 302 ms), chỉ dùng cho validation.
- **Consequences:** mọi bảng báo cả K (đơn vị S) và thời gian buffer ở điểm neo; F1 phải trả về điểm neo dưới dạng Π.
- **Revisit when:** DP0.

### K17 bổ sung — Định nghĩa chỉ số H2 (2026-09-25)

- Pilot P03 (exploratory, 4 thế giới đồ chơi): `sd_log_s` báo động giả (B: 0,565; D: 0,228 dù khoảng cách ≈ 0);
  Spearman trên MỌI epoch hỏng ở mạng rảnh (C: 0,195 dù khoảng cách = 0) do kẹp p± ở sàn Monte Carlo.
- Ứng viên (b) được định nghĩa lại: `rd_kappa` = 1 − Spearman(Î, log-odds) trên tập cân nhắc {p+ > κ}.
  Ứng viên (c) `sd_log_s_cond` giữ nguyên. `rd_all` bị loại. Quy tắc chọn ở DP0 không đổi.
