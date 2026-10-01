# Frontier v0 — kết quả so cùng ngân sách harm

## Kiểm tra và tiền đăng ký

8/8 test đạt (3,55 giây). Code, test và dự đoán được khóa ở commit 9a77bde trước khi chạy. Đã chạy đủ đối chứng âm và 9 ô trên nhánh frontier-v0; tiến trình kết thúc mã 0.
Mã tính được giữ đúng theo hướng dẫn. Các số dưới đây chép từ log, đã làm tròn theo định dạng của chương trình; lần chạy này không xuất CSV số đầy đủ hay hình đường cong.

## Kết quả

Đơn vị headroom, gain và Δ là ms. CI là percentile bootstrap 95%, 300 lần lấy mẫu lại theo seed. Harm ratio là harm tối thiểu K2 cần để đạt gain SC chia α.

| Ô | Headroom | Gain SC | Gain K2 | Δ cùng ngân sách harm [CI 95%] | % headroom | % SC | Harm ratio |
|---|---:|---:|---:|---|---:|---:|---:|
| NEG_P2_cu | 15,311 | 4,112 | 4,188 | +0,076 [−0,014; +0,173] | 0,50 | 2 | 0,96 |
| m069 | 17,989 | 1,465 | 2,113 | +0,648 [+0,318; +0,986] | 3,60 | 44 | 0,49 |
| m071 | 9,733 | 1,000 | 1,243 | +0,243 [+0,112; +0,366] | 2,50 | 24 | 0,63 |
| m085 | 9,531 | 0,910 | 1,628 | +0,719 [+0,549; +0,930] | 7,54 | 79 | 0,24 |
| m070 | 8,376 | 1,416 | 1,742 | +0,327 [+0,213; +0,442] | 3,90 | 23 | 0,62 |
| m087 | 6,846 | 0,947 | 1,507 | +0,560 [+0,373; +0,791] | 8,19 | 59 | 0,27 |
| m084 | 7,714 | 1,728 | 2,223 | +0,494 [+0,347; +0,704] | 6,41 | 29 | 0,57 |
| m086 | 5,082 | 1,236 | 1,568 | +0,332 [+0,212; +0,455] | 6,54 | 27 | 0,54 |
| m080 | 1,192 | 0,340 | 0,430 | +0,090 [+0,074; +0,102] | 7,58 | 27 | 0,34 |
| m083 | 0,993 | 0,233 | 0,291 | +0,058 [+0,040; +0,079] | 5,81 | 25 | 0,50 |

## Diễn giải

Cả 9 ứng viên có cận dưới CI Δ > 0. Đối chứng âm có CI chứa 0 và harm ratio gần 1. Trung bình của đối chứng khớp ví dụ hướng dẫn (+0,076 ms); CI chạy thực tế là [−0,014; +0,173], khác CI ví dụ [−0,009; +0,198]. Không chỉnh RNG hoặc chạy lại để ép khớp ví dụ; chưa xác định nguyên nhân chênh CI.

m069 và m071 giữ lợi thế khi hai họ luật được tối ưu dưới cùng trần harm. Kết quả này hỗ trợ rằng chênh gain bậc C không chỉ phản ánh việc K2 dùng harm nhiều hơn. Tuy nhiên không thể lấy chênh giữa width C và Δ frontier để phân rã chính xác phần gain do harm, vì điểm vận hành được chọn theo cách khác.

Harm ratio 0,49 và 0,63 nghĩa là K2 cần khoảng 49% và 63% ngân sách α để đạt gain SC tại ngân sách α. Không khẳng định đây là giảm 51% và 37% so với số harm SC thực sự dùng: công cụ không xuất số harm thực dùng của SC tại điểm tối ưu.

Hai ô cùng nhịp vẫn có Δ dương rõ. Vì vậy dữ liệu không hỗ trợ claim tuyệt đối rằng bất định CHỈ hữu ích khi độ tươi hai path lệch nhau. Câu phù hợp hơn: hiệu ứng lớn hơn về ms trong nhóm probe B thưa được khảo sát; hai ô cùng nhịp có lợi ích tuyệt đối nhỏ.

## Đối chiếu dự đoán và ý nghĩa thực tế

- Dự đoán 7/9 ô có CI dưới > 0; đo được 9/9.
- m069: dự đoán Δ 0,5–0,9 ms đúng; harm ratio 0,49 hơi thấp hơn khoảng đoán 0,5–0,8.
- m071: Δ 0,243 ms và harm ratio 0,63 nằm trong khoảng đoán.
- m080/m083: đúng dự đoán Δ dưới 0,2 ms; headroom chỉ khoảng 1 ms.
- Δ lớn nhất là 0,719 ms ở m085, khoảng 8,9% của SESOI VoIP 8,1 ms. Không ô nào đạt SESOI delay đã khóa. Giữ nguyên SESOI của claim cũ.

## Phạm vi suy luận

Đây là frontier thực nghiệm tối ưu trên chính dữ liệu test, cùng các seed đã dùng ở confirm, không phải một xác nhận độc lập ngoài mẫu. Bootstrap chỉ lấy mẫu lại test seed, giữ quỹ đạo tham chiếu đã học từ calibration; chưa phản ánh bất định do học calibration và chưa hiệu chỉnh nhiều phép kiểm.

Chương trình so các tiền tố xếp hạng dưới cùng trần harm, không đảm bảo harm thực dùng bằng nhau chính xác. Mã cung cấp xét mọi tiền tố, kể cả khi score trùng nhau; ở K2, score −inf biểu diễn Ibar≤0 nhưng best_gain không loại các phần tử đó. Do đó cách gọi chính xác của đầu ra hiện tại là frontier tiền tố theo mã đã cung cấp; trước khi dùng như frontier ngưỡng triển khai chính xác, cần kiểm điểm tối ưu không cắt giữa nhóm đồng điểm hoặc lấy phần tử K2 không được phép đổi. Lần chạy này chưa xuất ngưỡng/tiền tố tối ưu để kiểm điều đó.

## Bước tiếp theo

Kết quả hỗ trợ tiếp tục ánh xạ telemetry và thang thời gian sang hệ thống thật có nguồn, kiểm novelty, và trao đổi với thầy về metric cùng SESOI của ứng dụng cho giai đoạn sau. Không đổi metric chỉ vì harm ratio trông lớn. Chưa chạy thêm kịch bản hoặc thực hiện rà soát nguồn/novelty trong bước frontier này.

## Artifact

- results/scan/frontier_output.txt: toàn bộ số đo xuất bởi lần chạy.
- notes/map/frontier_spec.md: dự đoán trước chạy.
- experiments/scan/frontier.py: mã so frontier.
- tests/test_scan.py: 8 test nền móng.
