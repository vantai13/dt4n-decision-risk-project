# n00 — Kết quả tái lập L1.1 (2026-10-02)

Base commit: `e669f5c8053a81d6de192de9f9d0d6304ee67802`; Python 3.14.5, NumPy 2.5.3, SciPy 1.18.1.

Ô **POS_probeB**, seed **9101** (pilot), **4000 epoch**; ε=0.604800 ms; thời gian tính/xuất ≈ 0.653 s.

Lệnh: `.venv/bin/python -m experiments.n00_trace_one_check | tee experiments/results/n00_trace_one_check_output.txt`.

Luôn ở A; đề xuất nếu Iplug > 0; duyệt nếu có đề xuất và Ibar > 0. Nhãn theo sự thật PSA.
Đây là minh hoạ một seed đã thấy kết quả trong lesson, không phải thí nghiệm mù, DES hay rollout; không áp ngân sách harm.

| Epoch (đánh số từ 0) | Iplug (ms) | Ibar (ms) | I thật (ms) | Phán quyết / hành động | Đánh giá theo kết quả thực hiện |
|---|---:|---:|---:|---|---|
| 99 | +0.509651 | -13.581437 | +1.368737 | Từ chối / giữ A | Từ chối nhầm |
| 23 | +5.194352 | +6.529966 | +70.604449 | Duyệt / chuyển B | Duyệt đúng |

Sai số dự báo lớn không đồng nghĩa phán quyết sai: epoch 23 vẫn duyệt đúng.

| Mẫu số | Số lượng | Duyệt mà hại / mẫu số |
|---|---:|---:|
| Mọi epoch | 4000 | 292/4000 = 7.3000% |
| Mọi đề xuất | 2552 | 292/2552 = 11.4420% |
| Mọi lần duyệt | 2012 | 292/2012 = 14.5129% |
| Mọi đề xuất có hại | 510 | 292/510 = 57.2549% |

Hàng cuối là tỷ lệ **bỏ lọt** đề xuất có hại, không phải tỷ lệ bắt được hại.

Phép tính đường cong dừng (không phải can thiệp DES):

- Δρ=0,0064 tại ρ=0.85: delay tăng 0.180013 ms (ε=0.604800 ms).
- Δρ=0,0064 tại ρ=0.95: delay tăng 1.739993 ms (ε=0.604800 ms).
- Ví dụ nhóm Δρ=0,1: lợi ích thật tĩnh T(0,95)−T(0,95)=0; bỏ qua tải nhóm tạo lợi ích ảo 8.041041 ms.

Kiểm đối chiếu số lesson (không phải bằng chứng độc lập về mô hình):

- ĐẠT — tử số và bốn mẫu số khớp lesson.
- ĐẠT — epoch 99 khớp số làm tròn của lesson.
- ĐẠT — epoch 23 khớp số làm tròn của lesson.
- ĐẠT — kỳ vọng từng đường khớp twin_inputs.
- ĐẠT — đầu ra hữu hạn.

Các tệp kết quả:

- [Output console](n00_trace_one_check_output.txt).
- [CSV 4.000 epoch](n00_trace_one_check_epochs.csv): dự báo, phán quyết, hành động minh hoạ, kết quả, telemetry và hậu nghiệm từng đường.
- [Question card N0](../../notes/novelty/N0_question_card.md).

Nguồn script lõi: lesson do người dùng cung cấp (ghi Claude). Codex bổ sung xuất dữ liệu, kiểm đối chiếu và báo cáo; chưa xác nhận tác giả tự kiểm bài.
Không thay hàm nền tảng; posterior Gauss và đường cong nội suy vẫn có xấp xỉ. Hai nhánh can thiệp Δρ>0 chưa triển khai.
