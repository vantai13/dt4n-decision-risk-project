# Ước lượng tham số twin từ telemetry — BẢN NHÁP ĐỂ REVIEW

Ngày 2026-10-01. Không phải tiền đăng ký đã khoá, không phải outcome v6.
Chưa chạy calibration DES 90001–90020 hoặc test 91001–91020.

## 1. Ranh giới thông tin

`experiments/scan/telemetry_fit.py` nhận riêng từng path, chỉ đọc:
`rhohat`, `age`, `decision_times`, chu kỳ T và service time S từ capacity/cỡ gói.
Không đọc delay, nhãn harm, tải OU tiềm ẩn, ρ̄, σ, τ của generator, hoặc telemetry test.
Ước lượng một bộ (ρ̄,σ,τ) cho mỗi path từ tất cả seed calibration; đóng băng khi test.
Các luật K2/SClin/SCtab24 phải dùng cùng bộ ước lượng và cùng tâm twin.

## 2. Tự dẫn công thức

Gọi X(t)=ρ(t)−ρ̄ là OU dừng với kernel Cov(X(u),X(v))=σ²exp(−|u−v|/τ).
Một bản tin là Yᵢ=(S/T)Nᵢ, với Nᵢ|ρ ~ Poisson((1/S)∫ρ(t)dt).
Đặt Gᵢ=(1/T)∫ρ(t)dt trên cửa sổ thứ i.

E(Yᵢ|ρ)=Gᵢ; Var(Yᵢ|ρ)=GᵢS/T. Bởi vậy:

    E(Yᵢ)=ρ̄
    Var(Yᵢ)=V(T)+R,    R=ρ̄S/T
    V(T)=2σ²[x−1+exp(−x)]/x², x=T/τ.

Hai cửa sổ không chồng lấn có nhiễu Poisson độc lập khi điều kiện hoá theo tải.
Với hai timestamp cách nhau kT, k≥1:

    Cₖ = (σ²/T²) ∫₀ᵀ ∫ₖᵀ⁽ᵏ⁺¹⁾ᵀ exp(−(v−u)/τ) dv du
       = σ² [τ/T·(1−exp(−T/τ))]² exp(−(k−1)T/τ).

Không có R trong Cₖ. Nếu covariance không nhiễu, từ hai lag k₂>k₁:

    τ = −(k₂−k₁)T / log(Cₖ₂/Cₖ₁).

Thay τ trở lại Cₖ₁ để suy σ². Đây là giải thích tính nhận dạng, không là
ước lượng log-ratio thực tế: covariance mẫu có thể âm. Code khớp WLS trên
covariance gốc, giữ cả lag âm có đủ cặp, thay vì bỏ chúng hoặc log chúng.

## 3. Bản tin tươi và outage

Timestamp đo = timestamp quyết định − tuổi. Chỉ giữ lần cập nhật đầu tiên
của mỗi timestamp; không deduplicate theo giá trị (hai số đếm bằng nhau vẫn
có thể là hai bản tin). Mặc định tuổi <=2T; đây là lựa chọn cần review/khóa,
không phải tiêu chí suy từ tham số OU thật. Timestamp đo phải trên lưới T;
không đúng thì fail, không âm thầm giả định đều.

Giữ tick thời gian gốc. Sau outage 30 s, hai bản tin sát nhau trong mảng đã
lọc KHÔNG được coi là lag 1. Chỉ tạo cặp có chênh tick bằng k. Không ghép
cặp qua hai seed, không nội suy bản tin mất, không điền lại số đo cũ.

ρ̄ được tính từ tất cả bản tin tươi, dùng chung để center covariance mỗi path.
Giả định mất bản tin độc lập tải và OU dừng. Nếu outage phụ thuộc nghẽn,
trung bình bản tin giữ lại có thể lệch; estimator hiện tại chưa xử lý cơ chế đó.

## 4. Objective và lựa chọn mặc định cần review

    min_{σ,τ>0} Σₖ nₖ/n_max · [Ĉₖ − Cₖ(σ,τ)]².

