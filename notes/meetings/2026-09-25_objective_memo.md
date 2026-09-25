# Memo: chọn mục tiêu tối ưu (2026-09-25)

> Soạn bởi Claude (AI) theo yêu cầu tác giả, cho buổi làm việc đầu tiên với GVHD (L0.6).
> Số liệu: `experiments/pilot/p02_objective_rules.py` (pilot lý thuyết, exploratory, thế giới đồ chơi).

## Câu hỏi cần thầy quyết định

Quyết định đổi/giữ đường được đánh giá theo mục tiêu nào? Mục tiêu quyết định luật tối ưu (oracle)
và quyết định RQ2 có tồn tại hay không.

## Ba lựa chọn

| | Mục tiêu | Luật tối ưu một bước | Độ rộng bất định có đổi luật? | RQ2 thành gì |
|---|---|---|---|---|
| (a) | Delay kỳ vọng (+ chi phí đổi c) | Đổi ⇔ E[I \| F] > c | Không | Chỉ còn sửa tâm (E[I \| F] ≠ Î gần knee) |
| (b) | Missed nhỏ nhất, harm ≤ α trên MỌI epoch | Đổi ⇔ p+ − λ·p− > κ | Có | Như thuyết minh v14 |
| (c) | Missed nhỏ nhất, harm / số lần đổi ≤ α | Đổi "rẻ" luôn đổi; đổi rủi ro theo p+/(p− − α) | Có | Oracle khác (b); có thể vô nghiệm |

## Ví dụ (ε = 1 ms)

X và Y cùng Î = 4 ms; X có s = 1 ms (p− ≈ 3×10⁻⁷), Y có s = 5 ms (p− ≈ 0,16; p+ ≈ 0,73).
(a) đổi cả hai. (b) với α = 1% trên hai epoch (ngân sách 0,02): đổi X, giữ Y.

## Đề xuất của em: (b), với hai điều chỉnh

1. Hiệu chỉnh theo KKT: λ ≥ 0 nhỏ nhất để harm ≤ α; không "tiêu hết" ngân sách khi ràng buộc lỏng.
   Thế giới mạng rảnh (P02-C): tiêu hết ngân sách cho harm 1,000% và 95,64% lần đổi mà không giảm missed.
2. Giá mỗi lần đổi κ = 0,01, áp cho MỌI luật qua cùng tiêu chí missed + κ·tỉ lệ đổi (harm ≤ α).
   P02-C: tỉ lệ đổi 84,83% → 10,00%, missed +0,010 điểm %; P02-A (ràng buộc cắn): gần như không đổi.

Vì sao không chọn (c): (c) khuyến khích đổi thêm để "mua" ngân sách, và vô nghiệm khi bất định tỉ lệ với
độ lớn delay (P02-B: 0 lần đổi, missed 45,3%). Đường cong đo trên testbed (T'/T gần hằng, pilot P01) gợi ý đúng dạng đó.
Vì sao không chọn (a): khi bất định không đồng đều, (a) vi phạm ngân sách (P02-A: harm 5,24%).

## Nếu thầy chọn khác

(a): RQ2 chuyển sang sửa tâm E[I | F]; posterior-odds thành phân tích phụ.
(c): oracle đổi sang p+/(p− − α), phải báo ô vô nghiệm; gần LEC và Zhu et al. 2026 hơn, cần định vị lại.

## Câu hỏi phụ

- K3: loss là nhãn riêng, đổi gây hại về loss khi loss tăng > δ = 1 điểm % (độ nhạy 0,5 và 2); không gộp utility.
- K21: κ = 0,01 làm mặc định, báo κ = 0 để so.
