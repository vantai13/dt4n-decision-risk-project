"""Tổng hợp v5 từ CSV đã lưu, không sinh lại thế giới hay tune lại luật."""
import csv
import json
import platform
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

import numba
import numpy as np
import scipy

from experiments.scan.rollout_v2 import ci

OUT = Path('results/go_test')


def save_csv(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def main():
    groups = defaultdict(dict)
    with (OUT / 'rollout_v5_seeds.csv').open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        key = row['alpha'], row['rule'], row['split']
        seed = int(row['seed'])
        if seed in groups[key]:
            raise ValueError(f'Duplicate seed: {key}, {seed}')
        groups[key][seed] = row
    for key, data in groups.items():
        expected = set(range(86001, 86021) if key[2] == 'calibration' else range(89001, 89021))
        if data.keys() != expected:
            raise ValueError(f'Incomplete/wrong seed range: {key}')
        if len({x['policy'] for x in data.values()}) != 1:
            raise ValueError(f'Policy must be frozen across seeds: {key}')
    summary, comparisons = [], []
    alphas = ('0.002', 'inf')
    rules = ('S0', 'SC', 'S0dir', 'SCdir', 'SCtab8', 'SCtab24', 'SClin', 'K2')
    for a in alphas:
        k2 = groups[a, 'K2', 'test']
        for r in rules:
            for split in ('calibration', 'test'):
                data = groups[a, r, split]
                values = np.array([[float(x[c]) for c in ('delay_ms', 'harm_1s_per_epoch',
                                                          'harm_window_per_epoch', 'switches_per_epoch')]
                                   for _, x in sorted(data.items())])
                if not np.isfinite(values).all():
                    raise ValueError('Nonfinite result')
                summary.append(dict(alpha=a, rule=r, split=split, n_seeds=len(data),
                                    delay_ms=values[:, 0].mean(), harm_1s=values[:, 1].mean(),
                                    harm_window=values[:, 2].mean(), switches_per_min=60*values[:, 3].mean()))
            test = groups[a, r, 'test']
            diff = np.array([float(test[s]['delay_ms'])-float(k2[s]['delay_ms']) for s in sorted(test)])
            m, lo, hi = ci(diff)
            base = np.mean([float(x['delay_ms']) for x in test.values()])
            comparisons.append(dict(alpha=a, baseline=r, delta_ms=m, lo95_ms=lo, hi95_ms=hi,
                                    improvement_pct=100*m/base))
    same = {r: all(groups['0.002', r, split][s]['policy'] == groups['inf', r, split][s]['policy']
                   for split in ('calibration', 'test') for s in groups['0.002', r, split]) for r in rules}
    save_csv(OUT/'rollout_v5_summary.csv', summary)
    save_csv(OUT/'rollout_v5_comparisons.csv', comparisons)
    lookup = {(r['rule'], r['split']): r for r in summary if r['alpha'] == '0.002'}
    lines = ['# Rollout v5 — tái lập POST HOC', '',
             f'Một ô R3_outage, 20 seed calibration + 20 seed test, {len(rows)} bản ghi seed/luật.',
             'Hold-down 30 s; horizon twin 30 s; α=0,002 và ∞.',
             f'Chính sách α hữu hạn và ∞ giống nhau ở {sum(same.values())}/8 họ (so mọi tham số).', '',
             'Dương = delay baseline − delay K2, tốt cho K2; CI t ghép cặp qua 20 seed.', '',
             '| Luật | Delay cal → test ms | Luật − K2 ms [CI 95%] | Giảm delay | Harm_W test (% epoch) |',
             '|---|---:|---:|---:|---:|']
    for x in comparisons:
        if x['alpha'] != '0.002':
            continue
        r = x['baseline']
        cal, test = lookup[r, 'calibration'], lookup[r, 'test']
        lines.append(f"| {r} | {cal['delay_ms']:.3f} → {test['delay_ms']:.3f} | "
                     f"{x['delta_ms']:+.3f} [{x['lo95_ms']:+.3f}; {x['hi95_ms']:+.3f}] | "
                     f"{x['improvement_pct']:+.2f}% | {100*test['harm_window']:.4f}% |")
    with (OUT/'rollout_v5_diagnostics.csv').open() as f:
        diagnostics = list(csv.DictReader(f))
    risk = next(x for x in diagnostics if x['twin_horizon_s'] == '30'
                and x['diagnostic'] == 'risk_calibration' and x['lo'] == '0.001')
    predicted, actual = float(risk['predicted']), float(risk['observed_window'])
    lines.extend(['', '## Diễn giải', '',
                  '- K2 hơn SClin hai tham số ở ô đã dùng: +0,451 ms, CI loại 0.',
                  '  Đây chưa phải xác nhận mới, chưa loại mọi hàm ngưỡng hai tham số khác.',
                  '- So SCtab24 có ràng buộc và ba khởi đầu: +0,082 ms, CI chứa 0;',
                  '  chưa chứng minh hơn, cũng chưa chứng minh tương đương.',
                  '- α hữu hạn/∞ chọn cùng chính sách: ràng buộc không cắn cho ô và lưới này,',
                  '  không phải định lý cho các chế độ/twin khác.',
                  f'- Twin 30 s, p₋ trong [0,001; 0,01), Ī>0: p₋ TB {predicted:.6f},',
                  f'  harm_W thật {actual:.6f}, gấp {actual/predicted:.2f} lần. p₋ chưa hiệu chỉnh xác suất.',
                  '  Tune harm bằng nhãn thật, không thay nó bằng p₋ dự đoán.',
                  '- Các luật SC* dùng cùng tâm của cùng twin biết đúng ρ̄, σ, τ;',
                  '  lợi thế ở đây chưa nói được độ bền khi twin phải tự ước lượng.', '',
                  '## Provenance / giới hạn', '',
                  'Claude đã chạy trước trong sandbox. SClin/harm_W được thiết kế sau v4.',
                  'Calibration 86001–86020, test 89001–89020 đã dùng; không phải holdout mới.',
                  '29 epoch cuối dùng cửa sổ ngắn dần theo code nguồn; không phải mọi harm_W đều đủ 30 s.',
                  'Harm chia cho tất cả epoch; không phải tỷ lệ hại trong các lần đổi.',
                  'CI mang tính khám phá, không hiệu chỉnh đa so sánh.',
                  'Horizon khớp hold-down không bảo đảm mô hình delay đúng do phi tuyến và bộ nhớ hàng đợi.',
                  'Không đổi phán quyết/SESOI VoIP cũ; không khẳng định uncertainty chỉ có giá trị trong outage.', '',
                  '## Bộ ước lượng chuẩn bị để review', '',
                  '`experiments/scan/telemetry_fit.py`: chỉ đọc telemetry tươi/timestamp và T,S;',
                  'ước lượng ρ̄ bằng trung bình, σ và τ bằng covariance off-diagonal giữ khoảng trống outage.',
                  'Đã kiểm bằng OU-box/Poisson tổng hợp, không dùng tham số DES thật.',
                  'Chưa chạy DES seed 90001–90020/91001–91020; chưa đo K2 với twin ước lượng.', '',
                  '## Tệp', '',
                  '- `rollout_v5_output.txt`: log đầy đủ.',
                  '- `rollout_v5_seeds.csv`: calibration/test, harm_W, harm_1s, chuyển đường, mọi tham số.',
                  '- `rollout_v5_diagnostics.csv`: bias và hiệu chỉnh rủi ro cho horizon 1/30 s.',
                  '- `rollout_v5_policies.json`: chính sách và kiểm α hữu hạn/∞.',
                  '- `rollout_v5_summary.csv`, `rollout_v5_comparisons.csv`: tổng hợp và CI.',
                  '- `telemetry_fit_synthetic.{csv,json}`, `telemetry_fit_synthetic_output.txt`: kiểm tổng hợp.',
                  '- `notes/map/telemetry_fit_review.md`: công thức, giả định và protocol dự thảo chờ review.'])
    (OUT/'rollout_v5_report.md').write_text('\n'.join(lines)+'\n')
    files = [Path('experiments/scan/rollout_v5.py'), Path('experiments/scan/telemetry_fit.py'),
             OUT/'rollout_v5_seeds.csv', OUT/'rollout_v5_output.txt', OUT/'rollout_v5_diagnostics.csv']
    manifest = dict(base_commit='634e133', classification='POST HOC reproduction',
                    claude_previously_ran_in_sandbox=True, sclin_and_window_harm_added_after_v4=True,
                    reused_calibration=[86001, 86020], reused_test=[89001, 89020],
                    seed_rows=len(rows), same_policy_finite_vs_infinite_alpha=same,
                    tail_windows_shortened=True, fresh_v6_des_calibration_and_test_not_run=True,
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                    numba=numba.__version__, sha256={str(p): sha256(p.read_bytes()).hexdigest() for p in files})
    (OUT/'rollout_v5_manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
    print('\n'.join(lines[:19]))
    print(f'\nSaved report and audit files to {OUT}')


if __name__ == '__main__':
    main()