Khớp trong log(σ),log(τ), ba điểm khởi đầu. Lags {1,2,4,8,16,32,64,128,256};
>=100 cặp/lag; ít nhất 3 lag hợp lệ. Bounds σ∈[1e−5,2], τ∈[0,1;3600] s,
không lấy từ σ/τ thật. Không bỏ covariance âm ở lag dài.
Trọng số số cặp là heuristic; các lag phụ thuộc nhau, nên không cung cấp CI
tham số từ Hessian. Có cảnh báo chạm bounds, nhận dạng yếu và lệch kiểm
Var(Y)≈V(T)+R >20%; chưa phải các cổng validity đã đăng ký.
Không dùng Var(Y) để fit; nó là phép kiểm tách khỏi covariance không chứa R.

## 5. Kiểm đã chạy — CHỈ TỔNG HỢP

Sinh chính xác OU-box Gaussian joint, rồi Poisson; 100.000 cửa sổ/ca, mất
ngẫu nhiên 20% bản tin. Entropy RNG [20261001,42,case_index], không dùng seed DES v6.

| T | ρ̄ thật → fit | σ thật → fit | τ thật → fit (s) |
|---|---:|---:|---:|
| 1 s | 0,8 → 0,8056 | 0,14 → 0,1383 | 60 → 57,90 |
| 1 s | 0,7 → 0,6985 | 0,10 → 0,0978 | 15 → 14,54 |
| 10 s | 0,9 → 0,8998 | 0,08 → 0,0793 | 120 → 118,93 |

Không cảnh báo ở ba ca. Sai số σ 0,8–2,2%, τ 0,9–3,5%.
Đây không phải CI hay bảo đảm với 20 seed DES/outage liên tục.
Kiểm đơn vị: covariance khớp tích phân kernel OU; moments chính xác khôi
phục tham số; clock gaps, duplicate, ranh giới seed và từ chối input sai.
Thêm test thay đổi D/ρ̄/σ/τ thật trong input phụ không làm thay đổi fit.

## 6. Dự đoán TRƯỚC TEST MỚI — đề xuất của trợ lý, chưa duyệt

Dựa trên v5 đã biết và kiểm tổng hợp, không giả làm dự đoán của tác giả:

- Tôi dự đoán K2 với twin ước lượng vẫn hơn SClin: chênh trung bình
  SClin−K2 dương khoảng 0,2–0,5 ms, CI ghép cặp loại 0.
- Tôi dự đoán K2 vs SCtab24 vẫn chưa phân giải ở 20 seed (CI chứa 0).
- Tôi dự đoán p₋ vẫn chưa là xác suất hiệu chỉnh chỉ nhờ ước lượng tham số;
  phải giữ tune bằng harm_W thật, không dùng ngân sách harm dự đoán.

Các dự đoán này chưa phải kết quả và chưa tiền đăng ký; người dùng cần
review bộ ước lượng/protocol trước khi khóa commit rồi mở seed mới.

## 7. Protocol phép so mới — dự thảo, CHƯA THỰC HIỆN

1. Review các lựa chọn trên và policy xử lý fit chạm bound/nhận dạng yếu.
   Không chọn/tune estimator bằng delay test.
2. Khóa estimator, dự đoán, objective và cổng validity bằng commit trước khi chạy.
3. Một ô R3_outage; cal 90001–90020, test 91001–91020; 6.000 epoch quyết định,
   H_dec=1 s, hold-down=H_tw=30 s, ε=1 ms, α=0,002.
   Sinh thêm 29 epoch nhãn tương lai, không rút ngắn cửa sổ như v5.
4. Fit riêng mỗi path trên bản tin cal tươi; đóng băng ρ̄,σ,τ; tính chung Ī,p₋
   bằng twin đó cho K2/SClin/SCtab24. Tune chính sách bằng delay/harm_W cal thật.
5. Chính: SClin−K2, CI t ghép cặp qua 20 seed; phụ: SCtab24−K2,
   harm_W, harm_1s, tần suất đổi, kiểm hiệu chỉnh p₋. Không tuyên bố tương đương
   khi CI chứa 0. Không sửa ngưỡng/cổng sau khi thấy test.
6. Chỉ sau review + phép so này mới xem xét calibration {2,5,20}/dịch chế độ.

Hiện mới viết và kiểm bộ ước lượng; chưa viết/chạy pipeline v6 chính thức.
