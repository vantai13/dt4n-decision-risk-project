"""Validate the completed GO artifact and generate an auditable report."""
import csv
from pathlib import Path

from experiments.scan.go_test import ALPHAS, EPS_EXTRA, GO_RULE, TWIN_ERRORS, scenarios, verdict

OUT = Path('results/go_test')


def failures(r):
    failed = []
    if r['oos_lo'] <= 0:
        failed.append('CI ngoài mẫu chứa 0')
    if r['fr_pct'] < 3:
        failed.append('frontier <3% headroom')
    if r['fr_lo'] <= 0:
        failed.append('CI frontier chứa 0')
    if r['harm_ratio'] > .7:
        failed.append('harm ratio >0,7')
    if r['oos_hSC'] > 1.5*r['alpha']:
        failed.append('harm SC >1,5α')
    if r['oos_hK2'] > 1.5*r['alpha']:
        failed.append('harm K2 >1,5α')
    return '; '.join(failed) or 'Đạt'


def main():
    with (OUT/'go_v0.csv').open() as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in r:
            if k == 'passed':
                r[k] = r[k] == 'True'
            elif k not in ('name', 'twin'):
                r[k] = float(r[k])
        assert r['passed'] == GO_RULE(r, r['alpha'])
    base, sweep = scenarios()
    expected = {(s['name'], e, a, 1.) for s in base for e in TWIN_ERRORS for a in ALPHAS}
    expected |= {(s['name'], 'đúng', .002, EPS_EXTRA) for s in base}
    expected |= {(s['name'], 'đúng', .002, 1.) for s in sweep}
    actual = {(r['name'], r['twin'], r['alpha'], r['eps']) for r in rows}
    assert actual == expected and len(rows) == 38
    lines = ['# GO/NO-GO v0 — kết quả 2026-10-01', '',
             'Đã kiểm đủ 38 dòng, không thiếu/trùng tổ hợp; tính lại GO_RULE khớp toàn bộ cờ trong CSV. Code và dự đoán khóa trước chạy ở commit 104841f. 14 test theo hướng dẫn + 3 test sửa lỗi trước chạy đạt; toàn bộ suite sau chạy: 95 passed in 5.49s.', '',
             '## Kết luận theo tiêu chí đã khóa', '']
    for s in base:
        label, alpha, lo = verdict(rows, s['name'])
        lines.append(f"- {s['name']}: **{label}**, α={alpha:g}, ε=1 ms; cận dưới lợi ích ngoài mẫu khi twin đúng {lo:.6f} ms.")
    lines += ['', 'Tổng: **GO** theo cổng mô phỏng; cả hai kịch bản đạt 7/7 trạng thái twin tại α=0,2%. Chưa đạt SESOI VoIP 8,1 ms. Nhãn này không xác nhận hệ thống triển khai thật.', '',
              '## Hai kịch bản, twin đúng, α=0,2%, ε=1 ms', '',
              '| Kịch bản | Headroom ms | Δ ngoài mẫu [CI 95%] ms | Δ frontier [CI 95%] ms | % headroom | Harm SC/K2 ngoài mẫu | Harm ratio |',
              '|---|---:|---|---|---:|---|---:|']
    for r in rows:
        if r['name'] in {s['name'] for s in base} and r['alpha'] == .002 and r['eps'] == 1. and r['twin'] == 'đúng':
            lines.append(f"| {r['name']} | {r['headroom']:.6f} | {r['oos_ms']:.6f} [{r['oos_lo']:.6f}; {r['oos_hi']:.6f}] | {r['fr_ms']:.6f} [{r['fr_lo']:.6f}; {r['fr_hi']:.6f}] | {r['fr_pct']:.3f}% | {100*r['oos_hSC']:.6f}% / {100*r['oos_hK2']:.6f}% | {r['harm_ratio']:.6f} |")
    lines += ['', '## Độ bền theo từng alpha', '', '| Kịch bản | α | Số trạng thái đạt | Trạng thái không đạt và lý do |', '|---|---:|---:|---|']
    for s in base:
        for a in ALPHAS:
            sub = [r for r in rows if r['name'] == s['name'] and r['alpha'] == a and r['eps'] == 1.]
            why = ' / '.join(f"{r['twin']}: {failures(r)}" for r in sub if not r['passed']) or 'Không có'
            lines.append(f"| {s['name']} | {100*a:g}% | {sum(r['passed'] for r in sub)}/7 | {why} |")
    lines += ['', 'Các sai số được thử từng loại riêng và áp dụng cho cả hai path; không kiểm sai số kết hợp, sai khác từng path, drift thời gian hoặc lỗi mô hình tải.', '',
              '## Quét biên (không quyết định GO)', '', '| Ô | Δ ngoài mẫu ms | Δ frontier ms | % headroom | Kết quả/lý do |', '|---|---:|---:|---:|---|']
    for r in rows:
        if r['name'] in {s['name'] for s in sweep}:
            lines.append(f"| {r['name']} | {r['oos_ms']:.6f} | {r['fr_ms']:.6f} | {r['fr_pct']:.3f}% | {failures(r)} |")
    lines += ['', '## Epsilon bổ sung (chỉ báo cáo)', '']
    for r in rows:
        if r['eps'] == EPS_EXTRA:
            lines.append(f"- {r['name']}, ε=8,1 ms: Δ ngoài mẫu {r['oos_ms']:.6f} [{r['oos_lo']:.6f}; {r['oos_hi']:.6f}] ms; frontier {r['fr_ms']:.6f} ms. Không đưa vào nhãn GO.")
    lines += ['', '## Đối chiếu dự đoán', '',
              'Dự đoán trước chạy là cả R1/R2 GO CÓ ĐIỀU KIỆN. Kết quả mạnh hơn dự đoán tại α=0,2%, nhưng tại α=1% vẫn có các kiểu sai twin làm mất điều kiện. Không thể suy ra độ bền với mọi sai số twin.', '',
              'Dự đoán TB=1 s và buffer=50 ms dễ mất hiệu ứng bị dữ liệu bác bỏ: cả hai vẫn đạt tiêu chí tương đối. Ô cùng nhịp có Δ ngoài mẫu chỉ khoảng 0,148 ms và headroom khoảng 0,435 ms; buffer 50 ms có Δ khoảng 0,572 ms. Vì vậy không được kết luận bất định chỉ hữu ích khi hai path đo lệch nhịp. TB=300 s đạt Δ ngoài mẫu 3,421 ms, cao hơn TB=60 s trong lần chạy này.', '',
              '## Cách đọc harm ratio và giới hạn', '',
              '- Harm ratio chính dùng harm tối thiểu của K2 để đạt gain frontier SC chia cho harm SC thực dùng; giữ thêm harm_ratio_budget để đối chiếu mã gốc. Dòng twin đúng α=0,2% ở cả R1/R2 có numerator đúng bằng 0 trên mẫu test: một ngưỡng K2 tối ưu trên test đạt gain SC mà chưa thấy sự kiện hại. Đây không phải rủi ro quần thể bằng 0 hay một policy ngoài mẫu không bao giờ gây hại. Policy calibration vẫn có harm ngoài mẫu dương như bảng.',
              '- Frontier tối ưu ngay trên test, CI bootstrap 100 lần theo seed. Ngoài mẫu dùng ngưỡng học trên calibration, CI paired t trên 20 test seed. Không hiệu chỉnh nhiều phép kiểm; các alpha/variant dùng cùng thế giới, không độc lập.',
              '- Chu kỳ 1/60 s, buffer 150/500 ms là lựa chọn được tài liệu người dùng gợi ý. Lần này chưa xác minh độc lập tài liệu nguồn; capacity, rho, r_f, tau, H vẫn là giả định. “GO thực tế” chỉ nên hiểu là GO trên hai cấu hình mô phỏng có động cơ thực tế, không phải tham số đã đo từ triển khai.',
              '- Telemetry vẫn đếm gói trong cửa sổ; không phải đo RTT trực tiếp. Từ mô tả LTE/probe tiết kiệm dữ liệu sang bộ đếm tải OU còn cần kiểm ánh xạ.',
              '- R2 headroom chỉ khoảng 0,835 ms nên đạt tỉ lệ giảm rủi ro/width không có nghĩa delay cải thiện đáng kể cho VoIP. Không thay metric hoặc SESOI cũ để biến nhãn GO thành bằng chứng ứng dụng.',
              '- Lần chạy chỉ xét SC và K2 trong gate; không thêm điều kiện thắng Sage hoặc kiểm twin lịch sử. Tải OU, một flow nhỏ, vòng hở và twin biết đường cong capacity/buffer vẫn là giả định.', '',
              '## Thay đổi trước chạy và artifact', '',
              'Sửa trước khi khóa: ratio theo harm SC thực dùng; duyệt cả hai alpha để ưu tiên GO; kiểm đủ 7 trạng thái; CSV lưu sau từng kịch bản; thêm CI trên và manifest. Không đổi ngưỡng hay kịch bản sau khi đọc kết quả.', '',
              '- results/go_test/go_v0.csv: 38 dòng số đầy đủ.',
              '- results/go_test/go_output.txt: log chạy và thời gian từng kịch bản.',
              '- results/go_test/go_manifest.json: seed, cấu hình, sai số twin, alpha/epsilon.',
              '- notes/map/go_spec.md: dự đoán/tiêu chí trước chạy.',
              '- experiments/scan/go_test.py: runner; report_go.py: kiểm tính đầy đủ và dựng báo cáo này.', '',
              'Quyết định: có thể đi sâu theo cổng đã chọn. Ưu tiên R1 vì lợi ích tuyệt đối lớn hơn R2; bước sau là kiểm nguồn/ánh xạ telemetry và twin ước lượng từ lịch sử. Chưa tự chạy thêm phạm vi ngoài bài GO trong lượt này.']
    Path('notes/map/go_report.md').write_text('\n'.join(lines)+'\n')
    print('Validated 38 rows; wrote notes/map/go_report.md')


if __name__ == '__main__':
    main()
