# Chuẩn bị GO-check Bước 2 — kiểm validity

Ngày 2026-10-01. Nền `8876e12`, nhánh `rollout-v6`; các thay đổi mới chưa commit.

## Việc đã hoàn thành

- Tách fresh Bước 1 sang cal 92001–92020 / test 93001–93020.
- Dành cal 94001–94020 / test 95001–95020 cho Bước 2.
- Thêm sổ seed; giữ 90001/91001 cho rollout v6.
- Thêm code ba bố trí FIX/SYM/FF trên cùng thế giới DES; RNG telemetry
  bổ sung riêng [seed, 424242].
- Dịch TC3 sang rollout, giữ m=8,1 ms, r=10% và quy tắc CI L1.5.
- Gộp hai dòng cooldown ở báo cáo Bước 1; giữ output thô để đối chiếu.
- Thêm guard chặn fresh/outcome nếu spec chưa điền dự đoán, chưa đánh dấu
  locked hoặc chưa commit đúng nội dung.

## Kết quả validity trên seed cũ

| Kiểm | Kết quả |
|---|---|
| V1: seed 80001 và 81001, thông tin gốc và delay DES bằng go_test.simulate từng bit | True cho cả hai |
| V2: rollout FIX bằng rollout.py, 4 tổ hợp luật/ngưỡng/cooldown | True |
| V3: neo FIX, α=0,2%, cooldown 0 | +1,652 [1,225; 2,080] ms |
| V4: telemetry A bổ sung nhịp 60 s | tuổi TB 30,07 s; tải đo TB 0,804 |
| V4: telemetry B bổ sung nhịp 1 s | tuổi TB 0,55 s; tải đo TB 0,798 |
| V5: pipeline SYM/FF, đầu ra twin và rollout smoke hữu hạn | True; không in hiệu ứng SYM/FF |
| V6: tuổi telemetry twin nhận ở cả sáu ô FIX/SYM/FF × path hiện tại | Đạt; xem bảng bên dưới |

### V6 — kiểm trực tiếp nối dây

| Bố trí | Luồng đang ở | Tuổi TB A | Tuổi TB B | Thấy / mong đợi |
|---|---|---:|---:|---|
| FIX | A | 1,00 s | 30,25 s | TC / TC |
| FIX | B | 1,00 s | 30,25 s | TC / TC |
| SYM | A | 1,00 s | 0,17 s | TT / TT |
| SYM | B | 1,00 s | 0,17 s | TT / TT |
| FF | A | 1,00 s | 30,25 s | TC / TC |
| FF | B | 30,04 s | 0,17 s | CT / CT |

T = tươi (tuổi TB < 2 s), C = cũ (tuổi TB > 10 s). V6 dùng seed
81001 từ cache go0_test; không chạy/tune SC/K2 hoặc mở seed mới.
arrangement_inputs vẫn tính đầu ra twin như API hiện tại; phần kiểm
chỉ đọc age_A/age_B. V6 thoát lỗi nếu bất kỳ ô nào sai.

V4 kiểm tuổi trong biên 5 sai số chuẩn của pha đo và tải trung bình cách
rho_bar không quá 0,05. V3 kiểm số neo trong sai số làm tròn 0,0006 ms.
Nếu bất kỳ kiểm nào trượt, validity thoát lỗi.

**Validity V1–V6: ĐẠT.** Kiểm toàn repo gần nhất trước khi thêm script V6:
138/138 test đạt. Script V6 mới đã chạy trực tiếp và khớp output hướng dẫn.
Guard cho cả hai spec draft đã được kiểm và dừng trước simulator.

## File

- Output: `results/gocheck/info_validity_output.txt`.
- Output V6: `results/gocheck/wiring_validity_output.txt`.
- Code V6: `experiments/gocheck/check_wiring.py`.
- Code: `experiments/gocheck/info_arrangement.py`.
- Spec Bước 2: `notes/gocheck/info_arrangement_spec.md`.
- Spec Bước 1: `notes/gocheck/GO_check_spec.md`.
- Sổ seed: `notes/seed_registry.md`.
- Đính chính SESOI: cuối `notes/02_decision_log.md`.

## Còn chờ

Tác giả điền dự đoán cho cả hai spec. Sau đó khóa/commit spec trước fresh và
outcome, ghi kết quả ở commit riêng. Chưa mở seed 92001/93001/94001/95001.
Tìm nguồn TC2 và bảng phán quyết GVHD sẽ cập nhật sau outcome; hiện chưa có
bằng chứng ngoài đời mới cho FIX/FF hoặc cadence 1 s.
