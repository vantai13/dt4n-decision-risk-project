# Hồ sơ một trang cho GVHD — GO-check, ngày 2026-10-01

**Trạng thái: chưa đủ bằng chứng GO.** Đã tái lập rollout seed cũ; đã đạt
validity cho thí nghiệm bố trí thông tin. Chưa mở fresh hoặc outcome FIX/SYM/FF.

| Tiêu chí | Bằng chứng hiện có | Đánh giá hiện tại |
|---|---|---|
| TC1: ưu thế delay cùng ngân sách harm | go0 α=0,2%, tự do: +1,652 [1,225; 2,080] ms, harm SC/K2 = 0,78α/0,82α; α=1%: CI chứa 0 | Đạt điều kiện gợi ý trên seed cũ ở α chặt; chờ lặp độc lập |
| TC2: tính thực tế | Chưa có nguồn mới cho FIX, FF hoặc cadence 1 s. Thí nghiệm cùng thế giới FIX/SYM/FF đã đạt V1–V6 | Chưa đạt; outcome sẽ xác định bố trí cần tìm nguồn |
| TC3: magnitude VoIP | Sàn đã khóa 8,1 ms và 10% headroom; cả CI go0 tự do lẫn cooldown nằm dưới 8,1 ms | Chưa đạt sàn tuyệt đối; giữ phán quyết VoIP |

Headroom rollout được dịch thành delay(SC) − delay(oracle nhìn trước);
oracle là cận dưới chứ không phải phương pháp triển khai. Giữ quy tắc CI L1.5.
Cooldown 30 s cho +0,552 [0,124; 0,981] ms; hai budget cho cùng kết quả trong
grid hiện tại. K2 dùng ít harm hơn SC; dòng này không xác nhận cơ chế budget
harm chặt.

Đề nghị thảo luận: delay trung bình ở vùng hiện tại có phản ánh chất lượng
VoIP đủ tốt không, và có cần báo loss theo K3 như nhãn phụ đã định nghĩa không?
Chưa thay metric/ứng dụng; các số về G.711/PLC từ hướng dẫn chưa được kiểm ITU
trong lượt chuẩn bị này.

Điểm tiếp theo: nhận dự đoán tác giả → commit hai spec → chạy fresh
92001/93001 → outcome 94001/95001 → kiểm nguồn TC2 → cập nhật bảng trên.
Tham chiếu output: results/gocheck/go0_output.txt, info_validity_output.txt
và wiring_validity_output.txt.
