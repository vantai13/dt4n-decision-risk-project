# Positioning — BẢN NHÁP (2026-09-27)

> Trạng thái: tạm thời. Chờ ghi chú full text Seshadri–Katz 2003, Mitzenmacher 2000, Dahlin 2000 và forward citation
> của Seshadri–Katz, Fischer–Vöcking (L1.9 phần 2). Mỗi câu trỏ tới một ô đã kiểm trong novelty matrix hoặc ghi chú.
> Provenance: Claude (AI) soạn; tác giả kiểm.

Dùng dự đoán delay kết hợp một ngưỡng hysteresis để chọn đích đã có trong literature gần (Burbano 2025, §III-B,
Alg. 1), và dùng thêm bất định dự báo — xếp hạng theo μ + kσ, lọc theo xác suất vi phạm SLO — cũng đã có (Liyanage 2026,
§III-B, Alg. 1–2). Các đánh giá này dùng một trace, không có khoảng tin cậy, và không có ô "trung bình + hysteresis",
nên không tách được giá trị của bất định khỏi giá trị của hysteresis (Liyanage 2026, §V-A, Table II; Burbano 2025,
Table I). Công trình gác twin theo độ tin cậy xử lý lệch mô hình toàn cục theo thời gian, không phải bất định thay đổi
theo từng quyết định do tuổi và nhiễu của telemetry (Almohammedi 2026, Eq. 6–12; ghi chú opentwin_2026_v2). Lý thuyết
về thông tin cũ trong định tuyến tập thể cho thấy hình thức luật đổi quyết định hội tụ hay dao động (Fischer–Vöcking,
TR 2005, Thm 1, Thm 3), nhưng trong chế độ tải nội sinh. Mô phỏng định tuyến overlay tập thể cho thấy H tối ưu phụ
thuộc mạnh vào tham số hệ thống, còn H cố định chạy tốt khi các luồng tự chọn đường chỉ là phần nhỏ của tải
(Seshadri–Katz 2003, Fig. 4–6, §V-B) — một dự đoán về đúng chế độ mà
đề tài đo, nhưng chưa được đối chiếu với oracle cùng thông tin. Đề tài xét chế độ bổ sung — một luồng nhỏ trên tải
ngoại sinh với telemetry có tuổi và nhiễu — đo khoảng cách giữa ngưỡng tĩnh được tune và oracle cùng thông tin trong
DES, tách khoảng cách thành phần tâm và phần độ rộng, và thấy phần độ rộng dưới 0,16 ms, thấp hơn SESOI khoảng 50 lần, trong
miền đã thử (f04b, f05, f05b).

## Không được claim

- "Dự đoán + hysteresis" là mới (Burbano 2025; Liyanage 2026).
- Dùng (μ, σ) hay xác suất vi phạm để chọn đích là mới (Liyanage 2026).
- Fallback theo độ tin cậy twin là mới (Almohammedi 2026; OpenTwin).
- "Thông tin cũ làm luật tham lam hỏng/dao động" là mới (Fischer–Vöcking; Shaikh et al. 2001).
- "H tối ưu phụ thuộc tham số hệ thống" hay "ngưỡng hysteresis thích nghi (MIMD)" là mới (Seshadri–Katz 2003).

## Đóng góp ứng viên (DP1, khung PIVOT) — "strong candidate", chưa phải kết luận

(a) Đặc trưng hoá khi nào bất định từng quyết định có giá trị hơn ngưỡng tĩnh được tune, với cận trên và phân rã
    thích nghi / an toàn / thông tin.
(b) Phép tách tâm / độ rộng — ô factorial còn thiếu ở literature gần nhất.
(c) Phát hiện phương pháp: surrogate dừng (PSA) thổi phồng giá trị thích nghi ở vùng gần bão hoà.
(d) Giao thức đánh giá: oracle cùng thông tin, quỹ đạo tham chiếu, CRN, CI paired theo seed, phân tích mù.

## Giới hạn phạm vi phải đi kèm mọi câu claim

Hai path đối xứng; tải OU-Poisson; một luồng nhỏ (không dồn đàn); mục tiêu gain trung bình có ràng buộc harm (chưa
kiểm mục tiêu SLO); 4 Mb/s; K ∈ {11, 100}; α = 1%; oracle bin.
