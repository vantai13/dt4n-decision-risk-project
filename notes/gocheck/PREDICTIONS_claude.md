Nguồn: Chép từ sandbox Claude; theo tài liệu người dùng cung cấp, khóa ở commit 1a66a24, 16:07:05 (giờ sandbox); outcome bắt đầu chạy 16:07:11. Múi giờ và commit sandbox chưa được kiểm độc lập tại repo local.

# Dự đoán của Claude (AI) — viết và commit TRƯỚC khi mở seed 92001–95020

Bối cảnh: tác giả chọn không tự dự đoán ("bạn hãy tự dự đoán và tiếp tục chạy") → LỆCH NT-1.
Dự đoán dưới đây là của AI, KHÔNG phải của tác giả. Claude chưa thấy kết quả SYM/FF nào
(smoke test trước đó dùng seed 99001/99101, n = 2, output đã xoá mà không đọc).

## A. Lặp FIX (rollout, α = 0,2%, cooldown 0) — rollout fresh 92/93 VÀ dòng FIX của Bước 2 trên 94/95
- Điểm ≈ +1,5 ms; khoảng 90% [0,9; 2,3] ms cho MỖI lần lặp
  (go0 ± √2·h = [1,05; 2,26], nới rộng vì tune lại ngưỡng, dịch nhẹ xuống vì winner's curse).
- Hai lần lặp lệch nhau ≤ 0,8 ms.
- α = 1%: CI chứa 0; |SC−K2| < 0,1 ms (tự tin cao).
- Cooldown 30 s: điểm ≈ +0,45 ms, khoảng [0,0; 1,0]; xác suất CI không chứa 0 ≈ 0,7.

## B. SYM (cả hai path đo 1 s) — mức "gần 0"
- SC−K2: điểm ≈ +0,05 ms, khoảng [−0,05; 0,2].
- Lý do: path hiện tại tươi → Ī mất phần đuôi quá tải của path cũ; thông tin tốt ở cả hai phía → SC giữ harm thấp
  với ngưỡng thấp → ràng buộc harm gần như không chạm → λ ≈ 0 → K2 ≈ SC. Mốc: R1_TB1 (decision-level) 0,148 ms;
  rollout đã hai lần nhỏ hơn decision-level.
- Delay thấp nhất cho cả hai luật: SYM (nhiều thông tin nhất); SC, K2 ∈ [2,3; 3,5] ms.

## C. FF (path đang mang luồng đo 1 s) — mức "nhỏ"
- SC−K2: điểm ≈ +0,3 ms, khoảng [0,0; 0,8]; xác suất CI không chứa 0 ≈ 0,5.
- Lý do: đích luôn cũ → mất nhóm "đích tươi và rảnh"; nhưng tuổi của đích dao động 0,1–60 s, nên ở cùng Ī,
  p₋ vẫn khác nhau ("đích cũ nhưng vừa báo rảnh", cơ chế (a)) → còn lại một phần lợi thế.

## Thứ hạng và hiệu-của-hiệu (α = 0,2%, cooldown 0)
- SC−K2: FIX > FF > SYM.
- (SC−K2)_FIX − (SC−K2)_SYM ≈ +1,4 ms, CI không chứa 0 (tự tin cao).
- (SC−K2)_FIX − (SC−K2)_FF ≈ +1,1 ms, CI không chứa 0 (tự tin vừa).
- SYM và FF ở α = 1% và ở cooldown 30 s: |SC−K2| < 0,15 ms.

## Bất ngờ nếu — và kiểm gì trước
1. FIX lặp lại < 0,8 ms hoặc CI chứa 0 → go0 may mắn / winner's curse lớn; kiểm hai lần lặp có khớp nhau.
2. SYM > 0,5 ms → cơ chế (b) (sàn/knee) mạnh hơn tôi nghĩ; kiểm harm của SC có chạm α không.
3. FF ≥ FIX → "đích tươi" không phải cơ chế chính; xem lại phân rã cơ chế.

Mức tự tin chung: vừa (A cao; B vừa–cao; C thấp–vừa).
