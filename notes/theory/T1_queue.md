# T1 — Hàng đợi M/D/1/K

> Ngày 2026-09-26. Tác giả xác nhận đã tự làm phần tính nháp ngoài repository; tài liệu hệ thống hóa kết quả và
> provenance của code. Đơn vị thời gian là một thời gian phục vụ `S=1`; `K` tính cả gói đang phục vụ.

## 1. Ký hiệu và đơn vị

Arrival là Poisson, phục vụ cố định, một server và tối đa `K` gói trong hệ thống. Offered load là `ρ=λS`.
Các đầu ra là blocking probability `P_K`, chờ của gói được nhận `W_q`, sojourn `T=W_q+S` và phân phối số gói
theo thời gian `p_n`. Với buffer hữu hạn, `ρ≥1` vẫn có trạng thái dừng nhờ drop.

## 2. Little, PASTA và cân bằng bận

Tốc độ được nhận là `λ_eff=λ(1−P_K)`, nên Little cho `L_q=λ_eff W_q`. PASTA cho phép arrival Poisson nhìn thấy
phân phối theo thời gian, vì vậy loss bằng tỉ lệ thời gian hệ thống đầy. Xác suất server bận đồng thời bằng
`1−p_0` và lượng công việc nhận mỗi đơn vị thời gian `ρ(1−P_K)`, nên `1−p_0=ρ(1−P_K)`.

## 3. Chuỗi Markov nhúng

Số gói liên tục theo thời gian không Markov vì còn phụ thuộc residual service. Quan sát ngay sau mỗi departure,
đặt `X_k` là số gói bị để lại, ta có trạng thái `0,…,K−1`. Nếu `A~Poisson(ρ)` là số arrival trong một service,
thì từ `i≥1`, `X_{k+1}=min(i−1+A,K−1)`; từ `i=0`, arrival đầu mở service mới nên
`X_{k+1}=min(A,K−1)`. Chuỗi chỉ giảm nhiều nhất một mức.

## 4. Phương trình lát cắt

Đặt `a_0=exp(−ρ)` và `Abar_m=P(A>m)`. Cân bằng luồng qua lát cắt `{0,…,n}` cho

```text
π[n+1] a_0 = π[0] Abar[n] + Σ(i=1..n) π[i] Abar[n+1−i].
```

Luồng xuống chỉ có `n+1→n` với `A=0` do tính skip-free; luồng lên cộng mọi trạng thái phía dưới. Đặt `u_0=1`,
tính lần lượt bằng phép cộng số dương rồi chuẩn hóa `π=u/Σu`.

## 5. Từ departure sang phân phối theo thời gian

Level crossing cho phân phối mà arrival được nhận nhìn thấy bằng `π_n`. PASTA cho phân phối đó là
`p_n/(1−P_K)`. Kết hợp cân bằng bận:

```text
p_n = π_n/(π_0+ρ) = π_n(1−P_K),   n<K,
P_K = 1−1/(π_0+ρ).
```

Sau khi có `p`, tính `L_q=Σ(n−1)p_n` và `W_q=L_q/[ρ(1−P_K)]`.

## 6. Triệt tiêu số

Bốn phép trừ nguy hiểm là: tính loss nhỏ bằng `1−1/(π_0+ρ)`; tính đuôi bằng `1−CDF`; tính đuôi vô hạn bằng
`1−(1−ρ)Σu`; và tính `W_q=T−1`. Code dùng `poisson.sf`, tổng đuôi dương, công thức loss ổn định và Little trực
tiếp để tránh loss âm hoặc chờ âm.

## 7. Công thức đuôi ổn định

Với `ρ<1`, phương trình lát cắt không chứa `K` trước biên nên hệ hữu hạn tỉ lệ với hệ vô hạn trên `0,…,K−1`.
Nếu `Q=P_inf(N≥K)` thì

```text
P_K = (1−ρ)Q/(1−ρQ).
```

`Q` nhỏ được tính bằng tổng các trọng số dương. Khi `Q` không nhỏ, phép tính trực tiếp đủ chính xác. Với `ρ≥1`,
dùng dạng toàn số dương `P_K=[1+(ρ−1)U]/[1+ρU]`, `U=Σu`.

## 8. Giới hạn Pollaczek–Khinchine

Khi `K→∞` và `ρ<1`, M/D/1 có `W_q=ρ/[2(1−ρ)]` trong đơn vị `S`. Đây là kiểm tra độc lập cho `K=1000`.
Buffer hữu hạn có thể có chờ nhỏ hơn vì drop các gói lẽ ra chờ lâu; vì vậy delay gói sống sót phải luôn đọc cùng loss.

## 9. Workload

Workload `V(t)` giảm với tốc độ một khi server bận. Arrival bị drop khi `V>(K−1)S`; nếu được nhận, nó chờ đúng
`V` rồi thêm `S` vào workload. Recursion này là phương pháp độc lập dùng trong `t01_mdk_des_check.py`.

## 10. Hai bài tính tay

Với `K=2, ρ=0,5`, `π=(0,606531;0,393469)`, `p=(0,548137;0,355588;0,096274)`,
`P_2=0,096274` và `W_q=0,213061S`. Với `K=3, ρ=0,5`,
`π=(0,528005;0,342528;0,129467)`, `p=(0,513621;0,333197;0,125940;0,027242)`,
`P_3=0,027242` và `W_q=0,370954S`.
