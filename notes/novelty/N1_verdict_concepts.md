# N1 — Phán quyết, sự thật, chi phí (v0, 2026-10-02, nháp)

> Nguồn nháp: lesson do người dùng cung cấp (ghi Claude). Codex triển khai và đối chiếu local ngày 2026-10-02.
> Chưa xác nhận tác giả đọc từng dòng hoặc hoàn thành tự kiểm. Số liệu local: [báo cáo n01](../../experiments/results/n01_report.md).
> [QUYẾT] = tác giả quyết; chốt ở Gate N. n01b: MỘT ô (POS_probeB), 10 seed pilot, luật Ī > 0, thế giới PSA. n01 là xác suất giải tích; n01c là 300 cặp DES ở tải hằng.

## 1. Một lần kiểm và sáu ô

- Đề xuất A → B; phán quyết V ∈ {duyệt, từ chối}; kết quả I = D_giữ − D_áp dụng (ms; > 0: chuyển có lợi).
- Lớp thật: lợi (I > ε) · thờ ơ (|I| ≤ ε) · hại (I < −ε). Duyệt nhầm (DN) = duyệt ∧ hại; từ chối nhầm (TCN) = từ chối ∧ lợi.
- Quy ước cực: lớp dương = "nên duyệt". Khi so với paper, ghi lớp dương của họ.

## 2. Chi phí và regret

- Biết trước tương lai: duyệt ⇔ I > 0. regret = trung bình chi phí cơ hội trên MỌI lần kiểm = headroom_ms − gain_ms (c=0) (definitions v2.1).
- Regret ở đây không phụ thuộc ε: E[max(I,0) − a·I]. Nó vẫn tính mất mát trong vùng thờ ơ; ε chỉ dùng cho tỉ lệ đếm.
- Luồng nhỏ: DN và TCN cùng thang |I| → đối xứng. Bất đối xứng cần cơ chế: c; ngân sách α; ngoại ứng khi Δρ > 0.
  N0 đã chọn nháp lợi ích cho nhóm chuyển; với c=0 và luật Ī>0, mất mát vẫn đối xứng. Ngoại ứng lên lưu lượng nền chỉ thuộc phần mở rộng; không tự tạo bất đối xứng cho metric chính. [QUYẾT] nếu thêm c/α hoặc mục tiêu có ngoại ứng ở Gate N.

## 3. Hai loại sự thật, ba sandbox

| Sandbox | Biết gì | Vai trò |
|---|---|---|
| Thực tế | telemetry cũ, nhiễu; mô hình của twin | đối tượng được chấm |
| Lý tưởng | trạng thái Markov đúng lúc kiểm t + đúng mô hình | phần sai còn lại = không tránh được |
| Biết trước | kết quả I | trần tuyệt đối, regret = 0 |

- Trạng thái Markov: PSA/OU → ρ(t). DES → ρ(t) + workload hàng đợi tại t. [?] chưa dựng cho DES.
- Cả ba dùng CÙNG luật (chính: duyệt ⇔ E[I | thông tin] > 0).
- Phân rã CỘNG được bằng regret: regret_thực = regret_lý tưởng + (regret_thực − regret_lý tưởng).
  KHÔNG phân rã bằng số lần sai: "luôn từ chối" có 0% DN, ít hơn bản lý tưởng xấp xỉ local (1,81% trên mọi lần kiểm).
- Ranh giới aleatoric/epistemic là lựa chọn: lý tưởng biết trạng thái lúc t → trôi trong a tính là không tránh được.
  [QUYẾT] mốc t hay t + a (liên quan N-5). Gợi ý Codex: t để lượng thông tin khả dụng khớp lúc kiểm; chưa nhận lựa chọn tác giả cho N1.

## 4. Ví dụ tính tay (kiểm bằng n01)

- μ = 0,5; sd = 3; ε = 0,5 ms: P(I < −ε) = 0,369 (DN thật sự); P(I < 0) = 0,434. Toàn vùng thờ ơ chiếm 13,06%; phần âm của vùng thờ ơ nằm trong I<0 chỉ chiếm 6,44 điểm %.
- Base rate: bắt 90%/giữ 90%; 10% đề xuất hại → P(hại|duyệt) = 1,2%; 50% → 10%.

