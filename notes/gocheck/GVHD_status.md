# Hồ sơ một trang cho GVHD — GO-check, ngày 2026-10-01

**Trạng thái: CHƯA GO, chờ họp GVHD.** Đã đạt V1–V6 và tái lập kết quả
sandbox trên seed 92/93 và 94/95. Khóa cấu hình local: 9272119.
Dự đoán Claude AI, lệch NT-1; không gọi là dự đoán tác giả. Outcome đã được
cung cấp trước lần chạy local, nên không gọi tái lập local là xác nhận mù.

| Tiêu chí | Bằng chứng hiện có | Đánh giá hiện tại |
|---|---|---|
| TC1: ưu thế delay cùng ngân sách harm | FIX 92/93: +1,506 [1,229; 1,784] ms; FIX 94/95: +1,746 [1,427; 2,066] ms | 92/93 trượt chênh harm ≤0,1α; 94/95 đạt. SYM đạt với hiệu ứng nhỏ |
| TC2: tính thực tế | SYM +0,153 [0,139; 0,167] ms; FIX hiệu ứng lớn hơn; FF −0,193 ms trong thiết kế bỏ số đo tươi path vừa rời | Chưa đạt nguồn cho FIX và cadence; FF chưa dùng kết luận đo thụ động thật |
| TC3: magnitude VoIP | FIX 1,51–1,75 ms; cooldown 0,64–0,68 ms; SYM 0,15 ms; sàn 8,1 ms | Chưa đạt sàn tuyệt đối; phần tương đối không cứu được quy tắc cả hai |

Headroom rollout được dịch thành delay(SC) − delay(oracle nhìn trước);
oracle là cận dưới chứ không phải phương pháp triển khai. Giữ quy tắc CI L1.5.
Cooldown FIX: 92/93 +0,681 [0,411; 0,950] ms; 94/95 +0,641 [0,218; 1,065] ms.
SYM cooldown: +0,155 [−0,048; 0,358] ms, chưa phân giải. SYM tự do:
K2 đổi 46,9 lần/1000 epoch, SC 12,4 (khoảng 3,8 lần).

Phát hiện khám phá trên cùng thế giới 94/95: SC đo B tươi (SYM) giảm khoảng
2,986 ms so SC FIX; K2 FIX cải thiện 1,746 ms so SC FIX; K2 FIX vẫn chậm hơn
SC SYM khoảng 1,239 ms. Đây là so sánh hậu kiểm trong R1; CI ghép cặp mới
được lưu ở reproduction_contrasts.csv, không chọn thành metric chính.
Nâng độ tươi có lợi hơn đổi luật trong kịch bản này, chưa khái quát mọi mạng.

Ba câu hỏi cho GVHD:

1. NARROW (mô tả vùng hiệu ứng lớn ở FIX, α chặt) hay PIVOT (ngưỡng tĩnh gần
   K2 khi đo đối xứng; ưu tiên độ tươi)?
2. Delay trung bình có phản ánh đúng VoIP ở vùng này; có cần báo loss theo K3?
   Chưa thay metric/ứng dụng; số G.711/PLC trong nguồn chưa kiểm ITU ở lượt này.
3. Có sửa FF thêm trí nhớ theo protocol/seed mới hay giữ là limitation?

Tham chiếu: results/gocheck/REPRODUCTION_REPORT.md, fresh_output.txt,
info_outcome_output.txt và hai output posthoc. DP0 do tác giả/GVHD quyết định.
