# Seshadri & Katz 2003 — Động học của định tuyến overlay đồng thời

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | Dynamics of Simultaneous Overlay Network Routing |
| Tác giả (đúng thứ tự của PHIÊN BẢN đang đọc) | Mukund Seshadri; Randy H. Katz (UC Berkeley) |
| Nguồn | Technical Report UCB/CSD-03-1291, 11/2003 (www2.eecs.berkeley.edu/Pubs/TechRpts/2003/CSD-03-1291.pdf) |
| Trạng thái | technical report, không qua bình duyệt |
| Lượt đã đọc | 2 — toàn văn §I–VII, Fig. 1–18 (đọc số trên trục và chú thích) |
| Ngày đọc | 2026-09-27 — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | thấp cho RQ1 (chế độ tập thể, metric băng thông/mất gói); cao cho mọi claim "H tối ưu phụ thuộc tham số" hay "H thích nghi" — không được claim |

Nhãn: [F] paper nói trực tiếp (có §/tr.) · [I] suy ra (ghi suy từ đâu) · [?] chưa kiểm

## 0. Five Cs (sau lượt 1)

- Category: nghiên cứu mô phỏng.
- Context: overlay routing (RON, i3, PlanetLab); Mitzenmacher về thông tin cũ trong cân bằng tải (§II-A).
- Correctness: mô phỏng mức luồng, không mức gói (§III); metric băng thông khả dụng; thêm nhiễu đo 10% (§IV, Fig. 1).
- Contributions (§I): tác động của đổi đường tham lam; ba dạng "kiềm chế"; thuật toán dò H kiểu MIMD; phân tích luồng gian lận.
- Clarity: tốt; có CI 95% qua 10 lần chạy (§III).
- Quyết định: lượt 2 đủ.

## 1. Một câu: paper làm gì?

Mô phỏng ~1000 luồng overlay độc lập chia sẻ nút cổ chai cho thấy đổi đường tham lam gây bất ổn, rằng H tối ưu phụ thuộc
mạnh vào tham số hệ thống, và rằng ngẫu nhiên hoá hay H tự điều chỉnh (MIMD) giảm mất gói ít nhất một nửa.

## 2. Problem · Assumptions

- Problem [F §III]: mỗi luồng gửi trên đường hiện tại, đo các đường khác; mỗi T_r (mặc định 10 s) quyết định giữ hay đổi.
- A1 [F §IV]: đổi nếu băng thông khả dụng của đường tốt nhất lớn hơn đường hiện tại một hệ số H (hysteresis nhân).
- A2 [F Fig. 1]: mặc định ~1000 luồng, 50 link cổ chai, P_f = 25 đường/luồng, cross-traffic 50% dung lượng, nhiễu đo 10%.
- A3 [F §III]: luồng không trao đổi quyết định; đến/đi ngẫu nhiên; tải chọn sao cho về lý thuyết định tuyến được không mất gói.

## 3. Method

Mô phỏng mức luồng với metric mất gói trung bình sau khởi động. Quét H, tốc độ đến của luồng (IAT), P_f, T_r, tỉ lệ
cross-traffic. So GREEDY với ba biến thể ngẫu nhiên (ARAND, GRAND, SRAND — chọn tốt nhất trong K_s đường lấy ngẫu nhiên)
và với MIMD-H: tăng H nhân khi vừa đổi, giảm nhân khi một cửa sổ trôi qua không đổi (Fig. 12). Theo ngôn ngữ đề tài:
MIMD-H là một **ngưỡng thích nghi theo tần suất đổi**, không phải luật dùng bất định từng quyết định [I].

## 4. Evaluation

