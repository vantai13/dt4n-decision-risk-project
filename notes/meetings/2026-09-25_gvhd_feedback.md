# Nhận xét của GVHD — 2026-09-25

> Nguyên văn nhận xét bằng văn bản tác giả nhận được; lưu không chỉnh sửa. Quyết định rút ra: `../02_decision_log.md`.

Ba lo ngại, nói thẳng.

1. Em đang sở hữu quy trình nhưng chưa sở hữu lý thuyết. Brief, definitions, protocol, memo và P02–P05 đều do AI soạn. Chỉ cần hội đồng hỏi "vì sao xếp theo p+/p−?" là lộ. Đây là rủi ro số 1. Chuỗi bài học bên dưới được thiết kế để xử lý đúng chỗ này.
2. Hồ sơ đang phình. Decision log 39 KB, 23 quyết định K, 13 baseline, 6 claim confirmatory, trong khi chưa có một kết quả thực nghiệm nào. Đây chính là bài học dt4n mà em đã tự ghi "không lặp lại".
3. Metric chính có vấn đề construct validity. Mình giải thích ở K2 ngay dưới đây.

Mục	Quyết định	Lý do ngắn
K2 — mục tiêu	Sửa. Giữ ràng buộc harm ≤ α trên mọi epoch và cách hiệu chỉnh KKT. Đổi đại lượng được tối ưu từ số lần bỏ lỡ sang ms cải thiện kỳ vọng.	Chi tiết ngay dưới
K3 — loss	Đồng ý tách nhãn, với 2 điều kiện: (i) δ ≥ độ phân giải đo (1/số probe); (ii) δ phải có nguồn. Ứng viên nguồn: ITU-T Y.1541, theo mình nhớ đặt IPLR 10⁻³ cho lớp thời gian thực. Em phải mở chuẩn để xác nhận.	Không có con số thiếu nguồn trong kết quả chính
K21 — κ	Thay κ bằng c_switch đơn vị ms. Kết quả chính dùng c = 0; độ nhạy c ∈ {0,25; 1}·S. Switch rate và flap báo ở tầng trajectory.	κ = 0,01 có đơn vị "sự kiện missed mỗi lần đổi", không neo vào vật lý
K14/K20 — thực tế ngoài họ	Đồng ý X1′ (token bucket trong DES) cho sai mô hình hàng đợi. Thêm X2 (tải dựng từ trace thật) cho sai mô hình traffic, nếu F1 tìm được chuỗi thời gian. Mininet chỉ xác nhận ≤ 2 cấu hình và là mục cắt đầu tiên.	OU là giả định yếu nhất; X1′ không kiểm được giả định đó
Scope	Tầng 1 (bắt buộc cho NCKH): RQ1 + RQ1-op, 16 ô. Tầng 2: RQ2 trong cùng chế độ + X1′. Tầng 3 (paper): dịch chuyển chế độ, ACI, M2, H2, Mininet.	NCKH thành công khi RQ1 làm tốt; RQ2 là phần thưởng
SESOI	Hôm nay chốt quy tắc, DP0 mới chốt con số. Một khoảng cách chỉ được gọi là có ý nghĩa khi vượt cả hai: sàn tuyệt đối (ms, có lý do ứng dụng) và tỉ lệ tương đối của headroom E[(I_D − c)⁺].	Chốt quy tắc trước khi có dữ liệu thì không bị nghi chỉnh theo kết quả
"Stale"	Đổi framing ngay thành "stale and noisy telemetry".	Nhiễu đếm là một cơ chế trong mô hình (e04 có biến thể "chỉ nhiễu đếm"); đổi sớm rẻ hơn đổi muộn
Hồ sơ (K23)	Đồng ý, và siết thêm: đóng băng tài liệu Phase 0; thêm một bảng "trạng thái K1–K23" ở đầu decision log; không ADR mới cho tới DP0.	Thời gian chuyển sang học và làm
Lịch	Đề nghị lùi DP0 sang 20/10 và gộp với DP1, có một mốc kiểm tra giữa kỳ ngày 13/10.	Em cần thời gian tự dẫn lý thuyết; đây không phải chậm
Hiểu bài	Điều kiện cứng: không dòng nào vào ndtrisk/ nếu em chưa tự dẫn được công thức và giải thích được từng dòng. Elevator test (G2) với người thật trong tuần này.	Rủi ro số 1 ở A2

## Vì sao mình sửa K2

Xét hai quyết định, cả hai có p+ = 0,9 và p− ≈ 0:

Quyết định P cải thiện kỳ vọng 0,7 ms.

Quyết định Q cải thiện kỳ vọng 30 ms.

Với mục tiêu (b), bỏ lỡ P và bỏ lỡ Q bị phạt như nhau: mỗi cái là "1 missed". Người dùng VoIP thì chỉ cảm nhận được Q. Reviewer mạng chắc chắn sẽ hỏi: "missed giảm 2 điểm %, vậy là bao nhiêu ms?" Nếu câu trả lời là 0,01 ms thì phát hiện của em vô nghĩa thực tế, mà metric (b) lại che mất điều đó. P04 đã có tín hiệu cảnh báo sớm: delay 4,6311 so với 4,6310 (thế giới đồ chơi, chưa kết luận được gì).

