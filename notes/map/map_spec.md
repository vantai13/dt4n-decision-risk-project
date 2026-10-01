# Map spec v0 — viết và commit TRƯỚC khi chạy run_scan (ngày: 2026-10-01)

## Câu hỏi

Có vùng nào mà K2 (dùng bất định) thắng SC (ngưỡng cố định trên tâm của twin) đáng kể không?

## Bản đồ (chép từ grid.py)

r_f {30k, 300k} · τ {2, 10, 60} · T_tel_A {0.5, 5} · probe_B {same, 30} · ρ̄_B {0.95, 0.85} · α {1%, 0.2%} → 96 ô

## Dự đoán (viết tay, trước khi chạy)

- Trục quyết định nhất theo tôi: `probe_B`, vì chu kỳ probe 30 s làm độ tươi và phương sai hậu nghiệm của path B khác path A ngay cả khi hai quyết định có cùng tâm Ī; `alpha` là trục phụ mạnh vì ngân sách harm chặt làm khả năng phân hạng theo rủi ro có giá trị hơn.
- Vùng tôi đoán có ứng viên: `probe_B=30`, `alpha=0.002`, đặc biệt khi `T_tel_A=0.5`, `r_f=300k`, `tau` vừa hoặc chậm; `rho_B=0.85` có thể giúp tạo đủ quyết định gần biên mà vẫn có gain.
- Vùng tôi đoán chắc chắn âm: `probe_B=same`, nhất là khi hai path cùng `rho_B=0.95`, vì độ rộng bất định gần ranh giới quyết định gần như đồng đều nên K2 khó hơn SC đáng kể.
- Số ô ứng viên tôi đoán: 8/96.

## Tiêu chí ứng viên (KHÓA — chép từ run_scan.py)

cận dưới CI của width > 0 · width ≥ 2% headroom · width ≥ 20% gain SC · ≥ 10 flow nền

## Quyết định

≥ 1 ứng viên → kiểm tính thực tế + novelty + DES · 0 ứng viên → PIVOT trong mô hình này
