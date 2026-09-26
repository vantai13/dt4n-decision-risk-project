# T2 — OU, cửa sổ đo, nhiễu đếm và tuổi dữ liệu

> Ngày 2026-09-26. Tác giả xác nhận đã tự làm phần tính nháp ngoài repository; tài liệu này hệ thống hóa lại kết quả
> để kiểm bằng mô phỏng. Các tham số số học dưới đây là giả định pilot, chưa phải số đo mạng thật.

## 1. OU và ba tham số

Tải được mô hình hóa bởi

```text
dρ(t) = −(ρ(t) − μ)/τ · dt + σ√(2/τ) · dB(t).
```

`μ` là trung bình dài hạn, `σ` là độ lệch chuẩn dừng và `τ` là thời gian tương quan. Ở trạng thái dừng,
`ρ(t) ~ N(μ,σ²)` và `Cov(ρ(t),ρ(t+u)) = σ²exp(−|u|/τ)`. OU là giả định yếu vì chỉ có một thang thời gian,
không bị chặn và không mô tả được tự tương tự hoặc đuôi dài của traffic thật.

## 2. Rời rạc chính xác và Euler

Đặt `r = exp(−Δ/τ)` và viết

```text
x[k+1] − μ = r(x[k] − μ) + sξ[k],       ξ[k] ~ N(0,1).
```

Điều kiện giữ phương sai dừng cho `r²σ²+s²=σ²`, nên `s=σ√(1−r²)`. Do đó

```text
x[k+1] = μ + exp(−Δ/τ)(x[k]−μ) + σ√(1−exp(−2Δ/τ)) ξ[k].
```

Euler dùng hệ số nhớ `1−Δ/τ`. Với `Δ=τ/2`, một bước từ phân phối dừng cho
`Var(x[k+1])=1,25σ²` và `Corr(x[k],x[k+1])=0,5/√1,25≈0,447`, thay vì `σ²` và `exp(−0,5)≈0,607`.

## 3. Điều kiện theo một điểm: plug-in và dự báo tối ưu

Nếu biết chính xác `ρ(t−z)=x` thì

```text
ρ(t) | x ~ N(μ+r(x−μ), σ²(1−r²)),       r=exp(−z/τ).
```

Sai số plug-in có phương sai `2σ²(1−r)`, còn dự báo tối ưu có phương sai `σ²(1−r²)`. Vì
`2(1−r)−(1−r²)=(1−r)²≥0`, dự báo tối ưu không tệ hơn plug-in: khi dữ liệu cũ, nó kéo dự báo về `μ` thay vì
coi số cũ là trạng thái hiện tại.

## 4. Trung bình trên cửa sổ

Với `m=L⁻¹∫ρ(s)ds` trên một khoảng dài `L`, đối xứng của tích phân kép theo khoảng cách `u=|s−s'|` cho

```text
Var(m) = V(L)
V(L) = 2σ² [L/τ − 1 + exp(−L/τ)] / (L/τ)².
```

Thật vậy, tích phân kép của kernel tương quan bằng
`2∫₀ᴸ(L−u)exp(−u/τ)du = 2τ²[L/τ−1+exp(−L/τ)]`. Vì vậy trung bình khoảng không thể được thay hoàn toàn
bằng một điểm tại tâm khi tính phương sai.

## 5. Nhiễu đếm

Nếu `N | quỹ đạo ~ Poisson(Wm/S)` và `ρ_hat=NS/W` thì

```text
E[ρ_hat | quỹ đạo] = m,
Var(ρ_hat | quỹ đạo) = mS/W ≈ μS/W = R.
```

Với gói 1512 byte, `W=0,5 s`, `μ=0,9`: ở 4 Mb/s có khoảng 149 gói và `sd(ρ_hat)≈0,0738`; ở
100 Mb/s có khoảng 3720 gói và `sd(ρ_hat)≈0,0148`. Ba điểm cần giữ: nhiễu phụ thuộc tải; Poisson chỉ phù hợp
với arrival Poisson; với arrival overdispersed, phương sai có thể tăng theo index of dispersion.

## 6. Phân phối của trung bình khoảng giữ

Gọi `y` là số đo trung bình cửa sổ có nhiễu, `G` là trung bình tải trên khoảng giữ, và `g` là khoảng từ cuối
cửa sổ đến đầu khoảng giữ. Đặt

```text
A(L) = [1−exp(−L/τ)]/(L/τ),
c = Cov(G,y) = σ² A(W) exp(−g/τ) A(H),
Var(y) = V(W)+R,       Var(G)=V(H).
```

Tách tích phân hiệp phương sai được vì khoảng giữ nằm sau cửa sổ:
`exp(−(v−u)/τ)=exp(u/τ)exp(−v/τ)`; hai tích phân một chiều lần lượt sinh `A(W)` và
`exp(−g/τ)A(H)`. Do đó dự báo tuyến tính tốt nhất là

```text
E[G|y] = μ + β(y−μ),                 β = c/[V(W)+R],
Var(G|y) = V(H) − c²/[V(W)+R].
```

Cùng kết quả có thể đọc như hai bước Kalman: cập nhật trạng thái ở cuối cửa sổ bằng `y`, rồi dự báo OU chính xác
qua `g` và khoảng giữ `H`.

## 7. Giới hạn của z_eff

Khi `W,H << τ`, `A(L)≈exp(−L/(2τ))`, nên `c≈σ²exp(−z_eff/τ)`. Chỉ khi nhiễu không đáng kể mới có
`β≈exp(−z_eff/τ)`. Khi có nhiễu, còn phải nhân độ lợi tín hiệu `V(W)/[V(W)+R]`. Công thức phương sai chỉ dùng
`z_eff` cũng bỏ mất việc lấy trung bình trên `W`, `H` và nhiễu `R`.

Với `τ=10 s`, 4 Mb/s: `V(W)=V(H)=8,852×10⁻⁴`, `c=8,145×10⁻⁴`, `R=5,443×10⁻³`, nên
`β≈0,129` và `Var(G|y)≈7,803×10⁻⁴` (`sd≈0,0279`). Trong khi đó `exp(−z_eff/τ)≈0,905`; plug-in theo tuổi
vì vậy tin số đo quá mức.

## 8. Hàm ý của jitter tuổi

Ở giả định pilot 4 Mb/s, nhiễu đếm lớn hơn biến thiên tín hiệu nên thay đổi tuổi trong một chu kỳ poll chỉ làm
độ lệch chuẩn hậu nghiệm thay đổi rất ít. Ở 100 Mb/s, nhiễu nhỏ hơn nên tuổi có thể tạo ra khác biệt rõ hơn giữa
các quyết định. Đây là giả thuyết cần được neo bằng dữ liệu F1, không phải kết luận thực nghiệm.

## 9. Chỉ số nhiễu

`Π_noise` chỉ cho bậc độ lớn vì mẫu số dùng xấp xỉ điểm theo `z_eff`. Khi báo cáo F1, giữ chỉ số này nhưng bổ sung:

```text
nhiễu/tín hiệu = R/V(W),
phương sai được giải thích = 1 − Var(G|y)/V(H),
không đồng đều do tuổi = sd hậu nghiệm tuổi lớn nhất / sd hậu nghiệm tuổi nhỏ nhất.
```

Các đại lượng này nói trực tiếp số đo chứa bao nhiêu thông tin và bất định có thay đổi giữa quyết định hay không.