## 5. Kết quả n01b

| H | H/τ | Regret lý tưởng xấp xỉ (ms) | Regret thực tế (ms) | Chênh thực tế − lý tưởng (ms) | Lý tưởng DN\|hại |
|---|---:|---:|---:|---:|---:|
| 0.5 s | 0.05 | 0.319318 | 4.598814 | 4.279496 (93.06%) | 5.71% |
| 5.0 s | 0.5 | 2.386218 | 5.746669 | 3.360452 (58.48%) | 26.79% |
| 30.0 s | 3.0 | 4.708451 | 5.161522 | 0.453071 (8.78%) | 81.37% |

Các số trên là **local**, thay bảng số được trích trong lesson. Bản lý tưởng ở H=0,5 s cho 0,319318 ms / DN|hại 5,714%, không phải 0,324 ms / 5,3%.
Nguyên bản script trong attachment cũng cho đúng từng bit các mảng local; chưa xác định nguyên nhân khác với bảng lesson.

- Trong ba mức H đã chạy, regret lý tưởng tăng. Không suy thành quan hệ đơn điệu với mọi H.
- H đổi cả cửa sổ chấm, nhịp epoch và độ dài trace. Không phải ba cửa sổ lồng nhau trên cùng trace.
- Các tỉ lệ là pooled trên lần kiểm được chọn, không phải CI hoặc kết luận ngoài ô này.

## 6. Bộ sinh đề xuất (n01b, H = 0,5 s)

| Bộ sinh | Hại/đề xuất | DN\|hại | TCN\|lợi | P(hại\|duyệt) |
|---|---:|---:|---:|---:|
| G_all | 31,8% | 27,7% | 24,0% | 15,8% |
| G_greedy | 20,3% | 57,7% | 11,9% | 14,7% |

- Tỉ lệ theo lớp KHÔNG bất biến (vi phạm label shift). Cơ chế ứng viên: người đề xuất và twin dùng chung telemetry cũ
  → lỗi tương quan. Ứng viên insight, bằng chứng yếu (một ô).

## 7. Phản thực tế và CRN (n01c)

- Kết quả local khớp lesson: CRN không có hiệu ứng âm trong 300 lần kiểm (nhỏ nhất 0,54 ms); độc lập: 9,3% hiệu ứng âm. Đây là kết quả mẫu, không chứng minh dấu luôn không âm cho hàng đợi hữu hạn có drop và metric chỉ trên probe được nhận.
- Phân tán dưới CRN (sd 7,722551 ms local) thuộc coupling cụ thể của mô phỏng, gồm ngẫu nhiên hàng đợi/gói chuyển và phép lấy mẫu probe.
- n01c thêm gói chuyển từ đầu mô phỏng, kể cả warm-up: workload lúc bắt đầu chấm có thể khác giữa hai nhánh. Đây là so hai chế độ tải, chưa là rẽ hai nhánh tại t từ cùng workload.
- Đo probe ảo được nhận trên B, chưa đo trực tiếp delay nhóm chuyển đã chọn làm mục tiêu chính trong N0.
- Ghép độc lập vẫn dùng được để ước lượng chênh kỳ vọng; không dùng từng cặp làm phản thực tế của cùng một lần kiểm. Không kết luận hiệu ứng âm là bug.
- Giới hạn: sự thật theo coupling cụ thể của thế giới mô phỏng, chưa phải sự thật của mạng thật.

## 8. Đề xuất, chưa chốt

