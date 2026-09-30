# Positioning — v2 (BẢN NHÁP, 2026-09-30; khung Phase 1 v2)

> Chờ: Richardson 2000 full text; Houtekamer/Whitaker–Loughe full text (tải tay); một bài nghiên cứu họ multipath/SD-WAN.
> Bản 27/09 giữ trong git. Provenance: Claude (AI) soạn; tác giả kiểm. Mỗi câu trỏ tới một ghi chú/ô đã kiểm.

So một luật dùng phân phối với luật tĩnh đã tune, trên cùng thông tin và cùng ngân sách, là câu hỏi đã có tiền lệ: trong
handoff, luật locally optimal so xác suất rơi dưới ngưỡng phục vụ chỉ ngang luật hysteresis + ngưỡng hai tham số tốt nhất
khi dùng cùng bộ dự báo, ở cùng số handoff (veeravalli_kelly_1997 §V, Fig. 3); trong dự báo tổ hợp, spread không cải
thiện dự báo xác suất ngoài mẫu vì phần biến thiên dự đoán được của bất định nhỏ (jewson_2003 §4.2, §4.5). Cả hai không
tách được giá trị của độ rộng biến thiên giữa các quyết định: mô hình handoff có phương sai có điều kiện không đổi
(veeravalli_kelly_1997 §IV), còn bài khí tượng chấm dự báo bằng likelihood, không chấm quyết định (jewson_2003 §3).
Chuẩn hoá giá trị theo thông tin hoàn hảo (REV; Richardson 2000 — abstract), tách EVPI/VSS (Birge 1982 — thứ cấp), tương
đương ràng buộc–Bayes (veeravalli_kelly_1997 Thm 1) và luật bậc hai (classical_anchors.md) là công cụ cũ. Trong mạng và
điện toán biên, đã có dự đoán + hysteresis và (μ, σ) + hysteresis nhưng thiếu ô "trung bình + hysteresis" và không có
oracle (burbano_2025 §III-B; liyanage_2026 §III-B, Table II); twin xử lý telemetry trễ đặt giá trị vào dự báo trạng thái
tới lúc quyết định (tiwari_2026 §III-C, §IV-D) hoặc vào cổng tin cậy toàn cục (opentwin_2026_v2 §VI; almohammedi_2026
Eq. 12); SD-WAN vận hành đổi đường bằng ngưỡng SLA trên trung bình dài kèm damping (cisco_aar_sdwan §1); công trình chế độ
tập thể xét dao động khi tải nội sinh (fischer_voecking_2005 Thm 1, 3; seshadri_katz_2003 Fig. 4–6; Keralapura 2008 và
Scherrer 2020 — abstract). Đề tài tách kênh độ rộng khi bất định thật sự biến thiên giữa các quyết định (κ̂ = 0,15–0,27
trong DES, f05c) cho quyết định đổi/giữ đường của một luồng nhỏ trên tải ngoại sinh dưới ngân sách harm: với oracle một
bước cùng thông tin dọc quỹ đạo tham chiếu, headroom tách thành thông tin 59–84%, an toàn 6–14%, tâm 1–4% và độ rộng thuần
≤ 1,5% (F7 §3–4); đề tài giải thích vì sao phần độ rộng nhỏ — biên của luật đã tune nằm ở vùng thưa epoch (f₀ nhỏ hơn toy
30–200 lần, F7 §1) và β ∝ λ (T4 §3) — và lập bản đồ sơ bộ các cơ chế mạng có và không tạo bất định trực giao (f05c; F7 §3;
F8 §3, khám phá).

## Không được claim (v2)
- "Luật tĩnh đúng thống kê gần bằng luật dùng xác suất" như phát hiện chung (Veeravalli–Kelly 1997; Jewson 2003) — chỉ
  claim trong điểm vận hành đã kiểm, kèm cơ chế.
- So luật dựa phân phối với luật tĩnh đã tune trên cùng dự báo, ở cùng ngân sách, bằng đường cong đánh đổi (V–K 1997).
- Luật dựa mô hình thích nghi môi trường tốt hơn hysteresis cố định (V–K 1997 §V) — liên quan H3 cũ.
- Nguyên lý "độ rộng thêm ít khi biến thiên dự đoán được của bất định nhỏ; giá trị ở tâm" (Jewson 2003; Houtekamer 1993).
- Chuẩn hoá theo thông tin hoàn hảo (REV); tách EVPI/VSS; luật bậc hai; tương đương ràng buộc–Bayes.
- "Twin dựng trạng thái hiện tại từ telemetry trễ" (Tiwari 2026); "tuổi là thông tin phụ cho quyết định" (Li 2026).
- "MPTCP có subflow stale được probe định kỳ" (sai nghĩa); "SD-WAN đo path phụ thưa hơn" (sai với cấu hình mặc định Cisco).
- Giữ nguyên danh sách không-claim của bản 27/09.

## Đóng góp ứng viên (DP1 khung mới) — candidate, chưa kết luận
(a′) Tách kênh độ rộng biến thiên (K2 − SC, κ > 0) khỏi kênh tâm/mức, và phân rã thông tin / an toàn / tâm / độ rộng với
     oracle một bước cùng thông tin trong DES có ground truth.
(c′) Bản đồ cơ chế mạng → κ, gồm cả cơ chế KHÔNG tạo κ; giả thuyết trạng thái (backlog, tải) cho Phase 2.
(d′) Giao thức (thu hẹp): oracle một bước cùng thông tin dọc quỹ đạo tham chiếu + CRN + kiểm oracle ≥ tĩnh trên seed
     oracle giữ riêng.
KHÔNG còn là đóng góp: (b) nguyên lý đổi thứ tự và luật bậc hai — lăng kính giải thích, có trích dẫn.

## Giới hạn phạm vi đi kèm mọi claim
Một luồng nhỏ, tải OU-Poisson ngoại sinh, M/D/1/K FIFO, 4 Mb/s, K ∈ {11, 100}, α = 1%, oracle bin, thang giây (W = 0,5 s;
SD-WAN mặc định ở thang 10–60 phút); F7: một cặp path; F8: khám phá.
