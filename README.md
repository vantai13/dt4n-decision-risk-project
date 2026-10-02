# dt4n-decision-risk-project

Mã nguồn nghiên cứu quyết định **đổi hay giữ đường truyền** của Network Digital
Twin khi telemetry đã cũ, có nhiễu đếm và có thể bị gián đoạn. Repo gồm mô hình
hàng đợi, mô phỏng mức gói, twin, các luật quyết định, kiểm thử và hồ sơ kết quả.

Cập nhật ngày **02/10/2026** trên nhánh **`rollout-v6`**. Nền kết quả hiện có:
`e32a8c1` (GO-check), `8f0c899` (rollout v5), `8876e12` (chuẩn bị v6).

**Trạng thái nghiên cứu: CHƯA GO.** GO-check đã tái lập; pipeline rollout v6
với tham số twin tự ước lượng vẫn là bản dự thảo, chưa chạy DES trên seed dành
riêng. Repo là một nghiên cứu khả thi đang phát triển, có thể dùng làm nền
tham khảo cho hướng paper sandbox; chưa phải bộ đánh giá sandbox hoàn chỉnh.

## 1. Bài toán và phạm vi

Một luồng nhỏ đang đi trên đường A. Tại mỗi epoch, bộ điều khiển dùng telemetry
để chọn giữ A hoặc chuyển sang B. Twin dự báo delay trên khoảng giữ và tính:

- `Ī`: lợi ích kỳ vọng khi rời đường hiện tại, đơn vị ms.
- `p−`: xác suất đổi sang đường có delay tệ hơn quá `ε`.
- `I = D_current − D_alternative`: lợi ích thật; dương nghĩa là đổi tốt hơn.

Mục tiêu một bước là tối đa hóa lợi ích kỳ vọng dưới ngân sách đổi gây hại.
Hai luật cơ bản là SC (đổi nếu `Ī > h`) và K2
(đổi nếu `Ī − λ·p− > 0`, tương đương ngưỡng trên `Ī/p−` khi `Ī > 0`).
Một số phiên bản rollout bổ sung ngưỡng lợi ích và baseline mạnh hơn; cần đọc
đúng protocol của từng phiên bản.

Tải nền được sinh theo OU, gói đến theo Poisson và hàng đợi dùng M/D/1/K.
Luồng được điều khiển và probe không làm thay đổi tải nền. Vì vậy cả
`D_A` và `D_B` đều có sẵn để chấm các luật trên cùng thế giới, nhưng repo
chưa đo tác động ngược của chuyển một lượng lưu lượng lớn.

Telemetry chính là **số gói đếm trong cửa sổ**, có trễ và tuổi dữ liệu; không
phải phép đo RTT/delay trực tiếp của SD-WAN. Các tham số kịch bản vẫn cần
nguồn thực tế trước khi kết luận về triển khai.

Hai cách đánh giá cần phân biệt:

| Cách đánh giá | Đại lượng được đo | Nơi sử dụng |
|---|---|---|
| Decision-level | Lợi của một đề nghị đổi trên quỹ đạo tham chiếu | Scan, frontier, GO v0, GO switch v1 |
| Rollout | Delay luồng thực sự chịu khi mỗi luật tự đi quỹ đạo riêng | Rollout v2–v5, GO-check; v6 đang chuẩn bị |

Trần **số lần đổi trung bình** của GO switch v1 cũng khác **cooldown/hold-down**
giữa hai lần đổi thật trong rollout. Không so trực tiếp các con số giữa
hai estimand hoặc hai kiểu ràng buộc này.

## 2. Thành phần đã có

| Thành phần | Mã nguồn | Trạng thái |
|---|---|---|
| Nghiệm dừng M/D/1/K | [mdk.py](ndtrisk/theory/mdk.py) | Có kiểm nghiệm lý thuyết và mô phỏng |
| Workload hàng đợi mức gói | [f04b_des_gap.py](experiments/f04b_des_gap.py), [des_world.py](experiments/scan/des_world.py) | Sinh delay thật và telemetry từ cùng gói đến |
| Tải OU và quan sát | [world.py](experiments/scan/world.py) | Tuổi, cửa sổ đo, nhiễu đếm |
| Twin posterior và đường cong delay | [twin.py](experiments/scan/twin.py), [go_test.py](experiments/scan/go_test.py) | Tính `Ī`, `p−`; nhiều thí nghiệm vẫn dùng tham số tải thật |
| Luật rollout và outage collector | [rollout_v2.py](experiments/scan/rollout_v2.py) đến [rollout_v5.py](experiments/scan/rollout_v5.py) | Ngưỡng thô, theo chiều, theo tuổi, bảng 8/24 ô và K2 |
| Ước lượng tham số từ telemetry | [telemetry_fit.py](experiments/scan/telemetry_fit.py), [rollout_v6.py](experiments/scan/rollout_v6.py) | Đã kiểm tổng hợp; DES v6 chưa chạy |
| GO-check bố trí thông tin | [experiments/gocheck/](experiments/gocheck/) | V1–V6 đạt; rollout và FIX/SYM/FF đã tái lập |
| Dữ liệu testbed cũ | [data/mininet_calibration/](data/mininet_calibration/) | Có provenance và checksum, giữ read-only |
| Validation Mininet mới | [emulation/](emulation/) | Chưa triển khai |

