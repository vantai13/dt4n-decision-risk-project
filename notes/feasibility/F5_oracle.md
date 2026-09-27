# F5 — Độ mạnh oracle và tuổi dao động

> Feasibility, ngày 2026-09-27. Validity commit `1b84fa2`; prereg commit `9056ac1`; outcome chỉ chạy sau đó.
> Dự đoán và diễn giải trong repo do Codex soạn theo ủy quyền, không phải phần tác giả tự viết.

## Kết quả và quyết định

| Ô/chế độ | Oracle | Gap K2−S0 | Tâm SC−S0 | Thuần K2−SC | Phán quyết |
|---|---|---:|---:|---:|---|
| P2/A0 | F20x2 | +0,135±0,348 | +0,048±0,370 | +0,086±0,114 | Không đáng kể |
| P2/A1 | F20x2 | +0,560±0,383 | +0,558±0,323 | +0,002±0,139 | Không đáng kể |
| P2/A1 | FZ10x5 / FZ20x3 | +0,278±0,401 / +0,662±0,344 | +0,400 / +0,508 | −0,122 / +0,154 | Không đáng kể |
| K100/0,95/0,03/10/A0 | F20x2 | +0,099±0,155 | +0,099±0,155 | 0,000±0,000 | Không đáng kể |
| K100/0,95/0,03/10/A1 | F20x2 | −0,103±0,134 | −0,103±0,134 | 0,000±0,000 | Không đáng kể |
| K100/0,95/0,03/10/A1 | FZ10x5 / FZ20x3 | −0,243±0,073 / −0,016±0,175 | −0,313 / −0,043 | +0,070 / +0,027 | Không đáng kể |

Mọi oracle đếm F/FZ đều “KHÔNG ĐÁNG KỂ”; luật 1 được kích hoạt: **PIVOT vững trong phạm vi đã thử** (tuổi cố
định/dao động, bin 10–40, dữ liệu oracle ×2). Không có trường hợp “CHƯA KẾT LUẬN”, nên luật 2–3 không kích hoạt.
Q20x2 cũng không có ý nghĩa, nên luật 4 không kích hoạt; tuy vậy gap của Q lớn hơn rõ rệt và được giữ như hướng
telemetry hàng đợi, không phải kết quả RQ1.

## Đối chiếu Q1–Q5

**Q1 — đúng.** Độ lệch cực đại so với F20 chỉ `0,315 ms` tại P2 và `0,183 ms` tại ô τ=10 s, đều dưới dự đoán
`0,5 ms` và tiêu chí `m/2=4,05 ms`. Oracle đếm ổn định theo độ mịn/dữ liệu, nên kết quả âm không phải artefact rõ
ràng của lưới 20×20; tuy nhiên tiêu chí DP0 vẫn thô hơn gap quan sát một bậc độ lớn.

**Q2 — sai một phần.** Tại P2/A0 F20x2, phần thuần `0,086 ms` lớn hơn tâm `0,048 ms`; tại ô τ=10 s, tâm
`0,099 ms` và thuần đúng 0. Không có quy luật “tâm luôn lớn hơn” ở A0, nhưng cả hai thành phần đều rất nhỏ và CI
của phần thuần chứa 0, nên chưa có bằng chứng rằng dùng độ rộng tạo giá trị thực dụng.

**Q3 — đúng.** Q20x2 tăng `K2(∞)−S0` lên `5,972 ms` tại P2 và `4,773 ms` tại ô τ=10 s, so với F20x2 lần lượt
`1,480` và `0,558 ms`. Gap K2 của Q là `4,125±1,206` và `3,458±1,741 ms` nhưng vẫn không đạt SESOI; workload là
kênh telemetry hứa hẹn hơn, không phải bằng chứng cho claim với F chính.

**Q4 — đúng một phần.** P2 có A1−A0 dương `+0,425±0,317 ms`, còn ô τ=10 s âm `−0,202±0,191 ms`, nên dự đoán
dương ở cả hai ô sai. Dự đoán hiệu ứng lớn hơn tại P2 đúng, phù hợp với tương quan tuổi biến thiên mạnh hơn khi
τ=2 s; ở τ=10 s, `exp(−z_eff/τ)` chỉ chạy `0,890–0,935` quanh A0 `0,912`.

**Q5 — không được ủng hộ nhất quán.** Tại P2, phần thuần F20x2 là `+0,002`; FZ10x5 giảm xuống `−0,122` nhưng
FZ20x3 tăng lên `+0,154 ms`; tại ô τ=10 s, FZ tăng từ 0 lên `+0,070/+0,027 ms`. Dấu và độ lớn phụ thuộc cách bin,
mọi giá trị đều nhỏ; chưa có bằng chứng tuổi làm giá trị thuần của bất định tăng ổn định.

## Tâm so với thuần

Tỉ lệ tâm/thuần tại A0 F20x2 là `0,56` ở P2 và không xác định tại ô τ=10 s vì phần thuần bằng 0. Với A1/FZ,
tỉ lệ có dấu lần lượt là `−3,28` và `+3,30` ở P2, `−4,47` và `−1,59` ở ô τ=10 s; các tỉ lệ không ổn định vì
mẫu số gần 0 và đôi khi hai phần triệt tiêu. Điều chắc hơn là phần thuần chỉ nằm trong `−0,122…+0,154 ms`, thấp
hơn SESOI hơn 50 lần; điều chỉnh độ rộng không tạo lợi ích thực dụng trong miền đã thử.
