# Search log — Phase 1 / Lesson 1.2

Ngày bắt đầu: 2026-09-23. Trạng thái: **đang thực hiện**, chưa đủ điều kiện kết luận độ phủ hoặc DP1.

## Phạm vi và quy tắc sàng lọc

Protocol này được ghi **sau một lượt tìm thử và sau khi OpenTwin đã được đọc**. Vì vậy đây là đăng ký muộn, không được trình bày như một protocol đã chốt trước mọi tìm kiếm. Dùng cùng quy tắc cho các lượt tiếp theo; ghi mọi thay đổi với ngày và lý do.

- **I1:** quyết định routing/điều khiển dưới state cũ, trễ hoặc bất định.
- **I2:** gate, từ chối, fallback hoặc chứng nhận chất lượng của quyết định.
- **I3:** tuổi thông tin/độ trễ có hệ quả lên sai số, quyết định hoặc coverage.
- **I4:** calibration/conformal trực tuyến dưới phụ thuộc thời gian hoặc phản hồi trễ.
- **E1:** chỉ dự báo state, không có quyết định hoặc calibration, trừ tài liệu nền về freshness.
- **E2:** chỉ tối ưu lịch truyền/cập nhật mà không xét chất lượng state hoặc quyết định, trừ tài liệu nền.
- **E3:** không tìm được full text tiếng Anh: giữ metadata và gắn cờ, không suy diễn từ abstract thành kết luận full text.
- **Rất gần:** có quyết định/chứng nhận cho route hoặc action dưới dữ liệu cũ, hoặc đúng một trong hai mô tả bên dưới.
- **Gần:** thỏa ít nhất hai I nhưng chưa cùng trust target. **Nền:** thỏa một I và cần cho mô hình/phương pháp.

Hai mô tả đối kháng: (C-a) tuổi/thang nhớ cùng margin giải thích flip hoặc regret của routing; (C-b) conformal/ACI có điều kiện theo age/horizon để chấp nhận route/action hoặc bật fallback. Đặc biệt phân biệt *tuổi telemetry khi quyết định* với *độ trễ quan sát nhãn để cập nhật calibration*.

Điều kiện dừng dự kiến: một vòng backward/forward snowballing hoàn chỉnh không thêm bài **rất gần**, hoặc hết 5 ngày làm việc; nếu hết thời gian, ghi backlog và không claim tìm kiếm bão hòa. Mỗi nguồn phải ghi chuỗi, ngày, tổng kết quả mà giao diện thật sự cung cấp, số tự xét tiêu đề/abstract/full text. Không điền số giả khi công cụ không trả tổng hoặc danh sách đầy đủ.

## Nhật ký truy vấn web — lượt thăm dò 2026-09-23

Công cụ tìm web dùng để phát hiện ứng viên, sau đó đối chiếu trang/PDF của tác giả, arXiv hoặc proceedings. Công cụ không trả tổng số kết quả hay toàn bộ thứ tự kết quả riêng cho mỗi truy vấn ghép; vì vậy **chưa có phễu PRISMA có thể tái lập**. Dấu `—` nghĩa là không đo được, không phải 0.

