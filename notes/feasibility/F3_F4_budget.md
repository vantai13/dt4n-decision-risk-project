# F3/F4 — Cỡ mẫu, chi phí DES và quyết định sau f04b

> Feasibility, ngày 2026-09-27. Preregister tại commit `cdcea06` trước khi chạy `power` và `outcome`.
> Đây là spike định hướng, không phải kết quả confirmatory RQ1/RQ2.

## 1. Cỡ mẫu

Với mục tiêu quan sát ít nhất 100 sự kiện harm, số epoch tối thiểu là `ceil(100/α)`; mỗi seed có 1.500 epoch:

| α | Epoch tối thiểu | Seed tối thiểu |
|---:|---:|---:|
| 0,5% | 20.000 | 14 |
| 1,0% | 10.000 | 7 |
| 2,0% | 5.000 | 4 |

Tại `α=1%`, 8 seed test cho 12.000 epoch, kỳ vọng 120 sự kiện. Power theo độ phân tán thực đo:

| Ô | Thế giới | sd_seed(gap), ms | Seed cho ±4,05 ms | Seed cho ±1 ms |
|---|---|---:|---:|---:|
| P1 | DES / PSA | 0,020 / 0,011 | 3 / 3 | 3 / 3 |
| P2 | DES / PSA | 0,478 / 0,641 | 3 / 3 | 4 / 5 |
| K100, ρ̄=0,85, σ=0,10, τ=2 | DES / PSA | 0,168 / 0,488 | 3 / 3 | 3 / 4 |
| K100, ρ̄=0,95, σ=0,03, τ=10 | DES / PSA | 0,195 / 0,151 | 3 / 3 | 3 / 3 |

Kiểm tay tại P2 DES: với `n=3`, `t₀.₉₇₅,₂·sd/√n = 4,303×0,478/√3 = 1,19 ms < 4,05 ms`,
nên 3 seed đủ cho SESOI. Với đích ±1 ms, `n=3` chưa đủ (`1,19 ms`), còn `n=4` cho
`3,182×0,478/2 = 0,76 ms`, khớp script. Đơn vị suy luận vẫn là seed; ACF của `(I)⁺` lên tới 0,866 dù ACF
đóng góp gap chỉ từ −0,037 đến 0,102.

## 2. Engine và ngân sách CPU

Numba trùng từng bit với Python thuần, đạt 123,1 triệu gói/s và khớp nghiệm `mdk.py` trong CI ở mọi đại lượng đủ
sự kiện. Một ô 215 seed tốn khoảng 14–15 s mô phỏng; 16 ô khoảng 0,06–0,07 CPU-giờ, chưa gồm đánh giá.

Oracle nested MC một ô với `16×1500` epoch, `M_ngoài=200`, `M_trong=50` và khoảng 1.730 gói/quỹ đạo cần
`24.000×10.000×1.730 ≈ 4,15×10¹¹` gói. Ở tốc độ đo được, kernel mất khoảng 3.374 s = 0,94 giờ/ô;
16 ô khoảng 15 giờ = 0,63 CPU-ngày chỉ riêng kernel. Cộng overhead Python, ngân sách thực tế cỡ 1–2 CPU-ngày,
vẫn dưới ngưỡng 3 CPU-ngày nhưng không phù hợp để quét rộng.

## 3. Phân rã PSA so với DES

| Ô | Thế giới | Thích nghi | An toàn | Thông tin | Headroom | Phán quyết |
|---|---|---:|---:|---:|---:|---|
| P1 | DES / PSA | −0,010 / 0,002 | 0,001 / 0,000 | 1,498 / 0,318 | 1,513 / 0,339 | đều không đáng kể |
| P2 | DES / PSA | 0,149 / 1,150 | 1,289 / 8,042 | 9,418 / 24,348 | 14,556 / 37,699 | đều không đáng kể |
| K100, ρ̄=0,85, σ=0,10, τ=2 | DES / PSA | 0,215 / 0,558 | 0,786 / 2,501 | 3,435 / 7,987 | 5,706 / 12,973 | đều không đáng kể |
| K100, ρ̄=0,95, σ=0,03, τ=10 | DES / PSA | 0,082 / 0,093 | 0,372 / 0,626 | 9,637 / 10,032 | 11,204 / 11,202 | đều không đáng kể |

Đối chiếu prereg: Q1, Q2, Q4 và Q5 đúng. Q3 sai: gap DES tại P2 là `0,149±0,400 ms`, không thuộc khoảng
1–4 ms đã dự đoán. Các hiệu DES−PSA có CI loại trừ 0 gồm: thông tin tại P1; cả ba khoảng tại P2; an toàn và
thông tin tại ô K100/0,85/0,10/2. Không có hiệu nào phân giải được tại ô K100/0,95/0,03/10.

## 4. Quyết định theo luật đã khóa

Cả bốn ô đều “KHÔNG ĐÁNG KỂ”; không có ô “CHƯA KẾT LUẬN”. Theo luật 3, đề xuất **PIVOT: ngưỡng tĩnh đủ,
và vì sao**. Trong DES, khoảng thích nghi luôn nhỏ nhất; tại P2 phần mất mát chủ yếu là thông tin (`9,418 ms`),
sau đó là an toàn (`1,289 ms`), còn thích nghi chỉ `0,149 ms`. Không thêm seed để cứu một hiệu ứng thấp hơn SESOI
hơn 50 lần. Theo luật 4, PSA không được dùng làm bằng chứng định lượng cho các khoảng có hiệu ghép cặp nêu trên.

**Provenance:** Codex thực hiện code, dự đoán được ủy quyền, chạy và diễn giải; tác giả chưa được ghi nhận là đã tự
tính hoặc tự viết các phần này. Cần tác giả tự tái lập phép tính cỡ mẫu và giải thích bảng trước khi vấn đáp.