Trong nghiệm M/D/1/K, `K` gồm cả gói đang phục vụ; `S` là thời gian phục vụ
một gói. Ở `K=11, ρ=0,8`, loss ≈ **0,2353%**, **thời gian chờ ≈ 1,878 S**,
còn sojourn (chờ + phục vụ) ≈ **2,878 S**.

Testbed nhập từ dự án cũ dùng HTB token bucket và `bfifo`, khác server có
service time cố định. [Pilot P05](experiments/pilot/results/p05_token_bucket_testbed_output.txt)
ghi sai số OWD trung bình khoảng 3,3% cho mô hình token bucket và 57,0% cho
M/D/1/K trong phép so đó; đây là kết quả pilot, chưa xác nhận toàn bộ controller
trên Mininet. Ý nghĩa dữ liệu ở [PROVENANCE.md](data/mininet_calibration/PROVENANCE.md).

## 3. Bản đồ repo

| Đường dẫn | Nội dung |
|---|---|
| [ndtrisk/](ndtrisk/) | Package lõi, hiện có bộ giải hàng đợi |
| [experiments/](experiments/) | Kiểm lý thuyết `t*`, nghiên cứu khả thi `f*`, runner và báo cáo |
| [experiments/pilot/](experiments/pilot/) | Thử nghiệm trước khung hiện tại; không dùng thay bằng chứng xác nhận |
| [experiments/scan/](experiments/scan/) | Map, confirm, frontier, GO và rollout v2–v6 |
| [experiments/gocheck/](experiments/gocheck/) | Rollout SC/K2, FIX/SYM/FF, validity, hậu kiểm và exporter |
| [experiments/results/](experiments/results/) | Output và hình của các thí nghiệm lý thuyết/F1–F8 |
| [results/scan/](results/scan/) | Artefact của quét, confirm và frontier |
| [results/explore_width/](results/explore_width/) | Sensitivity, phân rã cơ chế và khám phá độ rộng |
| [results/go_test/](results/go_test/) | Kết quả GO v0, GO switch và rollout v2–v5 |
| [results/gocheck/](results/gocheck/) | Output tái lập, CSV theo seed, summary, CI và manifest GO-check |
| [notes/](notes/) | Brief, định nghĩa, protocol, nhật ký, lý thuyết và literature |
| [data/](data/) | Dữ liệu tham khảo/testbed có hồ sơ nguồn gốc |
| [tests/](tests/) | Kiểm solver, pipeline, đơn vị, seed và giới hạn thông tin |
| [reference/](reference/) | Snapshot dt4n và code hướng trust-gate cũ |
| [emulation/](emulation/) | Chỗ dành cho validation Mininet |

Hướng trust-gate/top-2 margin cũ được giữ trong
[notes/archive/v1_trust_gate/](notes/archive/v1_trust_gate/) và
[reference/v1_trust_gate/](reference/v1_trust_gate/). Nó không phải protocol
đổi/giữ đang được đánh giá.

## 4. Các giai đoạn nghiên cứu

