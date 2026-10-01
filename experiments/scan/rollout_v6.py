"""v6: twin ước lượng từ calibration; cấm chạy khi protocol chưa khoá.

Chạy sau prediction tác giả + commit/tag prereg-rollout-v6:
python -m experiments.scan.rollout_v6 | tee results/go_test/rollout_v6_output.txt
Không có phép so tương đương: SCtab24 chỉ mô tả. Giữ nguyên estimator v5.
"""
import argparse
import copy
import csv
import json
import subprocess
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

import numpy as np

from experiments.scan import go_test as g
from experiments.scan import rollout_v2 as v2
from experiments.scan import rollout_v5 as v5
from experiments.scan.telemetry_fit import estimate
from experiments.scan.world import PKT_BITS

CAL, TEST = range(90001, 90021), range(91001, 91061)
N, HD, H_TW, ALPHA = 6000, 30, 30., .002
PROTOCOL = Path('notes/map/rollout_v6_protocol.json')
OUT = Path('results/go_test')
LOCK_TAG = 'prereg-rollout-v6'
SOURCES = (
    'experiments/scan/rollout_v6.py', 'experiments/scan/telemetry_fit.py',
    'experiments/scan/rollout_v5.py', 'experiments/scan/rollout_v2.py',
    'experiments/scan/go_test.py', 'experiments/scan/twin.py',
    'experiments/scan/des_world.py', 'experiments/scan/world.py',
    'experiments/f04b_des_gap.py', 'ndtrisk/theory/mdk.py',
)


