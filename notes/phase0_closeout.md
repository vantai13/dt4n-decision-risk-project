# Phase 0 closeout — 2026-09-23

**Kết luận: ĐẠT CÓ ĐIỀU KIỆN (C1–C4).** Người hướng dẫn thay thế: Claude
(AI), theo D14; kết luận này không thay xác nhận học vụ của GVHD người thật.

Plan tham chiếu: PHASE_0 SHA256 **chưa khả dụng** vì file private không có trong
workspace khi đóng gate. Khi tìm thấy, chỉ bổ sung hash bằng một đính chính;
không commit plan và không thay bằng hash của nội dung chat.

## Validity

| Điều kiện | Trạng thái | Bằng chứng |
|---|---|---|
| Repo cũ archive; repo mới khớp thực tế; F0-1…F0-5 đóng | Đạt | tag `archive-2026-09` → `d45cf4f`; bundle WIP SHA256 `1a08c2f9f2b4a9c125854c96af718d657ab1246b5fa1eeba82d9389530145028` + bản Drive; `wip-stash-before-archive` đã push; `wip-before-archive` → C4 |
| Brief v1: RQ tách loại, hypothesis có số, kill criteria | Đạt có điều kiện (C2, C3) | `00_research_brief.md` tại `cd04954`, sửa D12 tại `de4030b`; elevator test chưa làm |
| Definitions: estimand đủ cột, không trùng tên | Đạt có điều kiện (C1) | `06_definitions.md` v1; VD2–VD8 hiện là lời giải agent và đã khai báo |
| Design: W_ref cụ thể, không suy biến; mỗi eNN một chiều | Đạt | `05_experiment_design.md` §1: κ_ref=0,5, b=4,281255 ms; D12 |
| D2–D12 có ADR; research contract được review | Đạt (người hướng dẫn thay thế) | `02_decision_log.md` D2–D15; `meetings/2026-09-23.md`; giới hạn thẩm quyền theo D14 |

## Điều kiện

| Mã | Việc | Hạn | Cách kiểm |
|---|---|---|---|
| C1 | Tự giải tay VD7, VD8, không code/AI; gửi người hướng dẫn chấm | Trước khi mở L1.3 | Thêm nguyên văn bài tự giải vào `06_definitions.md` §4 dưới mục “Tự giải của tác giả”, tách khỏi đáp án agent |
| C2 | Elevator test 2 phút với một người thật ngoài ngành | Trước DP1 | Câu người nghe nhắc lại, nguyên văn, trong brief §11 |
| C3 | Tự trả lời 7 câu bảo vệ bằng lời mình, không nhìn `08_phase0_defense_prep.md` | Buổi review DP1 | Người hướng dẫn hỏi vặn; ghi câu trả lời và nhận xét vào biên bản DP1 |
| C4 | Push `wip-before-archive` bằng SSH hoặc PAT có scope `workflow`; kiểm VM GCP trước khi xóa/snapshot | Trước Phase 6 | `git ls-remote`; dòng append-only trong `04_bootstrap_verification.md` |

Nếu một điều kiện quá hạn: thêm dòng đính chính cuối file theo mẫu
`Cx không đạt hạn, gate mở lại`; không sửa bảng lịch sử trên. DP1 không được PASS
khi C1–C3 chưa đạt.

## Outcome

| Mục | Ghi lại |
|---|---|
| Venue chính / dự phòng | CNSM 2027 main/full / GLOBECOM 2027, theo D15 |
| Ngày muộn nhất xong thí nghiệm | Mốc nội bộ 2026-12-31; tính lại theo deadline−6 tuần khi CFP 2027 ra |
| Bản thảo đầy đủ | Mốc nội bộ 2027-02-15 |
| Quyết định người hướng dẫn thay thế | D15: RQ1b thu gọn; D5 với f≤0,1σ; e03 dùng DV không phụ thuộc ε; venue và ranh giới AI |
| ε | 2 ms chính; sensitivity {0;0,5;1;5} ms; e03 báo kèm ε/σ_D |
| Số claim confirmatory | ≤6; dự kiến RQ1a:3, RQ1b:1, RQ2:2; e01 là validity; đăng ký cụ thể trước từng batch |

## Mang sang Phase 1

- C1 trước L1.3; C2 và C3 trước DP1.
- Đọc full text OpenTwin v2, Zhu et al. và Guérin–Orda; xác nhận hoặc bác bỏ
  các ô SUY LUẬN trong novelty matrix.
- Tự dẫn định lý xác suất đảo A1–A7 trước khi viết simulator; e01 chỉ chạy sau L1.3.

## Đính chính sau rà soát — 2026-09-23 (D16)

Bảng trên lưu kết luận tại commit `316ee7f`; các cách diễn đạt sau cần đọc cùng
đính chính này. Tag `phase-0-complete` vẫn là mốc đạt có điều kiện, C1–C4 chưa
có bằng chứng hoàn tất trong lần rà soát này.

- Dòng repo có việc `wip-before-archive`/VM còn treo: trạng thái phù hợp là
  **Đạt có điều kiện (C4)**, không hiểu “F0-1…F0-5 đóng” là mọi việc đã xong.
- Dòng design: sửa “mỗi eNN một chiều” thành “khung biến/đối chứng đã ghi;
  e05 là factorial, config e06–e12 còn phải chốt”. Đạt ở mức khung Phase 0,
  chưa đủ để chạy mọi batch confirmatory.
- Dòng review dùng trạng thái **Đạt** trong quy trình nội bộ theo D14;
  bằng chứng là review AI do tác giả chuyển tiếp, không phải phê duyệt học vụ.
- C1 phải khai đã được cung cấp đáp án VD7–VD8; bài làm lại có thể kiểm hiểu bài,
  không được ghi là giải mù trước khi xem lời giải.
- Mốc thí nghiệm là 2026-12-31. Quy tắc deadline−6 tuần so với mốc bản thảo
  2027-02-15 cho deadline sớm nhất theo kế hoạch là 2027-03-29; chờ CFP thật.
- D5 và cách diễn giải selective_risk_ratio được giới hạn theo D16/design §7.