| Giai đoạn | Câu hỏi / việc đã làm | Hồ sơ |
|---|---|---|
| Phase 0, 23–26/09 | Định nghĩa bài toán, mục tiêu và cơ chế testbed | [Brief](notes/00_research_brief.md), [decision log](notes/02_decision_log.md) |
| F1–F6, 26–30/09 | Khoảng cách ngưỡng tĩnh–oracle và SESOI ở các cấu hình 4 Mb/s | [F6 closeout](notes/feasibility/F6_DP0_DP1.md) |
| F7–F8, 30/09 | Bất đối xứng rủi ro, twin có lịch sử; F8 có ô hỏng cổng oracle | [F7](notes/feasibility/F7_asym_freshness.md), [F8](notes/feasibility/F8_history_twin.md) |
| Map → confirm → frontier → explore | Tìm vùng hiệu ứng, sensitivity và cơ chế; có lựa chọn hậu kiểm | [Frontier](notes/map/frontier_report.md), [explore](notes/map/explore_width_report.md) |
| GO v0 → GO switch v1, 01/10 | Kịch bản R1/R2, harm budget, trần đổi và chi phí đổi | [GO v0](notes/map/go_report.md), [GO switch](notes/map/go_switch_report.md) |
| Rollout v2–v5, 01/10 | Mỗi luật tự đi quỹ đạo, hold-down, horizon twin và baseline mạnh | [v2–v4](results/go_test/rollout_reproduction_report.md), [v5](results/go_test/rollout_v5_report.md) |
| Rollout v6 | Twin học tham số từ telemetry calibration, 60 seed test | [Chuẩn bị v6](notes/map/rollout_v6_preparation.md); chưa chạy |
| GO-check | Tái lập rollout, so FIX/SYM/FF, kiểm nguồn sai tại lúc đổi | [Báo cáo tái lập](results/gocheck/REPRODUCTION_REPORT.md) |

Các nhãn “GO” trong gate v0/v1 chỉ là kết quả theo cổng mô phỏng của giai đoạn
đó. Chúng không thay phán quyết **CHƯA GO** theo đủ ba tiêu chí ứng dụng hiện tại.

## 5. Kết quả hiện có

### GO-check: delay luồng trên quỹ đạo riêng

Ở `α=0,2%, ε=1 ms`, không cooldown; CI95% t ghép cặp theo 20 seed test.
Giá trị `SC−K2 > 0` nghĩa là K2 tốt hơn.

| Lần chạy | Bố trí | Delay SC (ms) | Delay K2 (ms) | SC−K2 [CI95%] (ms) |
|---|---|---:|---:|---|
| 92/93 | FIX | 5,675 | 4,168 | +1,506 [1,229; 1,784] |
| 94/95 | FIX | 5,770 | 4,024 | +1,746 [1,427; 2,066] |
| 94/95 | SYM | 2,785 | 2,632 | +0,153 [0,139; 0,167] |
| 94/95 | FF | 3,289 | 3,483 | −0,193 [−0,291; −0,095] |

FIX luôn đo A mỗi 1 s và B mỗi 60 s. SYM đo cả hai mỗi 1 s.
FF dùng luồng đo 1 s cho path đang mang luồng và 60 s cho path còn lại.

FF hiện bỏ số đo tươi của path vừa rời. Vì vậy kết quả FF chỉ áp dụng cho
thiết kế không nhớ telemetry này, chưa kết luận được về đo thụ động thực tế.
Hai hậu kiểm phát hiện sai lệch lớn tại lúc đổi, nhưng chưa trực tiếp kiểm
quan hệ nhân quả bằng một phiên bản FF có trí nhớ.

Cooldown 30 s làm lợi thế FIX còn **0,681 ms** ở 92/93 và **0,641 ms** ở
94/95. SYM cooldown có CI chứa 0. Ở 92/93, harm SC/K2 là
**0,1842% / 0,2133%**: trượt điều kiện chênh harm `≤0,1α` của TC1,
dù CI delay dương; lần FIX 94/95 đạt điều kiện TC1 này.

So sánh khám phá trên cùng thế giới 94/95: làm telemetry B tươi hơn giúp
SC giảm **2,986 [2,496; 3,475] ms**. K2 ở FIX vẫn chậm hơn SC ở SYM
**1,239 [0,910; 1,569] ms**. Trong R1 này, nâng độ tươi có lợi hơn đổi luật;
chưa khái quát thành quy luật cho mọi mạng.

[Báo cáo GO-check](results/gocheck/REPRODUCTION_REPORT.md) có đối chiếu
dự đoán–kết quả, cả 16 cấu hình và giới hạn. Dữ liệu kiểm toán gồm
[1.280 dòng theo seed](results/gocheck/reproduction_seeds.csv),
[summary và ngưỡng tune](results/gocheck/reproduction_summary.csv),
[contrasts/CI](results/gocheck/reproduction_contrasts.csv),
[manifest](results/gocheck/reproduction_manifest.json) và
[kiểm khớp sandbox](results/gocheck/reproduction_checks_output.txt).

### Baseline mạnh và độ tin của twin ở rollout v5

Trong R3_outage, hold-down và horizon twin đều 30 s:

- K2 đạt delay test 3,877 ms; SC 4,490 ms; SClin 4,329 ms; SCtab24 3,960 ms.
- SClin−K2 = **0,451 [0,088; 0,815] ms**.
- SCtab24−K2 = **0,082 [−0,113; 0,278] ms**: chưa phân giải lợi thế,
  cũng chưa chứng minh tương đương.
