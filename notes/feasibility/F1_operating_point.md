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

### 8.1. Ứng dụng và nguồn chuẩn

Ứng dụng mục tiêu là VoIP, nhất quán với elevator test. [ITU-T Y.1541 (12/2011)](https://www.itu.int/rec/T-REC-Y.1541-201112-I/en)
lớp 0 đặt upper bound 100 ms cho mean IPTD, 50 ms cho IPDV và `10⁻³` cho IPLR; VoIP/VTC là ví dụ ứng dụng.
IPTD chỉ là phần mạng, trong khi người dùng chịu trễ miệng-tới-tai gồm cả codec, packetization và jitter buffer.

[ITU-T G.107 (06/2015)](https://www.itu.int/rec/T-REC-G.107-201506-I/en) §7.4 định nghĩa E-model và suy giảm
do trễ thuần `Idd`. Bản gốc đã được mở và đối chiếu trực tiếp với `t04_emodel_floor.py`: mặc định `sT=1`,
`mT=100 ms`, và lớp mặc định phải dùng cho carrier-grade/enterprise telephony hoặc khi chưa biết nhóm người dùng.

### 8.2. Sàn tuyệt đối m

Với mặc định G.107, `Idd=0` khi `Ta≤100 ms`; sau đó đường cong gần như phẳng tới khoảng 150 ms. T04 tìm được độ
dốc cực đại `0,1231 điểm R/ms` tại `Ta≈241,5 ms`. Chọn thiết kế `ΔR_min=1` điểm—một thay đổi nhỏ, theo hướng dễ
phát hiện hiệu ứng—cho

```text
m = 1 / max(dIdd/dTa) = 8,1 ms.
```

ITU chuẩn hóa công thức E-model nhưng **không** quy định rằng một điểm R là SESOI; `ΔR_min=1` là lựa chọn nghiên cứu
được khóa trước F2. Vì dùng độ dốc lớn nhất, gap dưới 8,1 ms làm đổi dưới một điểm R ở mọi mức `Ta` trong miền quét.
Gap vượt m chỉ *có thể* cảm nhận được tùy tổng trễ, không đảm bảo người dùng nhận ra.

Các con đường không chọn là 5% ngân sách Y.1541 (`5 ms`, hệ số 5% tùy ý) và một service time (`3,024 ms` tại
4 Mb/s, không phải lý do ứng dụng). Quy đổi `m` là `2,68S`, `5,36S`, `66,97S` tại 4/8/100 Mb/s. Do đó m là ngưỡng
cao so với hàng đợi link nhanh; kết luận “ngưỡng tĩnh đủ cho VoIP trong miền kiểm” là kết quả hợp lệ, không phải thất bại.

### 8.3. Sàn tương đối r và quy tắc CI

Khóa `r=10%` như phán đoán thiết kế: thích nghi phải lấy lại ít nhất một phần mười headroom mới đáng chi phí tính
phân phối mỗi epoch. `r=5%` và `20%` chỉ báo phụ. Theo từng seed paired:

```text
D_abs = gap − 8,1 ms
D_rel = gap − 0,10·headroom
```

- Có ý nghĩa khi cận dưới CI95 của cả hai đại lượng lớn hơn 0.
- Không đáng kể khi cận trên CI95 của ít nhất một đại lượng nhỏ hơn 0.
- Các trường hợp khác chưa kết luận; thêm seed theo F3, không đổi ngưỡng.

Ô chính DP0 đã khóa trong experiment log: P1 là anchor lưới gần nhất (`K=11, ρ̄=0,85, σ=0,03, τ=10 s`);
P2 là contrast buffer sâu/gần bão hòa (`K=100, ρ̄=0,95, σ=0,10, τ=2 s`), cả hai tại 4 Mb/s và tuổi CLEAN
cố định trung bình. Các ô khác chỉ mô tả. Báo phụ dùng `m/2`, `2m`, `r∈{5%;20%}` và không quyết định DP0.
