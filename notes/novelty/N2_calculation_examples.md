# L1.3 — Bài tính đối chiếu (Codex, không phải bài tự làm của tác giả)

Tính từ bốn số đã làm tròn trong lesson: y00=0,355; y10=3,156;
y01=3,671; y11=4,562 ms. Không dùng làm dự đoán mù; các số đã được cung cấp.
Tệp này được ghi sau lần chạy local, không xác nhận tác giả tính trên giấy trước khi chạy.

| Thứ tự | Phần S (ms) | Phần M (ms) | Tổng (ms) |
|---|---:|---:|---:|
| S → M | 3,156−0,355=2,801 | 4,562−3,156=1,406 | 4,207 |
| M → S | 4,562−3,671=0,891 | 3,671−0,355=3,316 | 4,207 |

Tương tác: 4,562−3,156−3,671+0,355=−1,910 ms.
Shapley(S)=(2,801+0,891)/2=1,846 ms.
Shapley(M)=(1,406+3,316)/2=2,361 ms; tổng=4,207 ms.
Đây là Shapley **hai nguồn, giữ P=0**, khác phân rã **ba nguồn** trong output n02.

Ví dụ tự tạo không tương tác: y00=0,5; y10=2,5; y01=3,5; y11=5,5.
Cả hai thứ tự cho S=2 và M=3 ms; tương tác=5,5−2,5−3,5+0,5=0.

Số local có khác lesson ở các nhánh dùng quan sát tức thời W=1e-6.
Xem n02_report.md để tránh trộn số minh hoạ làm tròn ở đây với số đo local.