- Ngân sách `α=0,2%` và `α=∞` cho cùng chính sách ở cả 8 họ trong ô/lưới
  này; không suy harm budget luôn không có tác dụng ở mọi kịch bản.
- Trong một bin rủi ro thấp, `p−` dự báo trung bình 0,447% nhưng harm trên
  cửa sổ thật khoảng 1,423%. Rủi ro twin chưa được hiệu chỉnh xác suất.

Chi tiết và điều kiện tính nhãn ở [báo cáo v5](results/go_test/rollout_v5_report.md).
Cửa sổ harm v5 ngắn dần ở 29 epoch cuối; pipeline v6 đã chuẩn bị padding để
giữ cửa sổ đủ 30 s, nhưng chưa có outcome v6.

### Ba tiêu chí GO

| Tiêu chí | Trạng thái |
|---|---|
| TC1: lợi thế delay trong điều kiện harm đã định | Có điều kiện; phụ thuộc lần lặp, bố trí và baseline |
| TC2: kịch bản/telemetry có cơ sở thực tế | Chưa đạt; thiếu nguồn cho các giả định chủ chốt |
| TC3: magnitude VoIP | Chưa đạt sàn tuyệt đối 8,1 ms |

SESOI giữ cả **8,1 ms** và **10% headroom** theo L1.5. Trong GO-check,
`headroom = delay(SC) − delay(oracle nhìn trước)`; oracle nhìn trước là cận
tham chiếu không triển khai được. Không đổi metric sau khi thấy kết quả.
[Hồ sơ GVHD](notes/gocheck/GVHD_status.md) tổng hợp bằng chứng và câu hỏi DP0.

## 6. Cài đặt và kiểm thử

Chạy từ gốc repo, sau khi checkout nhánh có rollout và GO-check:

```bash
git clone --branch rollout-v6 https://github.com/vantai13/dt4n-decision-risk-project.git
cd dt4n-decision-risk-project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install -e ".[dev]" --no-deps
python -m pytest -q
```

Môi trường đã kiểm: Python **3.14.5**, NumPy **2.5.3**, SciPy **1.18.1**,
Numba **0.67.0**, llvmlite **0.49.0**; bộ test hiện có **138 test đạt**.
[Lockfile](requirements-lock.txt) đã có Numba và llvmlite để tái lập engine
tăng tốc. `pyproject.toml` khai báo Python ≥3.10 cho package, nhưng không có
nghĩa mọi bản Python đó đã được kiểm với lockfile hiện tại.

## 7. Chạy lại các phép đo

Các lệnh dưới đây chạy từ gốc repo, trong môi trường đã cài.

**Validity trên seed cũ**, gồm kiểm thế giới, rollout và nối telemetry:

```bash
python -m experiments.gocheck.info_arrangement --mode validity
python -m experiments.gocheck.check_wiring
```

**Tái lập GO-check trên các dải đã xem**:

```bash
mkdir -p results/gocheck
set -eo pipefail
python -m experiments.gocheck.check_wiring
python -m experiments.gocheck.rollout --seeds fresh | tee results/gocheck/fresh_output.txt
python -m experiments.gocheck.info_arrangement --mode outcome --cal 94001 --test 95001 | tee results/gocheck/info_outcome_output.txt
python -m experiments.gocheck.posthoc_reliability | tee results/gocheck/posthoc_reliability_output.txt
python -m experiments.gocheck.posthoc_switch_errors | tee results/gocheck/posthoc_switch_errors_output.txt
python -m experiments.gocheck.verify_supplied_results
python -m experiments.gocheck.report_reproduction
```

`fresh` là tên tùy chọn lịch sử; **92/93 và 94/95 không còn là seed chưa xem**.
Hai script `posthoc_*` là khám phá. Exporter chỉ đọc cache, không sinh thêm
thế giới; cần chạy hai runner trước nếu máy chưa có cache. Lần đo local ghi
63 s cho rollout và 147 s cho info outcome; thời gian thay đổi theo máy/cache.

Cache `results/gocheck/raw/` bị gitignore; output văn bản, CSV, báo cáo và
manifest được lưu trong Git. Xem [sổ seed](notes/seed_registry.md) trước mọi
phép xác nhận mới.

**Rollout v6 chưa được phép chạy outcome ở trạng thái hiện tại**:
[protocol](notes/map/rollout_v6_protocol.json) còn draft,
`author_prediction=null`; chưa có tag khóa `prereg-rollout-v6`.
Dải calibration **90001–90020**, test **91001–91060** vẫn để dành.
Có thể đọc hash code mà không mở seed:

