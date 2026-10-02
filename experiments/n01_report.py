"""Tổng hợp kết quả L1.2 từ tệp đo đã lưu, không chạy thêm thế giới mô phỏng."""
import csv
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'experiments/results'


def read_rows(name):
    with (OUT / name).open() as f:
        return list(csv.DictReader(f))


def write_rows(name, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    summary, pooled, comparisons = [], {}, []
    for h in (.5, 5., 30.):
        rows = read_rows(f'n01b_H{h:g}_metrics.csv')
        assert len(rows) == 88
        pooled[h] = {(r['generator'], r['sandbox']): r for r in rows if r['seed'] == 'pooled'}
        raw = np.load(ROOT / f'results/raw/n01/n01b_H{h:g}_epochs.npz')
        assert len(raw['I']) == 40000 and np.isfinite([raw[k] for k in ('I', 'real', 'ideal', 'plug')]).all()
        for row in rows:
            pick = np.ones(len(raw['I']), dtype=bool) if row['seed'] == 'pooled' else raw['seed'] == int(row['seed'])
            if row['generator'] == 'G_greedy':
                pick &= raw['plug'] > 0
            I = raw['I'][pick]
            a = dict(clairvoyant=raw['I'] > 0, ideal=raw['ideal'] > 0, real=raw['real'] > 0,
                     reject_all=np.zeros(len(raw['I']), dtype=bool))[row['sandbox']][pick]
            harm, good = I < -.6048, I > .6048
            assert int(row['n']) == len(I)
            assert int(row['false_approval']) == (a & harm).sum()
            assert int(row['false_rejection']) == (~a & good).sum()
            assert np.isclose(float(row['regret_ms']), np.mean(np.maximum(I, 0) - a * I))
            six = ('false_approval', 'false_rejection', 'approve_good', 'approve_neutral', 'reject_harm', 'reject_neutral')
            assert sum(int(row[k]) for k in six) == len(I)
        ideal, real = (pooled[h]['G_all', p] for p in ('ideal', 'real'))
        ri, rr = float(ideal['regret_ms']), float(real['regret_ms'])
        summary.append(dict(H_s=h, H_over_tau=h/10, ideal_regret_ms=ri, real_regret_ms=rr,
                            excess_regret_ms=rr-ri, excess_fraction=(rr-ri)/rr,
                            ideal_false_approval_given_harm=float(ideal['false_approval_given_harm'])))
    write_rows('n01b_summary.csv', summary)
    print('PASS: 264 dòng metrics (theo seed + pooled), sáu ô, DN/TCN và regret khớp 120.000 dòng epoch đã lưu.')

    def compare(name, actual, expected, tolerance):
        comparisons.append(dict(metric=name, local=float(actual), lesson=expected, delta=float(actual)-expected,
                                tolerance=tolerance, match=abs(float(actual)-expected) <= tolerance))

    for row, ri, rr, far in zip(summary, [.324, 2.38, 4.71], [4.599, 5.75, 5.16], [.053, .261, .804]):
        h = row['H_s']
        compare(f'H{h:g}: ideal regret ms', row['ideal_regret_ms'], ri, .0005 if h == .5 else .005)
        compare(f'H{h:g}: real regret ms', row['real_regret_ms'], rr, .0005 if h == .5 else .005)
        compare(f'H{h:g}: ideal DN|harm', row['ideal_false_approval_given_harm'], far, .0005)
    trials = read_rows('n01c_crn_trials.csv')
    assert len(trials) == 300
    crn = np.array([float(r['effect_crn_ms']) for r in trials])
    ind = np.array([float(r['effect_ind_ms']) for r in trials])
    stats = []
    for name, x, expected in [('CRN', crn, [8.05, 7.72, .54, 0.]), ('Independent', ind, [7.51, 9.36, -6.43, .093])]:
        values = [x.mean(), x.std(), x.min(), np.mean(x < 0)]
        stats.append(dict(method=name, n=len(x), mean_ms=values[0], sd_ms=values[1], min_ms=values[2], negative_fraction=values[3]))
        for key, actual, target in zip(('mean ms', 'sd ms (ddof=0)', 'min ms', 'P(effect<0)'), values, expected):
            compare(f'n01c {name}: {key}', actual, target, .0005 if key == 'P(effect<0)' else .005)
    write_rows('n01c_summary.csv', stats)
    write_rows('n01_lesson_comparison.csv', comparisons)
    for c in comparisons:
        print(f"{'MATCH' if c['match'] else 'DIFF'}: {c['metric']}: local={c['local']:.6f}, lesson={c['lesson']}, delta={c['delta']:+.6f}")

    fig, ax = plt.subplots(figsize=(8, 4.8), layout='constrained')
    x = np.arange(3)
    lower = np.array([r['ideal_regret_ms'] for r in summary])
    upper = np.array([r['excess_regret_ms'] for r in summary])
    ax.bar(x, lower, width=.55, color='#537b9b', label='Regret lý tưởng xấp xỉ')
    ax.bar(x, upper, bottom=lower, width=.55, color='#df994c', label='Chênh regret thực tế − lý tưởng')
    for i, (lo, hi) in enumerate(zip(lower, upper)):
        ax.text(i, lo/2, f'{lo:.3f}', ha='center', va='center', color='white')
        ax.text(i, lo+hi/2, f'{hi:.3f}', ha='center', va='center')
    ax.set(xticks=x, xticklabels=['H = 0,5 s', 'H = 5 s', 'H = 30 s'], ylim=(0, 7.1),
           ylabel='Regret (ms / lần kiểm)', title='POS_probeB · 10 seed pilot · G_all · kết quả local')
    ax.legend(loc='upper left', frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(OUT / 'n01_regret_decomposition.png', dpi=160)
    plt.close(fig)

    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = ['# L1.2 — Báo cáo thực hiện local (2026-10-02)', '',
              '**Đã chạy n01, n01b ở ba H và n01c; tạo N1 và cập nhật N0.**', '',
              '**Tái lập có sai lệch:** n01, n01c và phần sandbox thực tế khớp lesson ở độ chính xác được in. '
              'Các số sandbox lý tưởng khác bảng lesson; nguyên bản script attachment vẫn cho đúng từng bit các mảng local ở cả 30 tổ hợp H–seed.', '',
              f'Base commit `{base}`. Kết quả là minh hoạ đã biết số trước khi chạy, không phải xác nhận mù. '
              'POS_probeB, seed 9101–9110; 40.000 epoch/H; luật kỳ vọng >0, luôn ở A, không áp ngân sách harm.', '',
              '![Phân rã regret theo H](n01_regret_decomposition.png)', '',
              '## 1. Ba sandbox và đối chứng — H=0,5 s, G_all', '',
              '| Sandbox | Duyệt | DN/mọi | TCN/mọi | DN/hại | TCN/lợi | Regret (ms/lần kiểm) |',
              '|---|---:|---:|---:|---:|---:|---:|']
    names = {'clairvoyant':'Biết trước', 'ideal':'Lý tưởng xấp xỉ', 'real':'Thực tế', 'reject_all':'Luôn từ chối'}
    for policy, name in names.items():
        r=pooled[.5]['G_all',policy]
        vals=[100*float(r[k]) for k in ('approval_rate','false_approval_all','false_rejection_all','false_approval_given_harm','false_rejection_given_good')]
        report.append(f"| {name} | " + ' | '.join(f'{v:.2f}%' for v in vals) + f" | {float(r['regret_ms']):.6f} |")
    report += ['', 'DN = duyệt ∧ I<−ε; TCN = từ chối ∧ I>ε; ε=0,6048 ms. Vùng thờ ơ tính cả biên.', '',
               'Regret = **trung bình** [max(I,0)−aI], không phải tổng chi phí; vẫn tính mất mát trong vùng thờ ơ và không phụ thuộc ε.', '',
               '## 2. Phân rã theo H', '',
               '| H (s) | H/τ | Regret lý tưởng (ms) | Regret thực tế (ms) | Chênh (ms) | Chênh / thực tế | Lý tưởng DN/hại |',
               '|---|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        report.append(f"| {r['H_s']:g} | {r['H_over_tau']:g} | {r['ideal_regret_ms']:.6f} | {r['real_regret_ms']:.6f} | {r['excess_regret_ms']:.6f} | {100*r['excess_fraction']:.2f}% | {100*r['ideal_false_approval_given_harm']:.2f}% |")
    report += ['', 'Phân rã là đồng nhất thức trên mẫu. Gọi hai phần là “không tránh được” và “do thông tin/mô hình” '
               'cần oracle đúng, tập thông tin/luật phù hợp và diễn giải theo kỳ vọng. Bản ideal hiện tại chỉ là xấp xỉ. '
               'Chênh regret giữa hai luật trên mẫu hữu hạn không có bảo đảm luôn không âm.', '',
               'H thay đổi cả khoảng chấm, nhịp epoch và độ dài quỹ đạo. Đây không phải ba cửa sổ lồng nhau trên cùng một trace; '
               'xu hướng ba H không chứng minh regret không tránh được tăng đơn điệu với mọi H.', '',
               '## 3. Đổi bộ sinh đề xuất — cùng sandbox thực tế, H=0,5 s', '',
               '| Bộ sinh | Số đề xuất | Hại/đề xuất | DN/hại | TCN/lợi | P(hại/duyệt) |', '|---|---:|---:|---:|---:|---:|']
    for gen in ('G_all','G_greedy'):
        r=pooled[.5][gen,'real']
        report.append(f"| {gen} | {r['n']} | " + ' | '.join(f'{100*float(r[k]):.2f}%' for k in ('harm_rate','false_approval_given_harm','false_rejection_given_good','harm_given_approval')) + ' |')
    report += ['', 'Tỉ lệ theo lớp cũng đổi khi thay bộ sinh. Lỗi tương quan do dùng chung telemetry là giải thích ứng viên, chưa được tách nhân quả.', '',
               '## 4. Hai ví dụ xác suất và CRN', '',
               '- μ=0,5, sd=3, ε=0,5 ms: P(I<−ε)=36,94%; P(I<0)=43,38%; toàn vùng thờ ơ=13,06%. '
               'Phần thờ ơ âm nằm trong I<0 chỉ là **6,44 điểm %**, không phải toàn bộ 13,06%.',
               '- Ví dụ label shift: 10%/50% đề xuất có hại → P(hại|duyệt)=1,22%/10,00%.', '',
               '| Cách ghép | TB (ms) | SD (ms, ddof=0) | Nhỏ nhất (ms) | Hiệu ứng âm |', '|---|---:|---:|---:|---:|']
    for r in stats:
        report.append(f"| {r['method']} | {r['mean_ms']:.6f} | {r['sd_ms']:.6f} | {r['min_ms']:.6f} | {100*r['negative_fraction']:.2f}% |")
    report += ['', 'n01c: 300 lần kiểm, seed 9101, nền ρ=0,85, thêm Δρ=0,1 từ đầu mô phỏng, warm-up=2 s, H=0,5 s. '
               'Đo delay probe ảo được nhận trên B, không trực tiếp đo các gói nền hay nhóm được chuyển.', '',
               'CRN giữ chung arrivals nền; gói chuyển đã có trong warm-up nên workload hai nhánh ở thời điểm bắt đầu chấm có thể khác. '
               'Đây là so hai chế độ tải, **chưa là can thiệp chuyển tại t từ cùng trạng thái**. '
               'Độc lập vẫn có thể dùng ước lượng chênh kỳ vọng; từng hiệu ứng âm không phải lỗi engine. '
               'CRN không chứng minh dấu luôn dương khi hàng đợi hữu hạn có drop và điều kiện chỉ nhận probe được phục vụ.', '',
               '## 5. Kiểm chứng và sai lệch so với lesson', '',
               '- Neo `rhohat`, `age`, `G_true` A/B trùng từng bit với `simulate_world` cho cả 30 tổ hợp H–seed.',
               '- Nguyên bản `n01b` trong attachment cho mảng I/real/ideal/plug trùng từng bit với dữ liệu local đã xuất.',
               '- 264 dòng metric được kiểm từ 120.000 epoch; sáu ô cộng đúng mẫu số; regret khớp headroom−gain.',
               '- 73 kiểm thử đạt, gồm biên ε, mẫu số theo bộ sinh, neo tuổi telemetry và CRN với can thiệp rỗng.', '',
               '| Chỉ số có sai lệch | Local | Lesson | Local − lesson |', '|---|---:|---:|---:|']
    for c in comparisons:
        if not c['match']:
            report.append(f"| {c['metric']} | {c['local']:.6f} | {c['lesson']} | {c['delta']:+.6f} |")
    report += ['', 'Với W=10⁻⁶ s, `var_box` tính hiệu hai số gần nhau: Var(W)/σ²=0,999200722 thay vì gần 1. '
               'Phương sai hậu nghiệm ở H=0,5 thấp hơn giới hạn quan sát điểm OU liên tục khoảng 1,812%; '
               'ở H=5 và 30 là 0,205% và 0,022%. Đây là vấn đề ổn định số đo được, '
               '**chưa chứng minh là nguyên nhân duy nhất** của khác biệt với bảng lesson. Không có môi trường/code thực chạy của bên soạn lesson để xác định nguyên nhân.', '',
               'Ngoài ra, lý tưởng dùng tích phân OU liên tục và quadrature Gauss–Hermite, còn world dùng tích phân trên lưới dt=0,05 s; '
               'không gọi đây là oracle chính xác của world rời rạc. Khoảng a là ngẫu nhiên tương lai đối với cả ideal biết lúc t; '
               'không thể quy toàn bộ ảnh hưởng a vào phần chênh regret thực tế−ideal.', '',
               '## 6. Tệp và lệnh tái lập', '',
               '- [N1 concepts](../../notes/novelty/N1_verdict_concepts.md), [N0 question card](../../notes/novelty/N0_question_card.md).',
               '- Output: [n01](n01_verdict_examples_output.txt), [n01b](n01b_three_sandboxes_output.txt), [n01c](n01c_crn_two_branches_output.txt).',
               '- CSV metrics theo seed/pooled: [H0,5](n01b_H0.5_metrics.csv), [H5](n01b_H5_metrics.csv), [H30](n01b_H30_metrics.csv).',
               '- [Tổng hợp H](n01b_summary.csv), [300 cặp CRN](n01c_crn_trials.csv), [đối chiếu lesson](n01_lesson_comparison.csv).',
               '- [Audit nguyên bản và số học](n01b_supplied_audit_output.txt), [CSV audit phương sai](n01b_ideal_numerical_audit.csv), [pytest](n01_tests_output.txt).',
               '- Raw từng epoch: `results/raw/n01/n01b_H{0.5,5,30}_epochs.npz` (local, gitignored; sinh lại bằng n01b).', '',
               '```bash', '.venv/bin/python -m experiments.n01_verdict_examples',
               'for hold_s in 0.5 5 30; do .venv/bin/python -m experiments.n01b_three_sandboxes --H "$hold_s"; done',
               '.venv/bin/python -m experiments.n01c_crn_two_branches',
               '.venv/bin/python -m experiments.n01_audit_ideal',
               '.venv/bin/python -m pytest tests/test_n01_verdict.py tests/test_scan.py tests/test_mdk.py -q',
               '.venv/bin/python -m experiments.n01_report', '```', '',
               'Có thể thêm `--lesson /đường/dẫn/attachment.txt` vào lệnh audit để kiểm lại nguyên bản Python trong lesson tin cậy. '
               'Script này thực thi đoạn mã lấy từ tệp đó. Các tham chiếu literature trong lesson chưa được kiểm lại ở lượt triển khai này.']
    (OUT/'n01_report.md').write_text('\n'.join(report)+'\n')
    sources = list((ROOT/'experiments').glob('n01*.py')) + [ROOT/'experiments/scan'/n for n in ('world.py','twin.py','cell.py','grid.py')] + [ROOT/'experiments/f04b_des_gap.py',ROOT/'ndtrisk/theory/mdk.py',ROOT/'tests/test_n01_verdict.py']
    results = [p for p in OUT.glob('n01*') if p.is_file() and p.name != 'n01_manifest.json' and p.name != 'n01_validation_output.txt']
    manifest = dict(date='2026-10-02',base_commit=base,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                    original_n01b_sha256='e983ea12c8ee884db42a5088ceea5748f796014a45fe8c351b0a7724a6360db3',
                    original_hash_convention='Python fence body decoded as LF, no trailing newline',
                    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+results+list((ROOT/'results/raw/n01').glob('n01b_*_epochs.npz'))})
    (OUT/'n01_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Đã lưu n01_report.md, n01b_summary.csv, n01c_summary.csv, n01_lesson_comparison.csv, n01_regret_decomposition.png, n01_manifest.json')


if __name__ == '__main__':
    main()
