# reference/ — code cũ để ĐỌC, không để CHẠY

Hai nguồn:

- `dt4n_snapshot/`: dự án cũ dt4n, lấy bằng `git show archive-2026-09:<path>`
  (tag `archive-2026-09` → commit `d45cf4ff26d8c6204a181f0fa77887e087a4d381`, đã có trên GitHub).
- `v1_trust_gate/`: hướng v1 của chính repo này, trước pivot (tag `pre-pivot-v14`).

**Quy tắc:** không `import` bất cứ thứ gì từ thư mục này. Không sửa file ở đây. Khi viết lại một chức
năng trong `ndtrisk/`, mở file tương ứng để đối chiếu logic, rồi viết lại gọn hơn.

| File cũ (dt4n_snapshot/) | Đọc để lấy gì | Dùng lại ở v2? |
|---|---|---|
| measurements/sla_calib_v2.py | `ar1_matrix()`: tải AR(1) từng link | Tham khảo cho OU rời rạc chính xác (Phase 3) |
| measurements/build_truth_table.py | Cách dựng `truth_table.parquet` | Chỉ để hiểu provenance (ý nghĩa cột: xem data PROVENANCE) |
| twin/link_model_v2.py | Twin đo được: PCHIP + sigma + domain | Có thể thành biến thể twin sai mô hình (K20) — chưa quyết |
| twin/cost_v2.py, twin/topology_v7.py, twin/link_model.py | Butterfly, cost ghép | Chưa dùng (lõi v2 là hai path) |
| measurements/decision_error_v2.py | Vòng lặp age → a_twin vs a_truth | Chỉ tham khảo |
| cert/conformal_age.py | q̂ theo bin tuổi, split theo block | Baseline conformal (Phase 4) |
| cert/margin_score.py, cert/fallback.py | Margin top-2, ABSTAIN | Thuộc v1; bản port ở `v1_trust_gate/margin.py` |

Muốn xem file khác của dự án cũ: mở repo dt4n tại tag `archive-2026-09`, đừng copy thêm vào đây.
