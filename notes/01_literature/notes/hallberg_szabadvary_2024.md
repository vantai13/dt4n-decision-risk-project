# Hallberg Szabadváry 2024 — ACI cho multi-step forecasting

| Trường | Giá trị |
|---|---|
| Tác giả | **Johan Hallberg Szabadváry** (một tác giả) |
| Nguồn | [PMLR 230:250–263](https://proceedings.mlr.press/v230/hallberg-szabadvary24a.html); [arXiv:2409.14792](https://arxiv.org/abs/2409.14792) |
| Trạng thái | Proceedings of COPA 2024 |
| Mức kiểm | 2026-09-23: PDF PMLR §3–5, Eq. (8)–(10), bảng 1–3 |
| Lượt đối chiếu nguồn | 2; lượt sau kiểm lại Eq. (8)–(10) và horizon `h=5` trong PDF ngày 2026-09-23 |
| Mức đe dọa | Cao cho claim “ACI riêng từng horizon/age bin là mới” |

**[F]** Bài duy trì vector target error và learning rate riêng cho từng bước dự báo, cập nhật ACI khi outcome của từng horizon được quan sát (Eq. 8, §3). Mỗi horizon có cận tần suất miscoverage dài hạn, và cả mức trung bình qua horizon cũng vậy (Eq. 9–10, §3). Đây là coverage-frequency, không phải coverage conditional cho một quyết định cụ thể.

**[F]** Ví dụ dùng dự báo nhu cầu điện Victoria 5 giờ. Khi target error đều 0,1, empirical error của hour 1–5 là 0,102; 0,102; 0,0964; 0,0905; 0,0869 (bảng 1, §4). Khi target error thay đổi 0,1→0,3, khoảng dự báo hẹp hơn (bảng 2). Tác giả nói rõ ví dụ chỉ minh họa phương pháp, **không phải comparative evaluation đầy đủ** (§4).

**[I] So với đề tài:** per-horizon ACI là baseline trực tiếp nếu age được rời rạc thành bins, nhưng “forecast horizon” không tự động bằng “telemetry age”, và score là forecast miss chứ không phải pairwise route-cost/ranking error. Cần so global ACI, per-age ACI và đề xuất trên cùng dữ liệu/feedback. Không claim phần chia horizon/bin tự nó mới.

**[?] Còn mở:** nếu các age bins có tần suất rất lệch, tốc độ hội tụ và utility ra sao; nếu ABSTAIN không nhận được label counterfactual, Eq. 8 có áp dụng được không?