def source_hashes():
    return {p: sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def require_locked():
    """Kiểm trước mọi simulate/fit; draft không được mở seed calibration/test."""
    protocol = json.loads(PROTOCOL.read_text())
    prediction = protocol.get('author_prediction')
    if protocol['status'] != 'locked' or not isinstance(prediction, str) or not prediction.strip():
        raise ValueError('Protocol chưa khoá hoặc thiếu dự đoán tác giả; không mở seed mới.')
    expected = dict(calibration_seeds=[CAL.start,CAL.stop-1],test_seeds=[TEST.start,TEST.stop-1],
                    decision_epochs=N,hold_down_s=HD,twin_horizon_s=H_TW,alpha=ALPHA,
                    label_padding_epochs=HD-1,decision_cadence_s=1.,epsilon_ms=1.,
                    world='R3_outage',sc_tab24_role='descriptive',equivalence_test=False,
                    author_prediction_source='user')
    if any(protocol.get(k) != v for k,v in expected.items()):
        raise ValueError('Protocol khác cấu hình v6 đã hiện thực; không chạy.')
    if protocol.get('source_sha256') != source_hashes():
        raise ValueError('Code khác SHA đã khoá; không chạy.')
    tagged = subprocess.run(['git', 'show', f'{LOCK_TAG}:{PROTOCOL}'],
                            capture_output=True, check=False)
    if tagged.returncode or tagged.stdout != PROTOCOL.read_bytes():
        raise ValueError('Thiếu tag prereg-rollout-v6 khớp protocol đã commit; không chạy.')
    for p in SOURCES:
        content = subprocess.run(['git', 'show', f'{LOCK_TAG}:{p}'], capture_output=True, check=False)
        if content.returncode or sha256(content.stdout).hexdigest() != protocol['source_sha256'][p]:
            raise ValueError(f'{p} chưa được commit đúng trong tag prereg; không chạy.')
    return protocol


def twin_config(sc_world, fits):
    """Bản sao riêng cho twin, thay toàn bộ rho/sigma/tau bằng calibration fit."""
    sc_tw = copy.deepcopy(sc_world)
    for q in 'AB':
        f = fits[q]
        vals = np.array([f.rho_bar, f.sigma, f.tau], float)
        if not np.isfinite(vals).all() or f.rho_bar < 0 or f.sigma <= 0 or f.tau <= 0:
            raise ValueError('Fit không hợp lệ; không fallback sang tham số thật.')
        sc_tw[q].update(rho=f.rho_bar, sigma=f.sigma, tau=f.tau)
    return sc_tw


def decisions_from_telemetry(telemetry, sc_world, fits, horizon_s=H_TW):
    """Toàn bộ đường tới Ī,p₋ không nhận nhãn delay/cửa sổ tương lai."""
    sc_tw = twin_config(sc_world, fits)
    sc_tw['H'] = float(horizon_s)
    # API g.decisions cần D cho I_A báo kèm: dùng zeros; nhãn thật gắn ở prep.
    observed = {q: dict(rhohat=np.asarray(telemetry[q]['rhohat']),
                        age=np.asarray(telemetry[q]['age']),
                        D=np.zeros(len(telemetry[q]['rhohat']))) for q in 'AB'}
    return g.decisions(observed, sc_tw, {}, sc_tw['eps_ms'])


def simulate_extended(seed, sc_world, n=N, hd=HD):
    """Sinh n+hd−1 epoch nhưng chỉ n epoch điều khiển; padding CHỈ cho nhãn."""
    rng = np.random.default_rng(seed)
    rng_out = np.random.default_rng([seed, 777])
    paths = (sc_world['A'], sc_world['B'])
    H, a = sc_world['H'], sc_world['a']
    if H != 1.:
        raise ValueError('v6 khoá cadence 1 s; hd được tính theo epoch.')
    dt = min(min(min(p['T_tel'] for p in paths), H)/10, min(p['tau'] for p in paths)/20)
    warm = 3*max(p['T_tel'] for p in paths) + max(p['d'] for p in paths)
    t_dec = warm + H*np.arange(n+hd-1)
    t_end = t_dec[-1] + a + 2*H
    world = {q: v2.des_path_outage(rng, rng_out, p['mbps'], p['k'], H, a, p,
                                  t_dec, t_end, dt) for q, p in zip('AB', paths)}
    world['decision_times'] = t_dec
    return world


def calibration_fits(cal_worlds, sc_world, n=N):
    """Chỉ lấy telemetry cal[:n], không padding, không tham số thật/model label."""
    fits = {}
    for q in 'AB':
        p = sc_world[q]
        observations = [dict(rhohat=w[q]['rhohat'][:n], age=w[q]['age'][:n],
                             decision_times=w['decision_times'][:n]) for w in cal_worlds]
        fits[q] = estimate(observations, p['T_tel'], PKT_BITS/(p['mbps']*1e6))
    return fits


def full_window_mean(x, n, hd):
    x = np.asarray(x, float)
    if len(x) < n+hd-1:
        raise ValueError('Thiếu padding: không cho rút ngắn nhãn cửa sổ hold-down.')
    c = np.r_[0., np.cumsum(x)]
    return (c[hd:hd+n] - c[:n])/hd


def prep(worlds, sc_world, fits, n=N, hd=HD):
    out = []
    for w in worlds:
        telemetry = {q: dict(rhohat=w[q]['rhohat'][:n], age=w[q]['age'][:n]) for q in 'AB'}
        d = decisions_from_telemetry(telemetry, sc_world, fits)
        d['DA'], d['DB'] = w['A']['D'][:n], w['B']['D'][:n]
        d['I_A'] = d['DA']-d['DB']
        d['IW_A'] = full_window_mean(w['A']['D']-w['B']['D'], n, hd)
        d['rh_A'], d['rh_B'] = telemetry['A']['rhohat'], telemetry['B']['rhohat']
        out.append(d)
    return out


def validity_warnings(fits):
    bad = ('parameter_at_bound', 'weak_identification', 'variance_mismatch_gt20pct')
    return {q: [s for s in f.warnings if s.startswith(bad)] for q, f in fits.items()
            if any(s.startswith(bad) for s in f.warnings)}


def comparison(delta):
    m, lo, hi = v2.ci(delta)
    verdict = ('K2 tốt hơn SClin' if lo > 0 else
               'SClin tốt hơn K2' if hi < 0 else 'Chưa phân giải: CI chứa 0')
    return dict(mean_ms=float(m), lo95_ms=float(lo), hi95_ms=float(hi), verdict=verdict)


def main():
    protocol = require_locked()  # PHẢI là hành động đầu tiên, trước mở mọi seed.
    OUT.mkdir(parents=True, exist_ok=True)
    sc_world = next(sc for sc in v2.worlds() if sc['name'] == 'R3_outage')
    cal_worlds = [simulate_extended(s, sc_world) for s in CAL]
    fits = calibration_fits(cal_worlds, sc_world)
    (OUT/'rollout_v6_fits.json').write_text(json.dumps({q: asdict(f) for q, f in fits.items()}, indent=2)+'\n')
    bad = validity_warnings(fits)
    if bad:
        raise ValueError(f'Validity calibration không đạt; dừng trước test, không sửa fit: {bad}')
    cal = prep(cal_worlds, sc_world, fits)
    del cal_worlds
    g_ip = v5.grid(np.concatenate([d['Iplug_A'] for d in cal]))
    g_ib = v5.grid(np.concatenate([d['Ibar_A'] for d in cal]))
    pol = v5.tables(cal, sc_world['eps_ms'], ALPHA, g_ip, g_ib)
    rc = v5.evaluate(cal, pol, sc_world['eps_ms'])
    if any(r['harmW'].mean() > ALPHA for r in rc.values()):
        raise ValueError('Calibration policy vượt harm_W; không mở test.')
    # Chốt policy trước khi sinh bất kỳ seed test nào; không fit/tune lại.
    (OUT/'rollout_v6_policies.json').write_text(json.dumps({r: v5.policy_record(p) for r,p in pol.items()},
                                                         indent=2)+'\n')
    print('Đã freeze fit + policies trên 20 cal; mở đúng 60 seed test.', flush=True)
    test_worlds = [simulate_extended(s, sc_world) for s in TEST]
    test = prep(test_worlds, sc_world, fits)
    del test_worlds
    rt = v5.evaluate(test, pol, sc_world['eps_ms'])
    with (OUT/'rollout_v6_seeds.csv').open('w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['split','seed','rule','delay_ms','harm_window','harm_1s','switches_per_epoch'])
        for split,seeds,res in (('calibration',CAL,rc),('test',TEST,rt)):
            for r in pol:
                for i,s in enumerate(seeds):
                    writer.writerow([split,s,r,res[r]['delay'][i,0],res[r]['harmW'][i,0],
                                     res[r]['harm1'][i,0],res[r]['nsw'][i,0]])
    rows = []
    for r in pol:
        delta = rt[r]['delay'][:,0]-rt['K2']['delay'][:,0]
        m,lo,hi = v2.ci(delta)
        row = dict(rule=r,delay_cal_ms=float(rc[r]['delay'].mean()),delay_test_ms=float(rt[r]['delay'].mean()),
                   delta_ms=float(m),lo95_ms=float(lo),hi95_ms=float(hi),
                   improvement_pct=float(100*m/rt[r]['delay'].mean()),
                   harm_window=float(rt[r]['harmW'].mean()),harm_1s=float(rt[r]['harm1'].mean()),
                   switches_per_min=float(60*rt[r]['nsw'].mean()),
                   comparison_role='primary' if r=='SClin' else 'descriptive')
        rows.append(row)
        print(f"{r:8s}: {row['delay_test_ms']:.3f} ms | {m:+.3f} [{lo:+.3f}; {hi:+.3f}] "
              f"| harm_W {row['harm_window']:.4%}", flush=True)
    with (OUT/'rollout_v6_summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    primary = comparison(rt['SClin']['delay'][:,0]-rt['K2']['delay'][:,0])
    primary['test_harm_budget_met'] = bool(max(rt[r]['harmW'].mean() for r in ('SClin','K2')) <= ALPHA)
    if not primary['test_harm_budget_met']:
        primary['verdict'] += '; test harm_W vượt α, không kết luận lợi thế admissible'
    (OUT/'rollout_v6_outcome.json').write_text(json.dumps(dict(primary=primary,protocol=protocol,
        estimator_sha256=source_hashes()['experiments/scan/telemetry_fit.py'],
        sc_tab24_interpretation='descriptive only; no equivalence claim',
        limitation='OU+Poisson correctly specified family; not model-misspecification or data-efficiency evidence'),
        indent=2,ensure_ascii=False)+'\n')
    with (OUT/'rollout_v6_diagnostics.csv').open('w',newline='') as f:
        writer = csv.writer(f,lineterminator='\n')
        writer.writerow(['twin_horizon_s','diagnostic','lo','hi','n_oriented_epochs',
                         'predicted','observed_window','observed_1s','bias_ms'])
        v5.twin_check(test,sc_world['eps_ms'],writer,H_TW)
    print(primary,flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--print-lock-hashes',action='store_true',help='Chỉ đọc code SHA, không mở seed.')
    args = parser.parse_args()
    if args.print_lock_hashes:
        print(json.dumps(source_hashes(),indent=2))
    else:
        main()
