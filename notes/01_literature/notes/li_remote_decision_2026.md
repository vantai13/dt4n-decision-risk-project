# Li et al. 2026 — From Freshness to Effectiveness (AR-MDP)

| Trường | Giá trị |
|---|---|
| Tiêu đề đầy đủ | From Freshness to Effectiveness: Goal-Oriented Sampling for Remote Decision Making |
| Tác giả | Aimin Li; Shaohua Wu; Gary C. F. Lee; Sumei Sun |
| Nguồn | arXiv:2504.19507v3 (06/02/2026); DOI 10.1109/TIT.2026.3663678 (theo ghi chú 23/09) |
| Trạng thái | theo DOI: IEEE Trans. Inf. Theory [?]; bản sớm ở IEEE ITW 2024 (chú thích của bài) |
| Lượt đã đọc | 2 — §I–VII; §VIII-A, VIII-B một phần; Fig. 7–10 chỉ chú thích; phụ lục chưa đọc |
| Ngày đọc | 2026-09-30 (nâng từ abstract 23/09) — Claude (AI) đọc và soạn; tác giả kiểm |
| Mức đe doạ novelty | trung bình cho câu "độ tươi ≠ giá trị quyết định"; thấp cho phân rã và so ngưỡng đã tune |

## 0. Five Cs
- Category: lý thuyết + thuật toán (MDP có ràng buộc, quan sát trễ).
- Correctness: không gian hữu hạn; hành động giữ nguyên giữa hai lần nhận mẫu (A1); mẫu mới chỉ sau khi mẫu trước tới (S1).
- Contributions (§II-C): AR-MDP; thống kê đủ hữu hạn chiều; τ-RVI, OnePDSI, QuickBLP; ngưỡng tần suất lấy mẫu.
- Quyết định: lượt 2 đủ cho định vị.

## 1. Một câu
Cùng thiết kế lấy mẫu và quyết định từ xa khi số đo tới trễ ngẫu nhiên, coi tuổi là thông tin phụ, và chỉ ra ngưỡng
tần suất lấy mẫu mà vượt qua thì không cải thiện quyết định.

## 2. Problem · Assumptions
- Problem [F Problem 1]: tối thiểu chi phí TB dài hạn, ràng buộc tần suất lấy mẫu f_max.
- A1 [F §III]: nguồn là MDP hữu hạn; trễ độc lập với nguồn, bị chặn. A2 [F (S1)]. A3 [F (A1)].

## 3. Method
Lemma 1: (giá trị mẫu mới nhất, tuổi lúc nhận, hành động trước) là thống kê đủ ⇒ cùng giá trị đo, tuổi khác có thể
cho quyết định tối ưu khác. Dinkelbach → MDP chuẩn; τ-RVI khử tính tuần hoàn làm RVI dao động; QuickBLP thêm một LP
khi ràng buộc cắn. Thm 9 / Cor. 2: f_max ≥ f_max^T thì nới ràng buộc không thêm lợi.

## 4. Evaluation
| Setup | Baseline | Metric | Kết quả chính | § |
|---|---|---|---|---|
| MDP 2 trạng thái × 2 hành động (Fig. 11, App. H); trễ nhị phân / hình học cắt | lấy mẫu đều, zero-wait, constant-wait, AoI-optimal, mỗi cái + policy tối ưu dài hạn dùng quan sát mới nhất (không dùng tuổi); myopic | chi phí TB | [?] số chỉ có trong Fig. 7–10, chưa đọc | §VIII |

## 5. Claim ↔ Evidence
| # | Claim | Loại | Phủ tới đâu | Khe hở? | § |
|---|---|---|---|---|---|
| 1 | Tuổi là thông tin phụ cho quyết định | định lý | MDP hữu hạn | Không | Lemma 1 |
| 2 | Có ngưỡng tần suất lấy mẫu | định lý | như trên | Không | Thm 9, Cor. 2 |
| 3 | Co-design tốt hơn baseline | mô phỏng | một MDP 2×2 | Có — đồ chơi | §VIII |

## 6. Limitation
- Tác giả [F Remark 2]: nới (A1) dẫn tới belief-MDP. Tôi thấy [I]: baseline không dùng tuổi ⇒ khoảng cách lẫn
  "giá trị của tuổi" với "giá trị lấy mẫu"; không có ngưỡng tĩnh đã tune.

## 7. So với đề tài
- Trùng: tuổi là Z loại (a) (T4 §1).
- Khác, ĐÃ KIỂM: nguồn Markov hữu hạn, không hàng đợi, không ngân sách harm, không oracle cùng thông tin, không phân rã.
- [I] A1 của tôi (e^(−z/τ) chỉ 0,890–0,935) cho thấy giá trị của tuổi có thể nhỏ — không mâu thuẫn Lemma 1.
- Dùng được: Cor. 2 là khung cho câu hỏi Phase 2 "probe path phụ dày tới đâu thì hết lợi" (F7a).

## 8. Câu định vị
"Li et al. chứng minh tuổi là thông tin phụ cho quyết định và có ngưỡng lấy mẫu vượt qua thì hết lợi (Lemma 1, Cor. 2)
trên MDP hữu hạn; đề tài đo, trong DES hàng đợi, phần giá trị nào của đổi/giữ đến từ tâm, độ rộng, an toàn hay
thông tin, so với ngưỡng đã tune và oracle cùng thông tin."