```bash
python -m experiments.scan.rollout_v6 --print-lock-hashes
```

Kiểm nền tảng dùng [tests/](tests/). Các kiểm và output lịch sử nằm trong
[experiment log](notes/03_experiment_log.md); không cần chạy lại toàn bộ sweep
để đọc các kết quả đã lưu.

## 8. Nguồn gốc và cách sử dụng bằng chứng

Một phần lớn tài liệu, code thí nghiệm và diễn giải được soạn với hỗ trợ AI.
Provenance trong từng protocol/báo cáo cho biết đâu là dự đoán, tái lập,
khám phá và xác nhận theo thiết kế của giai đoạn đó. Test xanh kiểm triển khai,
không tự chứng minh kịch bản thực tế hoặc tính mới nghiên cứu.

GO-check local là **tái lập kết quả sandbox đã được cung cấp trước lần chạy**.
Dự đoán thuộc Claude AI, được giữ ở [PREDICTIONS_claude.md](notes/gocheck/PREDICTIONS_claude.md),
có ghi lệch NT-1; không phải dự đoán tác giả. Commit sandbox `1a66a24` chưa
kiểm được tại repo local. Cấu hình local khóa ở `9272119`, kết quả lưu ở
`e32a8c1`. Nhiều phân tích ngày 01/10 dùng lại seed hoặc chọn hướng sau khi
xem kết quả; CI của những phân tích đó mang tính khám phá.

Các file trong [notes/meetings/](notes/meetings/) gồm biên bản mô phỏng, memo
chuẩn bị và ghi chép tự khai nguồn gốc. Không dùng một memo AI hoặc đề xuất DP0
như bằng chứng GVHD đã duyệt; khi trích quyết định thật cần kiểm nguồn xác nhận
của tác giả/GVHD. README không xác nhận độc lập các phát biểu học vụ lịch sử.

Dữ liệu testbed giữ nguyên và có checksum. Tài liệu thiết kế cũ giữ để truy
lịch sử; một tính năng nằm trong kế hoạch không đồng nghĩa đã có code/kết quả.

## 9. Tái sử dụng cho hướng paper sandbox

Repo có thể cung cấp lõi hàng đợi, tải OU, telemetry/outage, twin và đánh giá
ghép cặp cho một sandbox thử thay đổi mạng. Theo góc nhìn đó, bằng chứng hiện
có chủ yếu cho biết độ nhạy với thông tin, horizon dự báo và mô hình hàng đợi;
chưa có đánh giá đầy đủ cho các câu hỏi sau:

| Phần còn thiếu | Hiện trạng |
|---|---|
| Chấm trực tiếp duyệt nhầm / từ chối nhầm thay đổi | Chưa có benchmark sandbox hoàn chỉnh |
| Sandbox lý tưởng biết trạng thái thật và mô hình đúng | Các oracle hiện có phục vụ từng estimand, chưa thay được đối chứng này |
| Chuyển lưu lượng đủ lớn để đổi tải mạng | Chưa làm; tải nền đang ngoại sinh |
| Twin sai họ mô hình có hệ thống, traffic burst/token bucket | Có pilot và kế hoạch, chưa có đánh giá tích hợp đầy đủ |
| Bật lần lượt từng nguồn sai để phân rã | Chưa có protocol/thí nghiệm hoàn chỉnh |
| Tham số đo từ triển khai và holdout chưa dùng | Chưa đủ cho xác nhận thực tế |
| FF nhớ telemetry của path vừa rời | Chưa triển khai; cần thiết kế và seed mới nếu tiếp tục |

Không suy từ kết quả switch-or-stay hiện tại rằng một paper sandbox đã đạt GO.
Các hướng NARROW/PIVOT và việc đổi metric/ứng dụng còn cần quyết định nghiên cứu.

## 10. Tài liệu nên đọc

1. [Brief hiện có](notes/00_research_brief.md) và [định nghĩa](notes/06_definitions.md).
2. [Báo cáo GO-check](results/gocheck/REPRODUCTION_REPORT.md) và
   [rollout v5](results/go_test/rollout_v5_report.md).
3. [Protocol đánh giá](notes/05_evaluation_protocol.md), [sổ seed](notes/seed_registry.md),
   [decision log](notes/02_decision_log.md), [experiment log](notes/03_experiment_log.md).
4. [Lý thuyết](notes/theory/) và [literature](notes/01_literature/).
5. [Dữ liệu testbed](data/mininet_calibration/PROVENANCE.md) và
   [chuẩn bị rollout v6](notes/map/rollout_v6_preparation.md).
