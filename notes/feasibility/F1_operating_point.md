# F1 — Điểm vận hành từ tuổi đo được

> Spike định hướng ngày 2026-09-26. Không phải kết quả RQ1/RQ2. Mọi con số được gắn nhãn **đo**, **trích dẫn**
> hoặc **giả định**; tải của dt4n là tải tự sinh nên không được gọi là đo mạng thật.

## 1. Câu hỏi và dự đoán

F1 hỏi điểm neo có tuổi đo được nằm ở đâu trong không gian Π và nguồn bất định nào chiếm ưu thế. Trước khi chạy,
dự đoán `Π_noise≈6,00>5,78`; tại 8 Mb/s tỉ số bất định p95/p05 lớn nhất ở `(σ,τ)=(0,10;2 s)` và vượt 1,10;
`Π_relax>1` tại 8 Mb/s chỉ khi `(ρ̄,τ)=(0,95;0,5 s)` hoặc `(0,95;2 s)`.

## 2. Bảng đại lượng và nhãn

| Đại lượng | Giá trị dùng | Nhãn | Ý nghĩa/nguồn |
|---|---:|---|---|
| AoI `t−t_m` | CLEAN TB 0,369 s; PROD TB 0,343 s | đo | dt4n Phase 23, cuối cửa sổ đến lúc GET |
| `W,T_poll` | khoảng 0,5003 s | đo | chu kỳ `t_source` và cửa sổ `Δcounter/Δt` |
| `d` | CLEAN 0,118 s; PROD 0,100 s | đo gián tiếp | `P05−0,05T` theo răng cưa |
| `a` | trục `{0;0,05;0,2}` s; anchor 0,05 s | giả định | dt4n không đo actuation |
| `H` | anchor bằng `T_poll` | giả định có lý do | một quyết định cho mỗi bản tin mới |
| `τ,σ` | các trục quét của f01 | giả định | dt4n chỉ có tải tự sinh |
| `C` | 4/8 Mb/s; 100 Mb/s | đo thiết kế / giả định | 4–8 là dải testbed; 100 là tham chiếu |

## 3. Tuổi: construct và mô hình

`t_source` được lấy ngay trước khi đọc counter, nên asset đo `t−t_m`, không phải tuổi từ tâm cửa sổ. Phải dùng
`z=AoI+W/2` và `z_eff=z+a+H/2`. Với mô hình `AoI=d+UT`, ước lượng nhất quán là `d=P05−0,05T`, không phải
`d=P05`. Ở CLEAN, trung bình răng cưa dự đoán lệch số đo chưa tới 1 ms. Tuy nhiên sd đo lớn hơn `T/√12` và p99
vượt `d+T`, nên mô hình thực dụng là thân răng cưa cộng đuôi stall. Đây là phân tích lại exploratory.

Không tìm thấy raw AoI trên máy hiện tại và raw không có trong git, nên chưa thể ước lượng đáng tin tỉ lệ đuôi.

## 4. Tải, M/G/∞ và Π_flow

AR(1) và M/G/∞ của dt4n đều do chính dự án sinh; chúng chỉ xác nhận bộ phát chạy đúng. Với flow arrival Poisson,
duration bất kỳ và mỗi flow phát `r_f` trên link `C`:

```text
σ²=ρ̄r_f/C,       R=ρ̄L/(CW),       R/σ²=L/(r_fW)=1/Π_flow.
```

Vì vậy tỉ lệ nhiễu/tín hiệu không phụ thuộc `C` nếu giữ nguyên hỗn hợp flow. `σ=0,03` tại 4 Mb/s tương ứng
`r_f≈4 kb/s` và khoảng 900 flow đồng thời ở `ρ̄=0,9`; kết luận L1.2 “số đo gần như toàn nhiễu” chỉ đúng cho
traffic rất mịn. OU còn yếu ở hình dạng ACF vì M/G/∞ Pareto có nhiều thang thời gian/LRD; cần kiểm bằng X2.

## 5. Tải đi qua và tải đề nghị

dt4n dùng `txRate`, tức `ρ_carried≤1`; definitions cần
`ρ_offered=(Δtx_packets+Δdrop_packets)L/(CΔt)`, có thể vượt 1. Gần bão hòa, carried load che mất đúng phần overload
quan trọng. DES tiếp tục dùng offered load; validation Mininet phải dựng lại offered load và kiểm ý nghĩa counter drop.

## 6. Các nhóm Π và cảnh báo PSA

Điểm neo được mô tả bởi `Π_age=z_eff/τ`, `Π_hold=H/τ`, `Π_knee=σ/(1−ρ̄)`, `Π_noise`, `Π_relax`, `ε/S`, `K`
và đề xuất `Π_flow=r_fW/L`. `Π_noise` so nhiễu với độ trôi do tuổi, còn `R/V(W)` mới so với tín hiệu; hai tỉ số
không được diễn giải thay nhau. Bảng đầy đủ và ba đại lượng chính xác nằm trong output f01.

`Π_relax>1` đánh dấu nơi hàng đợi có thể không theo kịp tải, nên surrogate PSA cần được kiểm thay vì mặc nhiên tin.
`T_relax=S/(1−√ρ̄)²` chỉ là chỉ báo bậc độ lớn M/M/1 vô hạn, không phải kết luận cho K hữu hạn.

## 7. Đề xuất cho các quyết định

- **K7:** mô tả tốc độ link cùng thành phần flow; không nói riêng `C` quyết định nguồn bất định.
- **K8:** anchor không đồng bộ dùng tuổi thực nghiệm/răng cưa+đuôi; quét `a`; chế độ đồng bộ là sensitivity.
- **K9:** sinh `σ` từ `(C,r_f)` hoặc báo `Π_flow`, thay vì quét `σ` độc lập mà không giải thích vật lý.
- **K20/X2:** dt4n không cung cấp trace tải thật. Đề xuất M/G/∞ Pareto làm tầng 2 rẻ; mini-spike MAWI tối đa một
  ngày là tùy chọn để kiểm hình dạng ACF, với cảnh báo độ tổng hợp và capture loss. Chờ GVHD quyết định ở L1.10.

## 8. SESOI

Để trống cho L1.5: lập luận ngưỡng ý nghĩa thực tiễn theo ms và tỉ lệ headroom.