| # | Nguồn | Chuỗi tìm nguyên văn | Tổng / qua tiêu đề / qua abstract | Ứng viên phát hiện hoặc kiểm lại | Trạng thái |
|---|---|---|---|---|---|
| Q1 | Web | `"stale link state" routing uncertainty decision margin` | — / — / — | Shaikh et al. 2001; truy vấn quá hẹp, cần chạy lại ở IEEE Xplore | thăm dò |
| Q2 | Web | `"digital twin" network "conformal" action gate` | — / — / — | OpenTwin v2; thêm một DT ngoài mạng | thăm dò |
| Q3 | Web | `"conformal" "delayed feedback" adaptive online` | — / — / — | El Halabi & Brandt 2026 | full text |
| Q4 | Web | `"conformal" "backup policy" safe decisions` | — / — / — | Lekeufack et al. 2023/2024 | full text |
| Q5 | Web | `"age of information" routing decision control uncertainty` | — / — / — | Cần tách route *gói cập nhật* khỏi route *được chọn bằng telemetry cũ* | thăm dò |
| Q6 | Web | `"conditional coverage" delay staleness horizon conformal` | — / — / — | Conditional coverage là họ nền; chưa phát hiện C-b đúng nghĩa | thăm dò |
| Q7 | Web | `"Ornstein-Uhlenbeck" "age of information" estimation` | — / — / — | Ornee & Sun 2021 | full text |
| Q8 | Web | `"stale telemetry" "digital twin" routing` | — / — / — | Chưa thấy bài rất gần trong kết quả trả về | thăm dò |
| Q9 | Web | `"margin" "stale" "routing" conformal` | — / — / — | **Attri 2026 CERT** qua truy vấn liên quan; cần kiểm kỹ | abstract/full-text hiển thị một phần |

## Truy vấn arXiv API có tổng đếm — 2026-09-23

Nguồn: `https://export.arxiv.org/api/query`, `search_query` đúng như cột dưới, `start=0`, `max_results=20`, `sortBy=relevance`, `sortOrder=descending`; `totalResults` do API trả. Mọi truy vấn có ≤20 kết quả nên toàn bộ tiêu đề đều được xét. Số “qua abstract” là số giữ cho vòng đọc tiếp, **không** phải số đã kiểm full text. arXiv không bao gồm engrXiv nên batch này **không thể phát hiện CERT**.

| # | `search_query` | Tổng | Qua tiêu đề | Qua abstract | Ứng viên giữ / lý do loại chính |
|---|---|---:|---:|---:|---|
| A1 | `all:"adaptive conformal" AND all:"delayed feedback"` | 2 | 2 | 1 | El Halabi & Brandt; bài ECG ngoài domain |
| A2 | `all:"conformal" AND all:"decision" AND all:"backup policy"` | 1 | 1 | 1 | Conformal Decision Theory |
| A3 | `all:"conditional coverage" AND all:"horizon"` | 2 | 0 | 0 | Không bài nào đúng forecasting/age gate |
| A4 | `all:"stale" AND all:"routing" AND all:"conformal"` | 2 | 0 | 0 | Từ trùng nhưng không cùng bài toán; **không phát hiện CERT** |
| A5 | `all:"digital twin" AND all:"conformal" AND all:"action"` | 2 | 2 | 2 | OpenTwin; DT xử lý nước thải (domain khác, gate tương tự) |
| A6 | `all:"age of information" AND all:"routing" AND all:"decision"` | 7 | 4 | 1 | Qi et al. 2026 selective offloading; các bài còn lại chủ yếu route *bản tin cập nhật* |
| A7 | `all:"Ornstein-Uhlenbeck" AND all:"age of information"` | 4 | 1 | 1 | Ornee & Sun 2021 |
| A8 | `all:"conformal" AND all:"route planning"` | 2 | 2 | 1 | Tang et al. 2025 CQR-GAE; compact conformal subgraphs chưa có quyết định dưới state cũ |
| A9 | `all:"margin" AND all:"stale" AND all:"routing"` | 4 | 0 | 0 | Nhiễu từ vựng, không có route trust liên quan |

Tổng **26 bản ghi theo truy vấn**, chưa deduplicate giữa truy vấn; **7 lượt qua abstract** tính theo dòng truy vấn. Cần mở rộng nguồn và chuỗi tìm, vì exact phrase có precision cao nhưng recall thấp.

## Đợt formal F — sau commit protocol `99fb868`, 2026-09-23