| ID | Đề xuất | Lý do |
|---|---|---|
| N-T | Sự thật chính = kết quả thực hiện ghép cặp từng lần kiểm (CRN); luôn báo kèm sandbox lý tưởng và biết trước | chấm từng phán quyết cần sự thật từng lần; lý tưởng tách phần không tránh được |
| Metric chính | regret ms/lần kiểm + phân rã | cộng được, không phụ thuộc ε với định nghĩa hiện tại |
| Metric phụ | DN\|hại và TCN\|lợi (luôn cả hai), P(hại\|duyệt), bất đồng với lý tưởng theo hai chiều | đếm một chiều thưởng sự hèn nhát |
| ε | 0,5·S (liên tục với repo cũ); độ nhạy {0,25; 1; 2}·S cho tỉ lệ đếm | regret không cần ε |
| H | [QUYẾT] theo chu kỳ kiểm lại thực tế; gợi ý Codex: chính 0,5 s, khảo sát 5 và 30 s. Chưa nhận lựa chọn tác giả/căn cứ vận hành | phân rã đổi từ 93% xuống 9% theo H/τ |
| N-P | Hai bộ sinh: G_all (đối chứng) + G_greedy (cùng telemetry với twin); để ngỏ G_indep (thông tin khác twin) | DN\|hại đổi gấp đôi giữa hai bộ |

## 9. Ba cột cho template đọc (dùng ở L1.4)

| Đối tượng được chấm (dự báo / phán quyết / hành động) | Sự thật lấy từ đâu (ghép cặp / biết trước / cặp quan sát / testbed) | Mẫu số và lớp dương |
|---|---|---|
| [điền khi đọc paper] | [điền] | [điền] |

## 10. Lịch sử sửa

- 2026-10-02 v0: nháp đầu (hỗ trợ AI). Sửa so với kế hoạch: DN 36,9% (không phải 43%); phân rã bằng regret;
  H không phải núm giảm nhiễu; tỉ lệ theo lớp phụ thuộc bộ sinh.

## 11. Giới hạn của bản lý tưởng và việc tác giả cần làm

- Tách định nghĩa lý thuyết “đúng trạng thái + đúng mô hình” khỏi hiện thực `posterior(W=1e-6, R=0)`. Bản code là xấp xỉ: trừ số gần nhau trong `var_box`, tích phân OU liên tục và quadrature so với world tích phân trên lưới dt=0,05 s.
- Audit đo phương sai điều kiện ở H=0,5 s thấp hơn giới hạn quan sát điểm OU liên tục 1,812%; chưa chứng minh lỗi số này giải thích toàn bộ khác biệt với bảng lesson.
- Phân rã cộng regret đúng trên mẫu. Diễn giải “không tránh được / do sandbox” cần oracle đúng và luận điểm theo kỳ vọng; không coi chênh lệch của mọi mẫu hữu hạn là luôn không âm.
- Mốc lý tưởng t khiến ngẫu nhiên trong khoảng a thuộc tương lai của cả hai sandbox; không quy toàn bộ khoảng a vào phần do sandbox không hoàn hảo như câu hỏi cuối lesson.
- Không bổ sung chi phí bất đối xứng vào metric chính khi N0 chỉ chấm nhóm chuyển, c=0 và chưa đặt ngân sách α cho minh hoạ này.
- Các nguồn/paper nêu trong lesson chưa được kiểm lại ở lượt triển khai; không nâng mức chứng cứ literature.
- [ ] Tác giả chọn H và mốc lý tưởng ở mức nháp, sau đó chốt ở Gate N.
- [ ] Tác giả tính hai ví dụ xác suất trên giấy và tự giải thích ba câu hỏi không nhìn tài liệu.
- [ ] RQ bằng lời tác giả và bài kiểm 3 phút L1.1 chưa có xác nhận hoàn thành.

2026-10-02: Codex cập nhật bằng số đo local, lưu sai lệch với lesson, bổ sung giới hạn ideal/CRN và sửa “tổng” thành “trung bình” regret.

## 12. Liên kết L1.3 (2026-10-02)

[N2](N2_error_sources.md) phân biệt mô tả gap L=z+a với việc chọn chuẩn lý tưởng.
Kết quả n01b và n02 đều giữ mốc t, a=0,05 s. Chưa có quyết định tác giả đổi sang t+a;
không thay diễn giải kết quả L1.2 bằng một chuẩn chưa chạy. Cấu hình n02 (1,1,0)
chỉ gần regret n01b về mặt mô tả, không neo từng bit vì lịch rút nhiễu khác.
