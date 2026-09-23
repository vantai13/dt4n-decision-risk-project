# El Halabi & Brandt 2026 — ACI dưới delayed feedback

| Trường | Giá trị |
|---|---|
| Tiêu đề | Adaptive Conformal Inference Under Delayed Feedback: Coverage Guarantees and a Delay-to-Memory Diagnostic |
| Tác giả | Lama El Halabi; Adam Brandt |
| Nguồn | [arXiv:2609.07251v1](https://arxiv.org/abs/2609.07251), 07/09/2026 |
| Trạng thái | Preprint; chưa xác nhận peer review |
| Mức kiểm | 2026-09-23: PDF các đoạn §1–4, §7–8, bảng 6–7; proof appendix chưa kiểm đầy đủ |
| Lượt đối chiếu nguồn | 2; lượt sau kiểm lại Eq. (11), Table 6 và định nghĩa `τ/L` trong PDF ngày 2026-09-23 |
| Mức đe dọa | Cao cho framing “delay/memory là ý tưởng mới”; trung bình cho per-decision routing method |

**[F]** Bài phân tích ACI khi nhãn của dự báo horizon `τ` chỉ xuất hiện sau `τ` bước. Recursion tách thành `τ` chuỗi xen kẽ; có cận tần suất coverage dài hạn phụ thuộc `τ`, và diagnostic `r=τ/L` với `L` là memory của residual (§2–4). Đây là **feedback delay của dự báo**, chưa phải `z` = thời gian kể từ telemetry mới nhất tại lúc ra quyết định.

**[F]** Trên AR(1), chuẩn hóa delay theo memory giảm scatter của interval score trong bin **79%**; GARCH 46%, Markov switching mean 9%, variance 27%, joint 10% (bảng 6, §7.6). Các con số là diagnostic của **interval score**, không phải route flip/regret hay proof rằng một luật chuẩn hóa luôn đúng. Bảng 7 cho thấy kết quả thay đổi theo đại lượng đo.

**[F]** §8 nêu tỉ số không phải mô tả phổ quát: memory có thể nằm ở level, variance hoặc latent regime; step size `γ` cố định có trade-off. [I] Đề tài cần so `z/τ_OU` với age thô và kiểm nơi mô hình chuẩn hóa vỡ dưới heavy-tail/regime, nhưng không thể nhận toàn bộ ý tưởng “delay chia thang nhớ” làm novelty.

**[I] So với đề tài:** paper kiểm coverage/độ rộng của **prediction intervals** dưới delayed labels; đề tài kiểm lỗi **ranking và regret của route** khi state dùng để ra quyết định bị cũ. Hai delay có thể cùng hiện diện, nên thí nghiệm phải ghi riêng telemetry age `z` và label lag `d_label`. Baseline ACI có delay đúng giao thức nếu nhãn đến muộn.

**[?] Cần đọc sâu:** chứng minh §4 và Appendix A; kiểm liệu bound của họ cần residual assumptions nào ngoài bounded control variable; đọc Wang & Hyndman 2026 về cross-horizon error.