Nguồn: arXiv API `https://export.arxiv.org/api/query`; `start=0`, `max_results=100`, `sortBy=relevance`, `sortOrder=descending`. Mỗi query trả ≤100 bản ghi nên tất cả tiêu đề đã được sàng. Số liệu dưới đây tính trực tiếp từ [bảng sàng lọc 74 bản ghi](screening_formal_2026-09-23.csv); mỗi bản ghi có arXiv ID, tiêu đề, quyết định ở tầng tiêu đề/abstract và lý do. Tổng là **lượt kết quả theo query**, chưa khử trùng lặp giữa các query. Thời gian chạy: sau 18:25:15 +07:00 cùng ngày (thời điểm commit protocol).

| # | `search_query` nguyên văn | Kết quả | Qua tiêu đề | Qua abstract | Ứng viên chính |
|---|---|---:|---:|---:|---|
| F1 | `all:"stale link state" AND all:routing` | 0 | 0 | 0 | Cú pháp exact quá hẹp |
| F2 | `all:"digital twin" AND all:conformal AND all:network` | 9 | 4 | 3 | OpenTwin; DT nước thải; DT nước/adaptive sampling |
| F3 | `all:"adaptive conformal" AND all:"delayed feedback"` | 2 | 2 | 2 | El Halabi–Brandt; ConformalShift |
| F4 | `all:conformal AND all:decision AND all:fallback` | 2 | 1 | 1 | Fallback-safe MPC (liên quan cấu trúc fallback) |
| F5 | `all:"age of information" AND all:routing AND all:decision` | 7 | 5 | 2 | Qi et al. selective offloading; task-oriented AoI |
| F6 | `all:"age of incorrect information" AND all:decision` | 32 | 5 | 2 | Maatouk et al.; joint age-state belief |
| F7 | `all:"selective prediction" AND all:routing` | 14 | 4 | 2 | **LEC**; Available Guardrails (routing ở đây là model/intent routing) |
| F8 | `all:"conditional coverage" AND all:delay` | 0 | 0 | 0 | Cú pháp exact quá hẹp |
| F9 | `all:"Ornstein-Uhlenbeck" AND all:"age of information"` | 4 | 2 | 2 | Ornee–Sun; VoI latent models |
| F10 | `all:"stale telemetry" AND all:"digital twin"` | 0 | 0 | 0 | Cú pháp exact quá hẹp |
| F11 | `all:"route planning" AND all:conformal` | 2 | 2 | 1 | Tang et al. CQR-GAE |
| F12 | `all:"top-2 margin" AND all:routing` | 2 | 0 | 0 | Nhiễu từ vựng, không cùng bài toán |

