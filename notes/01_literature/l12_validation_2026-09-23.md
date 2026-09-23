# Lesson 1.2 — kết quả chạy và đối chiếu B6 (2026-09-23)

## Kết quả đo từ dữ liệu lưu trong repo

| Phép kiểm | Kết quả |
|---|---:|
| Protocol commit | `99fb868`, 2026-09-23 18:25:15 +07:00 |
| Truy vấn formal F sau protocol | 12; đủ ba số ở cả 12 dòng |
| Lượt kết quả / qua tiêu đề / qua abstract | **74 / 25 / 15** |
| Lượt web thăm dò trước protocol thiếu tổng đếm | **9**; ghi `—`, không thay bằng số giả |
| OpenAlex citation metadata đã xuất CSV | **582** dòng: 31+389 cho Guérin–Orda, 63+99 cho Ornee–Sun |
| References PDF đã xuất CSV | **52** mục: OpenTwin 35, El Halabi–Brandt 17 |
| Start set có backward + forward đã thử | **4/4** họ A, F, E, D; forward F/E trả 0 mục indexed trên OpenAlex |
| Mục giữ đọc tiếp sau snowball vòng 0 | **33 lượt**, có thể trùng, chưa sàng abstract đầy đủ |
| Evolution map | **8/8** mũi tên có limitation và nguồn ở cùng dòng |
| Ghi chú ưu tiên 1–5 | **5/5** ghi hai lượt đối chiếu nguồn; mức full text ghi riêng từng file |
| Workbook | **9** sheets, `Novelty Matrix` **36 hàng × 12 cột**, có cột `Đã kiểm full text (ngày, §)` và họ E/F |

Cách đo: đọc `screening_formal_2026-09-23.csv` để cộng cột `title_pass`, `abstract_pass`; đếm dòng trong hai CSV snowball; đọc bảng F trong `search_log.md`; mở sheet `Novelty Matrix` bằng `openpyxl`. Đây là số bản ghi theo truy vấn/nguồn, chưa khử trùng lặp giữa các truy vấn hoặc giữa các citation index.

## B6: điều kiện đạt và điều kiện còn thiếu

| Điều kiện | Trạng thái | Bằng chứng / việc còn lại |
|---|---|---|
| Commit protocol sớm hơn **mọi** dòng log | **Chưa đạt, không thể sửa hồi tố** | Chín truy vấn web thăm dò và chín truy vấn arXiv API A đã diễn ra trước commit. Riêng 12 truy vấn formal F chạy sau `99fb868`. Không đổi ngày hay tạo commit giả. |
| Mỗi chuỗi tìm đủ ba số | **Formal đạt; toàn bộ log chưa đạt** | F1–F12 và A1–A9 có ba số; Q1–Q9 web thăm dò không có tổng do công cụ không trả. |
| Snowballing bốn họ và lý do dừng | **Đã chạy vòng 0, chưa bão hòa** | Bốn start set có backward/forward trong log; dòng lý do tạm dừng và backlog 33 lượt. Forward của hai preprint mới chưa được OpenAlex lập chỉ mục. |
| Paper ưu tiên 1–5: ghi chú ≥2 lượt, tự viết | **Ghi chú và đối chiếu nguồn đạt; tiêu chí tự viết cần tác giả thực hiện** | Năm file `notes/` có mốc lượt 2, nhưng không thể ghi nhận việc tác giả tự viết khi tác giả chưa trực tiếp đọc và viết lại. |
| Mọi mũi tên có limitation + nguồn | **Đạt** | `evolution_map.md`: 8 dòng có cạnh, limitation, nguồn. Cạnh là bước chuyển bài toán, không gán quan hệ trích dẫn chưa kiểm. |
| Matrix có họ E/F + cột kiểm full text | **Đạt** | `novelty_matrix.xlsx`, sheet `Novelty Matrix`, cột L; ghi § cụ thể hoặc `Chưa` theo đúng mức đọc. |

**Kết luận:** Lesson 1.2 chưa thể đánh dấu hoàn thành toàn bộ B6. Đợt formal đã được đăng ký trước và đo đủ phễu; vẫn cần sàng backlog snowball, kiểm PDF/proof CERT và phần Appendix liên quan, cùng lượt đọc/viết độc lập của tác giả. Chưa kết luận novelty hoặc DP1.

## Đường dẫn bằng chứng

- `search_protocol.md`: quy tắc và commit trước F1–F12.
- `search_log.md`: chuỗi tìm, phễu từng chuỗi, bảng snowball và lý do dừng.
- `screening_formal_2026-09-23.csv`: 74 kết quả kèm quyết định sàng lọc.
- `snowball_openalex_2026-09-23.csv`: 582 citation metadata.
- `snowball_pdf_references_2026-09-23.csv`: 52 tham khảo PDF.
- `notes/`: ghi chú ưu tiên và đối thủ mới (CERT, LEC).
- `evolution_map.md` và `novelty_matrix.xlsx`: tổng hợp giới hạn và so sánh novelty.