Vì vậy mình đề nghị mục tiêu (d):

```text
max  E[ a·I_D ] − c·E[a]      với ràng buộc   E[ a·1{I_D < −ε} ] ≤ α   (mẫu số: mọi epoch)
Luật tối ưu (Lagrange / fractional knapsack):   đổi ⇔ E[I_D | F] − λ·p− > c,   λ ≥ 0 nhỏ nhất đạt ngân sách
```

Mục tiêu này có ba ưu điểm:

Metric có đơn vị ms. λ đọc được: "số ms kỳ vọng sẵn sàng bỏ ra để tránh một lần đổi gây hại".

Nó chứa (a) như trường hợp đặc biệt. Khi α → ∞ thì λ = 0 và luật thành E[I|F] > c. Một lần quét α trả lời cả nhà vận hành "an toàn trước" lẫn nhà vận hành "delay trung bình". Câu hỏi "sao không tối ưu delay trung bình?" có câu trả lời chính là điểm cuối của đường cong.

H1 vẫn là đối chứng hợp lệ. Với họ tịnh tiến, điểm E[I|F] − λp− đơn điệu theo Î, nên ngưỡng cố định vẫn tối ưu.

Cái giá: đuôi nặng hơn, nên có thể cần nhiều seed hơn. Revisit when: F3 cho thấy cần hơn 30 seed để phân giải SESOI thì quay về (b) với κ = 0.

Nguyên tắc em phải nhớ: mình chọn (d) vì nó đo đúng thứ người dùng quan tâm, không phải vì nó làm phương pháp của em thắng. Nếu em chọn mục tiêu theo kỳ vọng kết quả, đó là p-hacking ở tầng thiết kế.

Nếu em nhận (d), cần cập nhật:

- ADR K2 và memo mục tiêu.
- Definitions: thêm gain_ms, headroom_ms; recovery_ratio tính theo ms.
- K17: định nghĩa lại chỉ số đảo thứ tự trên điểm E[I|F] − λp− tại λ vận hành, và thêm ứng viên thứ ba ở mục 5 phần A4.

## A4. Sai sót kỹ thuật mình tìm được

Lỗi số học (quan trọng cho nền móng). Cách giải bằng ma trận, dùng trong P05 và trong đính chính, cho loss âm ở buffer sâu. Với K = 100: ρ = 0,8 cho −5,3×10⁻¹⁵ trong khi đúng là 5,2×10⁻²⁰; ρ = 0,5 cho −8,9×10⁻¹⁶. Vẽ log(loss) sẽ ra NaN. Lesson 1 sửa bằng phương trình lát cắt.

"Knee" chưa nhất quán. Hai định nghĩa trong plan cho kết quả khác xa nhau ở K = 11:

- "loss vượt 0,1%" cho knee ≈ 0,76;
- "dW/dρ cực đại" cho knee ≈ 0,985.

Ở K = 100 hai định nghĩa cho 0,99 và 1,00. Đề nghị: không dùng "knee" làm biến. Dùng Π_knee = σ/(1 − ρ̄), tức khoảng cách tới bão hoà tính theo σ, vốn đã có trong definitions.

Π_noise dùng z_eff trong công thức phương sai, trái với chính quy tắc "z_eff chỉ cho kỳ vọng" của em. Vẫn dùng được, nhưng phải ghi rõ là "chỉ số bậc độ lớn".

Nhãn trong DES nên tính bằng tích phân chính xác. V(t) tuyến tính từng khúc, nên delay trung bình và loss trên khoảng giữ tính được chính xác bằng tích phân. Theo PASTA, cách này tương đương vô hạn probe Poisson: không còn nhiễu lấy mẫu probe, và vấn đề độ phân giải δ ở K3 biến mất. Probe lấy mẫu chỉ giữ để so với Mininet. (Việc của L3.5.)

Chỉ số H2. Spearman trên toàn bộ tập đo thứ tự toàn cục, trong khi khoảng cách chỉ phụ thuộc thứ tự gần biên quyết định. Đề nghị ứng viên thứ ba, self_gap_twin: twin dùng chính p±, E[I|F] của nó để tính lợi ích của luật NP so với ngưỡng tĩnh tốt nhất ở cùng ngân sách. Nói cách khác, twin tự dự báo giá trị của việc thích nghi.

Dưới M0, chỉ số này đúng theo cấu trúc, nên đó là verification.

Dưới X1′ và X2 nó mới cho thông tin. So cả ba chỉ số ở DP0 bằng seed pilot.

Hàng xóm còn thiếu. Burbano et al. 2025 (arXiv 2511.10146), cùng nhóm với Liyanage. Bài này kết hợp dự đoán latency với độ tin cậy thích nghi và handover có hysteresis, dùng đo thụ động (tốc độ đến, utilization, kích thước payload) cùng một mô hình delay. Rất gần với phần "ρ̂ → mô hình delay → hysteresis" của em. Thêm vào danh sách DP1; cần đọc full text để xác nhận mức gần.