**Tổng F:** 74 lượt kết quả → 25 qua tiêu đề → 15 qua abstract. Số 0 ở F1/F8/F10 cho thấy cần thêm từ đồng nghĩa và nguồn khác, không chứng minh vắng mặt công trình. Bản ghi trên arXiv [LEC: Selection-Conditioned Risk Control](https://arxiv.org/abs/2512.01556) chạm trực tiếp mẫu số `risk | ACCEPT` nhưng kiểm trên dự đoán của mô hình, không phải route cost trong mạng; [Available Guardrails](https://arxiv.org/abs/2609.22048) phân tích tính khả thi của certificate khi dữ liệu calibration ít. Hai bài này cần có trong baseline/thảo luận.

## Ứng viên và mức kiểm

| Bài | Link gốc | Mức kiểm ngày 2026-09-23 | Mức gần / lý do |
|---|---|---|---|
| Attri, *CERT: Certified Route Planning under Drifting Costs* (2026) | [DOI](https://doi.org/10.31224/7306), [toàn văn tác giả đăng](https://www.researchgate.net/publication/406966969_CERT_Certified_Route_Planning_under_Drifting_Costs_Conformal_certificates_sense-to-certify_and_the_price_of_staleness) | các đoạn §1–7 và một phần Appendix qua toàn văn hiển thị; chưa đối chiếu PDF gốc/proof đầy đủ | **rất gần**: route cost cũ, conformal, tuổi, certificate |
| El Halabi & Brandt, *ACI Under Delayed Feedback* (2026) | [arXiv v1](https://arxiv.org/abs/2609.07251) | PDF các đoạn §1–4, §7–8, bảng 6–7; proof chưa đọc đủ | gần: delay-to-memory là về phản hồi dự báo, không phải trực tiếp tuổi telemetry lúc chọn route |
| Hallberg Szabadváry, *ACI for Multi-Step Ahead Time-Series Forecasting Online* (2024) | [PMLR 230](https://proceedings.mlr.press/v230/hallberg-szabadvary24a.html) | PDF §3–5, Eq. 8–10, bảng 1–3 | gần: ACI riêng mỗi horizon; **không được claim** ACI theo horizon là mới |
| Lekeufack et al., *Conformal Decision Theory* (arXiv v3, 2024) | [arXiv](https://arxiv.org/abs/2310.05921) | PDF §III–IV, Theorem 1 và đầu §V | gần: calibrate risk của quyết định/fallback trực tuyến |
| Gibbs & Candès, *ACI Under Distribution Shift* (2021) | [arXiv](https://arxiv.org/abs/2106.00170) | PDF §2, §4.1, Proposition 4.1 | nền: baseline online không cần exchangeability cho tần suất dài hạn |
| Ornee & Sun, *Sampling and Remote Estimation for the OU Process through Queues* (2021) | [arXiv](https://arxiv.org/abs/1902.03552), [DOI](https://doi.org/10.1109/TNET.2021.3078137) | abstract; PDF đã tải nhưng chưa đọc sâu | nền: OU + tuổi ở mức sai số ước lượng và sampling |
| Maatouk et al., *The Age of Incorrect Information* (2020) | [arXiv](https://arxiv.org/abs/1907.06604), [DOI](https://doi.org/10.1109/TNET.2020.3005549) | metadata + PDF abstract | nền: AoII, không phải per-decision routing risk |
| Qi et al., *Update for Decisions, Not Freshness* (2026) | [arXiv](https://arxiv.org/abs/2609.01082) | metadata + abstract | gần: stale remote state, gate/route/reject cho edge offloading; không phải conformal |
| Tang et al., *Enhanced Route Planning with Calibrated Uncertainty Set* (2025) | [arXiv](https://arxiv.org/abs/2503.10088) | metadata + abstract | gần: conformal uncertainty set cho robust route planning; arXiv có cảnh báo text overlap với 2406.08281, cần xem bản gốc đó |
| Zhu et al., *Conformal Risk-Averse Decision Making with Action Conditional Guarantee* (2026) | [arXiv v2](https://arxiv.org/abs/2606.05551) | PDF §2, §4, Thm 2.1/4.3, Cor. 4.4 | gần: action-conditional guarantee dưới exchangeability; khác event ACCEPT |
| Guérin & Orda, *QoS routing in networks with inaccurate information* (1999) | [DOI](https://doi.org/10.1109/90.779203), [PDF lưu trữ](https://static.aminer.org/pdf/PDF/001/122/204/qos_routing_in_networks_with_inaccurate_information_theory_and_algorithms.pdf) | PDF §I–V, Proposition III.1; Appendix chưa đọc hết | gần: probabilistic route choice dưới link-state không chính xác |
| Wang et al., *LEC: Linear Expectation Constraints for Selection-Conditioned Risk Control* (2026) | [arXiv v3](https://arxiv.org/abs/2512.01556) | PDF §3, Thm 3.1–3.2, đầu §4 | gần/rất gần với **risk trên ACCEPT**; domain là model routing, không network path routing |
| Priye et al., *Available Guardrails* (2026) | [arXiv](https://arxiv.org/abs/2609.22048) | metadata + abstract | gần: finite-calibration feasibility của selective risk certification |

**Đính chính metadata:** bài Hallberg Szabadváry có **một tác giả**, tên đầy đủ Johan Hallberg Szabadváry; bài AoII 2020 là *The Age of Incorrect Information: A New Performance Metric for Status Updates* với **bốn** tác giả, khác bài *An Enabler of Semantics-Empowered Communication* (arXiv:2012.13214).

## Snowballing — vòng 0, start set bốn họ, 2026-09-23

Nguồn forward/backward của Guérin–Orda và Ornee–Sun là OpenAlex Works API; [582 bản ghi metadata và cờ sàng tiêu đề](snowball_openalex_2026-09-23.csv). “Khớp tiêu đề” là bộ lọc từ khóa, **chưa** phải sàng abstract. OpenTwin và El Halabi–Brandt không có references/citations được OpenAlex lập chỉ mục tại thời điểm tra; backward được trích trực tiếp từ PDF tác giả đăng và [52 mục đã xét](snowball_pdf_references_2026-09-23.csv). Số 0 forward ở đây chỉ có nghĩa là **0 bản ghi OpenAlex trả**, không chứng minh không ai trích dẫn.

| Họ / paper gốc | Hướng | Số mục truy xuất/xét | Qua lọc tiêu đề | Giữ đọc tiếp | Phát hiện đáng chú ý / giới hạn |
|---|---|---:|---:|---:|---|
| A / Guérin–Orda 1999 | backward | 31/31 metadata (32 ID tham chiếu) | 16 | 1 | PDF đã truy xuất; OpenAlex thiếu metadata của 1 ID. |
| A / Guérin–Orda 1999 | forward | 389/389 metadata OpenAlex | 34 | 6 | Cần sàng abstract/full text của 6 mục; không bảo đảm đầy đủ trích dẫn. |
| F / OpenTwin v2 | backward | 35/35 references PDF | 8 | 8 | Gồm runtime safety copilot [17], ACI [18–19], conformal risk control [20]; đây là chọn theo nhan đề, chưa đọc hết 8 bài. |
| F / OpenTwin v2 | forward | 0/0 OpenAlex indexed | 0 | 0 | Chỉ số còn trống cho preprint mới; cần kiểm lại Scholar/Semantic Scholar. |
| E / El Halabi–Brandt 2026 | backward | 17/17 references PDF | 11 | 11 | Gồm Szabadváry, Wang–Hyndman, Gibbs–Candès; danh sách đọc tiếp, không đồng nghĩa đã đọc full text. |
| E / El Halabi–Brandt 2026 | forward | 0/0 OpenAlex indexed | 0 | 0 | Preprint mới; cần kiểm lại ngoài OpenAlex. |
| D / Ornee–Sun 2021 | backward | 63/63 metadata (76 ID tham chiếu) | 15 | 3 | 13 ID không có metadata trả về. |
| D / Ornee–Sun 2021 | forward | 99/99 metadata OpenAlex | 15 | 4 | Có *From Freshness to Effectiveness*; cần sàng abstract/full text. |

**Lý do dừng vòng ghi nhận hôm nay:** đã hết lượt xử lý metadata/PDF của bốn start set trong ngày; 33 mục giữ đọc tiếp ở các nhánh trên còn backlog (có thể trùng nhau), hai nhánh forward không được lập chỉ mục, và Appendix Guérin–Orda chưa được kiểm hết. Đây là **tạm dừng ở vòng 0**, chưa đạt S1 bão hòa và chưa hết time-box 2026-09-30. Cần đọc abstract/full text của backlog, kiểm forward ở nguồn thứ hai, mở rộng IEEE/ACM bằng truy vấn tái lập, và đối chiếu CERT Appendix trước DP1. Không suy từ bảng này rằng đã chứng minh “chưa ai làm age + margin”.

## Tra cứu known-item + đọc full text, 2026-09-27 (L1.9 phần 1)

Công cụ: web search của trợ lý AI (Claude), 2026-09-27. Đây là tra cứu **known-item** (tìm đúng bài đã biết), không
phải truy vấn hệ thống; không dùng để ước độ phủ.

| Truy vấn | Kết quả | Ghi chú |
|---|---|---|
| `arXiv 2511.10146` | không trúng | công cụ không khớp theo số hiệu |
| `Burbano latency prediction adaptive confidence hysteresis handover edge server passive measurements arXiv 2025` | trúng arXiv:2511.10146 | đọc full text PDF |
| `Liyanage 2026 arXiv 2604.21483 edge server selection latency prediction` | trúng arXiv:2604.21483 | đọc full text HTML |
| `Almohammedi 2026 arXiv 2607.22857 digital twin` | trúng arXiv:2607.22857 | đọc full text HTML |
| `Fischer Vöcking "Adaptive routing with stale information" Theoretical Computer Science` | trúng TR AIB-2005-06 (PDF) + trích dẫn TCS 2009 | đọc bản TR |

Đưa vào backlog (chỉ thấy trong kết quả, **chưa đọc**):
- *The Value of Information in Selfish Routing* (arXiv:2005.05191) — trích Fischer–Vöcking, Dahlin, Mitzenmacher; có thể
  liên quan tới phân rã "giá trị thông tin".
- *Incentivizing Stable Path Selection in Future Internet Architectures* (ACM SIGMETRICS PER, doi:10.1145/3453953.3453956)
  — trích Fischer–Vöcking; path-aware networks, dao động.
- Liyanage et al. 2025, *Lightweight Latency Prediction Scheme for Edge Applications* (arXiv:2511.02501) — bộ dự đoán
  dùng trong Burbano/Liyanage; không cần cho RQ1.

## Tra cứu + đọc full text, 2026-09-27 (L1.9 phần 2)

Công cụ: web search của trợ lý AI (Claude). Known-item lookup, không ước độ phủ.

| Truy vấn | Kết quả | Ghi chú |
|---|---|---|
| `Seshadri Katz 2003 dynamics of simultaneous overlay network routing` | trúng TR UCB/CSD-03-1291 | đọc full text PDF |
| `Mitzenmacher "How useful is old information" IEEE Transactions on Parallel and Distributed Systems 2000 pdf` | không có link PDF trực tiếp | hoãn (nhóm "nếu kịp") |

Backlog mới (chỉ thấy trong kết quả, chưa đọc, **chưa xác nhận tiêu đề**): bài IEEE Xplore 1544621 về đồng bộ hoá và
dao động giữa các overlay cùng tồn tại (mô hình giải tích xác suất đồng bộ hai overlay).

Forward citation qua OpenAlex chạy trên máy tác giả: Fischer–Vöcking resolve bằng DOI thành `W1996350158`, có 29 bài
trích dẫn và 6 bài qua lọc từ khoá tiêu đề. Seshadri–Katz không resolve được vì endpoint tìm theo tiêu đề trả HTTP 503;
ghi là **chưa lập chỉ mục/chưa truy xuất được**, không suy ra 0 trích dẫn. Cả 5 truy vấn có mục tiêu cũng trả HTTP 503;
các URL lỗi được lưu nguyên văn trong `openalex_l19_2026-09-27_output.txt` và phải chạy lại. CSV hiện là kết quả một
phần gồm 29 forward citation Fischer–Vöcking; `title_filter_match` chưa phải sàng abstract.

## L1.10 (P1v2) — literature cho khung mới, 2026-09-30

Công cụ: web search/fetch của trợ lý AI (Claude). Mỗi truy vấn trả ~8–10 kết quả, KHÔNG trả tổng ⇒ cột tổng ghi `—`
(không đo được, không phải 0). Tìm có mục tiêu + known-item, không dùng để ước độ phủ. Sandbox chặn api.openalex.org,
api.semanticscholar.org, export.arxiv.org (HTTP 403 host_not_allowed) ⇒ không chạy lại được `openalex_l19.py`.

### Forward citation (việc 1)
| Bài gốc | Nguồn | Kết quả | Sàng 2026-09-30 | Ghi chú |
|---|---|---|---|---|
| Fischer–Vöcking | OpenAlex (máy tác giả, 27/09) | 29; 6 qua lọc tiêu đề | Tiêu đề 29/29: không bài nào ở chế độ một luồng nhỏ, tải ngoại sinh. Giữ mức abstract: Scherrer et al. SIROCCO 2020 (VoI trong selfish routing). Chỉ tiêu đề: Scherrer et al. PEVA 2020 (stable path selection); PEVA 2021 (axiomatic, end-host path selection) | Họ tập thể / Wardrop |
| Seshadri–Katz | OpenAlex | không lập chỉ mục (27/09) | — | Còn được liệt kê là paper WIRED (trang nhóm SAHARA). Không truy xuất được "cited by" ⇒ CHƯA hoàn tất; KHÔNG suy ra 0 trích dẫn. Cùng họ: Keralapura et al. ToN 2008 (bản ICNP 2005) — CHƯA xác nhận có trích S–K. Backlog "IEEE 1544621" khớp mô tả bài Keralapura [I], chưa đối chiếu số hiệu |

### Truy vấn có mục tiêu (việc 2)
| # | Truy vấn nguyên văn | Trả về / tổng | Giữ | Mức kiểm |
|---|---|---|---|---|
| L1 | `"flat maximum" von Winterfeldt Edwards decision analysis origin 1973 OR 1982 "flat maxima"` | 9 / — | von Winterfeldt & Edwards 1973 (TR 011313-4-T, U. Michigan); sách 1986 | thư mục |
| L2 | `Radner Stiglitz 1984 "nonconcavity in the value of information" marginal value zero Chade Schlee 2002` | 10 / — | Radner–Stiglitz 1984; Chade–Schlee 2002 | thư mục + abstract |
| L3 | `Houtekamer 1993 "Global and local skill forecasts" spread skill correlation variability of spread lognormal Whitaker Loughe 1998` | 9 / — | Jewson 2003; Houtekamer 1993; Whitaker–Loughe 1998 | Jewson FULL TEXT; hai bài kia abstract/thứ cấp |
| L4 | `Birge 1982 "value of the stochastic solution" Mathematical Programming EVPI wait-and-see recourse EEV definition` | 10 / — | Birge 1982 | định nghĩa qua ≥ 3 nguồn thứ cấp |
| L5 | `Audibert Tsybakov 2007 "Fast learning rates for plug-in classifiers" margin condition excess risk density near decision boundary` | 9 / — | Audibert–Tsybakov 2007 | abstract |
| L6 | `arXiv 2604.25967 digital twin belief state reinforcement learning latency-robust ISAC 6G delayed telemetry EKF` | 9 / — | Tiwari, Kar, Tiwari 2026 | FULL TEXT (họ 1) |
| L7 | `"From Freshness to Effectiveness" age-aware remote decision making Li Wu Lee Sun arXiv 2504.19507` | 9 / — | Li et al. 2026 v3 | FULL TEXT §I–VII (họ 2) |
| L8 | `"The Value of Information in Selfish Routing" Scherrer Perrig Schmid SIROCCO 2020` | 10 / — | Scherrer et al. 2020 | abstract |
| L9 | `Keralapura Chuah "coexisting overlay networks" race conditions oscillations route selection` | 9 / — | Keralapura et al. 2008 | abstract/đoạn trích |
| L10 | `Linux MPTCP sysctl stale_loss_cnt "stale" subflow packet scheduler ignores stale subflows` | 9 / — | tài liệu kernel Linux | tài liệu gốc — ĐÍNH CHÍNH L1.8 |
| L11 | `"Dynamics of simultaneous overlay network routing" Seshadri Katz` | 9 / — | trang TR + trang nhóm | thư mục |

### Backlog có thứ tự (CHƯA chạy; [?] = nhớ từ kiến thức nền, chưa kiểm)
1. Họ handover: luật tối ưu vs hysteresis dưới đo nhiễu — [?] Veeravalli & Kelly 1997; Zhang & Holtzman 1996
   (ngưỡng tuyệt đối + tương đối, gần K22); Vijayan & Holtzman 1993. ƯU TIÊN CAO NHẤT: có thể lật DP1.
2. SD-WAN application-aware routing: chu kỳ poll/probe mặc định của nhà cung cấp [?].
3. Một full text họ multipath/SD-WAN có path phụ đo thưa — việc 3, bài thứ ba, CHƯA ĐẠT.
4. Cost–loss: giá trị dự báo xác suất vs tất định [?] (Murphy 1977; Richardson 2000).
5. Kiểm DOI: Karlin & Rubin 1956; Blackwell 1951, 1953 [?].

### Lượt 2 — cùng ngày 2026-09-30 (sau khi hết lượt công cụ ở lượt 1)

| # | Truy vấn / thao tác nguyên văn | Trả về / tổng | Giữ | Mức kiểm |
|---|---|---|---|---|
| L12 | `Veeravalli Kelly "locally optimal handoff algorithm" cellular communications IEEE Transactions on Vehicular Technology 1997 hysteresis` | 9 / — | Veeravalli–Kelly 1997; Prakash–Veeravalli 2003 | thư mục + tóm tắt |
| L13 | `Veeravalli Kelly locally optimal handoff algorithm pdf dynamic programming signal strength prediction hysteresis comparison tradeoff number of handoffs` | 10 / — | PDF trên trang tác giả; Prakash–Veeravalli 2000 (PDF) | V–K: FULL TEXT |
| L14 | `Cisco SD-WAN application-aware routing "poll-interval" default 600000 "app-route multiplier" SLA BFD probes` | 10 / — | Cisco Policies Config Guide vEdge 20.x, chương AAR | FULL TEXT chương |
| L15 | `SD-WAN path selection active probing frequency measurement staleness tunnel switching hysteresis flapping research paper arXiv` | 9 / — | KHÔNG có bài nghiên cứu về path phụ đo thưa (survey, bằng sáng chế, bài ước lượng băng thông) | sàng snippet |
| L16 | `Richardson 2000 "relative economic value" cost-loss ratio ensemble prediction system perfect forecast climatology deterministic control forecast Quarterly Journal` | 10 / — | Richardson 2000; định nghĩa REV qua ≥ 3 nguồn thứ cấp | abstract |
| F1 | fetch Houtekamer 1993 (journals.ametsoc.org) | lỗi | — | AMS chặn truy cập tự động |
| F2 | fetch Hopson 2014 (opensky.ucar.edu) | lỗi | — | robots không cho phép |

Đính chính thư mục: vài nguồn thứ cấp ghi V–K 1997 trang 351–356; header PDF gốc ghi 46(3):603–609. 351–356 là trang
của Vijayan & Holtzman 1993 (TVT 42(3)) — lỗi lan qua trích dẫn thứ cấp. Zhang & Holtzman: bản V–K trích là VTC 1994,
pp. 82–86 (ref [9]); bản tạp chí 1996 [?].

### Backlog (thay backlog của lượt 1)
1. ✓ Họ handover — V–K 1997 full text. Còn: Prakash–Veeravalli 2000 "Adaptive hard handoff algorithms" (PDF trên trang
   tác giả; đọc nếu Phase 2 mở lại RQ2/H3 cũ); Rezaiifar–Makowski–Kumar 1995 (JSAC 13(7):1348–1362) — chưa đọc.
2. ✓ SD-WAN — tài liệu gốc Cisco. CHƯA có bài nghiên cứu họ multipath/SD-WAN có path phụ đo thưa (L15).
3. Seshadri–Katz forward citation — CHƯA; cần Google Scholar "Cited by" bằng trình duyệt.
4. Houtekamer 1993 / Whitaker–Loughe 1998 / Hopson 2014 — tải tay (AMS, UCAR chặn công cụ).
5. Richardson 2000 full text — dự báo tất định có được tune ngưỡng không? [?]
6. Karlin–Rubin 1956; Blackwell 1951/1953 — kiểm DOI [?].
