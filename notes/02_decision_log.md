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
