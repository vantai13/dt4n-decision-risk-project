# T3 — Mục tiêu K2 và khoảng cách thích nghi

> Ngày 2026-09-26. Tác giả xác nhận đã tự làm phần chứng minh/tính nháp ngoài repository; code được hiện thực hóa
> theo pseudocode của lesson và được kiểm bằng các mốc đối chiếu. Luật K2 là thước đo sách giáo khoa, không phải
> contribution mới của đề tài.

## 1. Ký hiệu

`I_D=D_cur−D_alt` là lợi ích thật khi đổi; `F` là thông tin lúc quyết định; `a∈{0,1}`; `Î` là plug-in;
`Ī=E[I_D|F]`; `p−=P(I_D<−ε|F)`; `α` là ngân sách harm trên mọi epoch; `c` là chi phí đổi. Đánh giá dùng
`gain=E[a(I_D−c)]` và `harm=E[a·1{I_D<−ε}]`, đều chia cho mọi epoch.

## 2. Tính chất tháp

Vì `a` chỉ phụ thuộc `F`, nó là hằng số khi điều kiện hóa:

```text
gain = E[a(Ī−c)],             harm = E[a p−].
```

Do đó oracle không biết trước `I_D`; nó biết đúng phân phối có điều kiện trên cùng `F`, và chỉ cần hai số `Ī,p−`
cho mỗi epoch.

## 3. Lagrange và KKT

Với `λ≥0`, chọn `a*=1` khi `Ī−c−λp−>0`. Với mọi luật khả thi `a`:

```text
G(a) ≤ G(a)−λ[H(a)−α]
     = E[a(Ī−c−λp−)]+λα
     ≤ E[a*(Ī−c−λp−)]+λα
     = G(a*)−λ[H(a*)−α]
     = G(a*),
```

trong đó bất đẳng thức đầu do `H(a)≤α`, bất đẳng thức thứ hai do `a*` lấy đúng các số hạng dương, và dòng cuối
dùng complementary slackness. Nếu luật `Ī>c` đã đủ an toàn thì `λ=0`; ngược lại lấy `λ` nhỏ nhất làm harm không
vượt `α`. Với mẫu hữu hạn, harm nhảy bậc nên có thể thiếu một phần epoch biên.

## 4. Cái túi phân số và ý nghĩa λ

Khi `p−>0`, điều kiện đổi tương đương `(Ī−c)/p−>λ`: giá trị là ms kỳ vọng, trọng lượng là ngân sách harm. Vì vậy
`λ` có đơn vị ms cho mỗi harm chắc chắn. Với cùng `Î=Ī=1 ms`, `ε=0,5`, `λ=9,91`: nếu `s=0,5` thì điểm K2
khoảng `+0,987` và đổi; nếu `s=3` thì khoảng `−2,058` và giữ. P/Q có `p−≈0` nên 30 ms được ưu tiên khoảng
`30/0,7≈43` lần, khác mục tiêu đếm missed.

## 5. H1: khi ngưỡng tĩnh tối ưu

Nếu tại `λ` vận hành có hàm tăng ngặt `h` sao cho `Ī−λp−=h(Î)` gần biên, K2 chính là ngưỡng
`Î>h⁻¹(c)`. Nó vừa thuộc họ ngưỡng vừa tối ưu trong mọi luật, nên ngưỡng tốt nhất và K2 có cùng gain. Điều kiện
này bao gồm họ tịnh tiến, bất định thay đổi nhưng giữ thứ tự (thế giới B), ngân sách thừa với `Î=Ī`, và bất định
chỉ khác xa biên. Bất định không đồng đều tự nó chưa đủ tạo khoảng cách.

## 6. Phân rã headroom

```text
gain_static(α) ≤ gain_K2(α) ≤ E[(Ī−c)+] ≤ E[(I_D−c)+].
```

Ba khoảng lần lượt là giá trị thích nghi, giá của an toàn và giá trị của thông tin hoàn hảo. Với
`X~N(m,s²)`, `E[X+]=sφ(m/s)+mΦ(m/s)`, suy ra headroom bằng trung bình công thức này với `m=Ī−c`.

## 7. Ba thế giới đồ chơi và đính chính

Chung: `N=400.000`, `ε=0,5 ms`, `α=1%`, `c=0`, `I_D|F~N(Î,s²)` và `Ī=Î`.

- A, seed 9101: `Î~N(0,5;2²)`, rồi `log s~N(0;0,7²)`. Bất định độc lập làm đảo thứ tự; gap khoảng 0,095 ms.
- B, seed 9102: cùng `Î`, `s=0,3+0,5|Î|`. Trong vùng dương, `(0,5+Î)/(0,3+0,5Î)` tăng nên `p−` giảm;
  K2 và ngưỡng tĩnh chọn cùng tập. Gap chính xác bằng 0; `0,0008` trước đây là artefact lưới 801 điểm.
- C, seed 9103: `Î~N(0;0,3²)`, `s=0,05`. Luật `Î>0` đã có harm bằng 0 nên `λ=0`; cố tiêu hết ngân sách sẽ
  thêm epoch có kỳ vọng âm và làm giảm gain.

Con số “missed giảm 8,3 điểm %” thuộc mục tiêu cũ; với K2 là khoảng 7,9 điểm % tương ứng khoảng 0,095 ms.

## 8. Hệ thật khác đồ chơi

Trong hệ thật, `Î` dùng thẳng `ρ_hat`, còn tâm đúng bị shrink về `μ` với hệ số `β`; tại 4 Mb/s plug-in có thể
phản ứng quá mức với nhiễu. Đồng thời đường cong hàng đợi lồi làm `E[W(ρ)]>W(Eρ)` (Jensen), khiến plug-in đánh
giá thấp delay gần bão hòa. Hai sai lệch phụ thuộc trạng thái và có thể đảo thứ tự ngay cả khi `λ=0`. Phân phối
`I_D` sau biến đổi phi tuyến cũng không còn Gauss, nên hệ thật phải ước lượng `Ī,p−` bằng conditional Monte Carlo.
