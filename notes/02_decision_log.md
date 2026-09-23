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

### W, calibration và khởi tạo
- Context: tham số ước lượng hữu hạn không được đảm bảo exact ngay trong null Gaussian.
- Options: W là validity hoặc một trục nghiên cứu.
- Decision: chọn B; W_ref=200τ, e02 quét {10,50,200}τ; hồi quy trễ trên lịch sử twin.
  Dùng selective_risk_ratio chính; OU khởi tạo dừng; trace giữ thứ tự thời gian.
- Consequences: e01 kiểm oracle, operational là đối chứng hữu hạn mẫu; không tăng W
  đến khi test đẹp. Link chung chuyển thành unit test khi viết simulator ở Phase 2.
- Revisit when: trace thiếu lịch sử hoặc đổi chế độ; công bố W thực tế, không mượn dữ liệu tương lai.