| Setup (topology/testbed/data) | Baseline | Metric | Kết quả chính (có số) | §/tr. |
|---|---|---|---|---|
| Mô phỏng mức luồng, tham số Fig. 1; 10 lần chạy, CI 95% | GREEDY với H khác nhau | mất gói TB; số lần đổi | mất gói theo H hình chữ U; H tốt nhất ở mặc định = 8,75 | §IV, Fig. 2–4 |
| Quét IAT, P_f, T_r | GREEDY | mất gói | H tối ưu đổi mạnh theo IAT, P_f, T_r | Fig. 4, 5, 8 |
| Quét cross-traffic | GREEDY, H = 8,75 | mất gói | chạy khá tốt khi cross-traffic > 75% | §IV, Fig. 6 |
| Ngẫu nhiên hoá | GREEDY | mất gói | SRAND giảm mất gói ~một nửa, chỉ cần đo K_s trong P_f đường | §V-A, Fig. 9–11 |
| Dò H | GREEDY | mất gói | MIMD-H giảm ít nhất một nửa, thường < 1% | §V-B, Fig. 13–15 |
| Luồng gian lận | MIMD-H, SRAND | mất gói | gian lận chỉ có lợi nhỏ khi < 10% số luồng | §VI, Fig. 16–18 |

## 5. Claim ↔ Evidence

| # | Claim của tác giả | Loại evidence | Evidence thật sự phủ tới đâu | Khe hở? | §/tr. |
|---|---|---|---|---|---|
| 1 | Đổi tham lam không kiềm chế rất bất ổn | mô phỏng | Chế độ tập thể, luồng overlay chiếm phần lớn tải | Không | §IV, Fig. 2–3 |
| 2 | H tối ưu phụ thuộc mạnh tham số hệ thống | mô phỏng | Quét IAT, P_f, T_r | Không | Fig. 4, 5, 8 |
| 3 | GREEDY với H cố định có lẽ đủ nếu luồng overlay nhỏ so với link | mô phỏng + lập luận ("we believe") | Một đường cong theo cross-traffic | Có — rào đón, một chiều quét | §IV, Fig. 6 |
| 4 | MIMD-H tốt hơn H cố định | mô phỏng | Mặc định + quét P_f, IAT | Mô hình mức luồng | §V-B |

## 6. Limitation

- Tác giả tự nêu [F]: mô hình đơn giản hoá, không mức gói (§III); cần topology/tải thật hơn và cross-traffic động hơn (§VII).
- Tôi thấy [I]: metric băng thông/mất gói, không delay; thông tin "cũ" chỉ đến từ việc luồng khác đổi trong cửa sổ đo cộng
  nhiễu 10%, không mô hình tuổi; không có luật dùng phân phối; không oracle.

## 7. So với đề tài của tôi

- Trùng: đổi/giữ đường với ngưỡng hysteresis H; đo bị nhiễu; đường hiện tại làm mốc.
- Khác, ĐÃ KIỂM (§/tr.): chế độ tập thể, luồng chiếm phần lớn tải (§III, §IV); metric mất gói (§III); không luật dùng bất
  định từng quyết định (§IV–V); không oracle.
- Khác, CHƯA KIỂM / suy luận: kết quả Fig. 6 gợi ý rằng trong chế độ một luồng nhỏ thì H cố định đủ — đúng giả thuyết đề
  tài đo; họ không đo khoảng cách tới oracle [I].
- Dùng được: MIMD-H làm baseline "ngưỡng thích nghi" (protocol đã liệt kê MIMD); câu Related Work; lập luận phạm vi.

## 8. Câu định vị

"Seshadri–Katz cho thấy trong định tuyến overlay tập thể, H tối ưu phụ thuộc mạnh vào tham số và nên tự điều chỉnh
(Fig. 4–5, §V-B), còn GREEDY với H cố định chạy tốt khi luồng overlay chỉ là phần nhỏ của tải (Fig. 6); đề tài đo đúng
chế độ sau — một luồng nhỏ, tải ngoại sinh — và hỏi một câu họ không hỏi: luật dùng bất định từng quyết định có hơn một
ngưỡng được tune không, so với oracle cùng thông tin."

## 9. Câu hỏi còn mở

- Forward citation (openalex_l19): có bài nào đo hysteresis vs luật dùng bất định trong chế độ luồng nhỏ không?
- Mitzenmacher 2000, Dahlin 2000 chưa đọc; mô tả hiện có chỉ là nguồn thứ cấp (§II-A bài này; §1.5 Fischer–Vöcking).
