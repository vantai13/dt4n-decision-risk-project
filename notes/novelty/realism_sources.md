# Nguồn cho tham số thực tế — nháp L1.9 (2026-10-02)

> Hạt giống từ L1.3. Cả ba tham số đều là **GIẢ ĐỊNH**, chưa có nguồn thực nghiệm.
> Không suy từ POS_probeB ra cấu hình phổ biến của mạng thật.

| Tham số | Giá trị đang minh hoạ | Trạng thái | Bằng chứng cần tìm |
|---|---|---|---|
| Chu kỳ báo đường dự phòng B | 30 s (A: 0,5 s) | GIẢ ĐỊNH từ grid.controls, không phải đo thực tế | Chu kỳ thu thập/poll thực, chủ động hay thụ động, loại thiết bị/controller và timestamp |
| Cửa sổ đếm có bằng chu kỳ báo không? | W = T_tel, nên W_B = 30 s | GIẢ ĐỊNH của world.telemetry_view | Phân biệt khoảng tích luỹ counter, lịch xuất bản tin, trễ vận chuyển, khả năng cửa sổ trượt |
| Độ lớn sai ρ̄_B | thật 0,85; twin tin 0,80 hoặc 0,70 (lệch −0,05/−0,15) | GIẢ ĐỊNH do lesson chọn | Sai số ước lượng từ dữ liệu có độ dài xác định, dịch chế độ, đánh giá ngoài mẫu; cả dấu và độ lớn |

L1.9 cần lưu nguồn gốc, ngày, môi trường áp dụng, giá trị/dải, cách ánh xạ
sang mô hình và mức đã kiểm. Mức giả định chỉ hỗ trợ kết luận có điều kiện.
H, bộ sinh đề xuất, Δρ và metric cũng phải được khai báo khi so thứ hạng nguồn sai.
