# Phase 0 defense prep — bản tham khảo của agent

File này hỗ trợ ôn và **không chứng minh tác giả đã tự trả lời**. Trước buổi họp,
tác giả cần nói lại bằng hiểu biết của mình; GVHD có thể hỏi tiếp vào mọi giả định.

## Bảy câu hỏi và khung trả lời

1. **Nếu chỉ là tuổi lớn thì risk cao, có gì mới?**
   Claim không phải quan hệ đơn điệu đó. RQ1 nghiên cứu khi luật conditional theo
   tuổi và margin còn calibration dưới W hữu hạn, phi tuyến, heavy-tail và mismatch.
   RQ2 hỏi gate có đổi risk–coverage so với forecast+Gaussian mạnh hay không.

2. **Luật Gaussian là định lý, còn chạy thí nghiệm để làm gì?**
   Định lý là oracle validity check trong affine Gaussian với tham số thật. Hệ thống
   dùng tham số ước lượng, cost phi tuyến và dữ liệu lệch giả định; thí nghiệm đo
   ranh giới nơi plug-in operational law còn đáng tin và nơi nó thất bại.

3. **Vì sao ε=2 ms?**
   Đây là ngưỡng phân tích neo theo thang delay và sai số đo của D1, chưa phải SLA.
   Thiết kế báo sensitivity 0/0,5/1/5 ms và sẽ đổi mức chính trước test nếu GVHD
   cung cấp ngưỡng vận hành có căn cứ. Không được gọi 2 ms là ý nghĩa người dùng.

4. **D_lin không thật, sao dùng làm tham chiếu?**
   Nó cô lập staleness trong thế giới có luật Gaussian kiểm được, giúp phát hiện
   bug và phân biệt lỗi ước lượng với lỗi mô hình. D0/D1 sau đó kiểm độ cong và
   realism; kết luận ứng dụng không dựa riêng vào D_lin.

5. **Nếu gate hòa forecast+Gaussian ở mọi nơi?**
   Khi đó claim RQ2 về cải thiện coverage bị bác bỏ và phải ghi kết quả âm.
   Contribution còn có thể là bản đồ sufficiency/breakdown của luật operational
   nếu RQ1 đủ mới và vững; nếu DP2 cũng cho thấy luật đơn giản luôn đủ, thu hẹp paper.

6. **Traffic exogenous có thực tế không, khi nào sai?**
   Nó hợp với quyết định tức thời khi traffic là input không bị action hiện tại làm
   đổi trong horizon đo. Nó sai trong closed-loop TE, nơi đổi route đổi tải rồi đổi
   telemetry tương lai. Paper đầu cô lập open-loop; closed-loop là RQ3 ngoài scope.

7. **W=200τ trên Abilene là bao lâu và có đủ dữ liệu không?**
   Chưa thể đổi ra giờ khi chưa ước lượng/chốt τ của trace và sampling interval.
   Câu trả lời đúng hiện tại là phải fit τ trên calibration prefix, tính 200τ theo
   đơn vị thật rồi kiểm history còn lại. Nếu thiếu, ghi amendment và không mượn future.

## Ba câu tự suy nghĩ — đáp án gợi ý

1. Ở e06, báo phân phối κ theo topology/OD, so trong strata κ hoặc đưa κ làm
   covariate mô tả; kiểm residual calibration sau conditioning. Không đồng nhất
   nhiều lỗi thô với luật vỡ hơn khi bài toán vốn khó hơn.
2. Nếu GLOBECOM giới hạn ngắn, thu hẹp RQ1b trước: giữ một kiểm transfer đại diện,
   ưu tiên RQ1a cơ chế và RQ2 so baseline. Validation còn lại dành cho bản mở rộng.
3. Ba lỗi chung một mẫu: quy trình đúng nhưng lấy snapshot/công thức/W_ref làm thật
   trước khi kiểm trạng thái thực tế và câu hỏi có phân biệt được hay không.

## Phần con người bắt buộc, hiện chưa hoàn tất

- Elevator test 2 phút và câu người nghe nhắc lại nguyên văn: **chưa thực hiện**.
- Tác giả tự giải VD7–VD8 không code/AI: **chưa có bằng chứng**; đáp án agent nằm ở
  `06_definitions.md` chỉ để đối chiếu sau.
- Tập nói 7 câu bằng lời tác giả và trả lời câu hỏi vặn: **chưa thực hiện**.

