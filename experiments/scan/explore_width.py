"""Exploratory DES sensitivity study; old preregistered results are untouched.

Run --stage audit, screen, or verify. Seed splits are distinct by stage.
Stores full summaries, per-seed OOS outcomes, configs and ignored raw caches.
"""
import argparse
import copy
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy import stats

from experiments.scan.cell import _pool, get_curve, twin_inputs
from experiments.scan.des_world import simulate_world_des
from experiments.scan.frontier import matched as legacy_matched
from experiments.scan.grid import grid, make_cell
from experiments.scan.rules import orient, s0_trajectory, tune_threshold
from experiments.scan.strict_frontier import matched, optimum, ranking_scores

ROOT = Path('results/explore_width')


def configurations():
    kw = dict(r_f=300e3, tau=10., T_tel_A=.5, probe_B=30., rho_B=.95, alpha=.002)
    cases = {}

    def add(name, **changes):
        c = make_cell(name, **(kw | changes))
        cases[name] = c
        return c

    add('base_m069')
    for k in (166, 332, 664):
        add(f'buffer_{k}', k=k)
    for tau in (2., 30., 60.):
        add(f'tau_{tau:g}', tau=tau)
    for T in (.5, 2., 5., 10., 60., 120.):
        add(f'probeB_{T:g}', probe_B=T)
    for rf in (30e3, 100e3, 600e3):
        add(f'flow_{rf:g}', r_f=rf)
    for rho in (.8, .9, 1., 1.05):
        add(f'load_{rho:g}', rho_A=rho, rho_B=rho)
    for alpha in (.0005, .001, .005, .01, .02):
        add(f'alpha_{alpha:g}', alpha=alpha)
    for H in (.1, 2.):
        add(f'hold_{H:g}', H=H)
    for C in (5., 2., 1.):
        # Constant utilization fluctuations and implied number of background flows.
        add(f'capacity_{C:g}_fixedK', mbps=C, r_f=300e3*C/10)
        add(f'capacity_{C:g}_fixedBuffer', mbps=C, r_f=300e3*C/10, k=round(83*C/10))
    for q in (4., 16.):
        c = copy.deepcopy(cases['base_m069'])
        c['name'] = f'similarity_{q:g}'
        c['mbps'] /= q
        c['H'] *= q
        c['a'] *= q
        for p in (c['A'], c['B']):
            for f in ('tau', 'T_tel', 'd', 'stall_mean'):
                p[f] *= q
        c['axes']['r_f'] /= q
        c['axes']['tau'] *= q
        c['axes']['T_tel_A'] *= q
        c['axes']['probe_B'] *= q
        cases[c['name']] = c
    for c in grid():
        if c['name'] in ('m069', 'm071', 'm085', 'm080', 'm083'):
            cases[c['name']] = c
    for T in (.05, .1, .2):
        add(f'freshA_{T:g}', T_tel_A=T)
    for path, tau in (('A', 2.), ('B', 30.), ('B', 60.)):
        c = add(f'tau{path}_{tau:g}')
        c[path]['tau'] = tau
    for path in 'AB':
        c = add(f'quiet{path}')
        c[path]['sigma'] /= 3
    c = add('stallB')
    c['B']['stall_p'], c['B']['stall_mean'] = .5, 30.
    add('joint_small', r_f=600e3, rho_A=.8, rho_B=.8, T_tel_A=.1, probe_B=60.)
    add('joint_medium', k=332, r_f=600e3, rho_A=.8, rho_B=.8, T_tel_A=.1, probe_B=60.)
    add('joint_large', k=664, r_f=600e3, rho_A=.8, rho_B=.8, T_tel_A=.1, probe_B=60.)
    add('joint_large_tau30', k=664, r_f=600e3, rho_A=.8, rho_B=.8, T_tel_A=.1, probe_B=60., tau=30.)
    add('buffer_1328', k=1328)
    # Sensitivity to quadrature and to retaining the ORIGINAL absolute harm epsilon.
    c = copy.deepcopy(cases['similarity_16'])
    c['name'], c['eps_over_s'] = 'similarity_16_fixed_eps', c['eps_over_s']/16
    cases[c['name']] = c
    for src in ('base_m069', 'joint_large', 'buffer_664'):
        c = copy.deepcopy(cases[src])
        c['name'], c['gh_nodes'] = f'{src}_gh256', 256
        cases[c['name']] = c
    return cases


def raw(seed, cell):
    from experiments.scan import twin
    nodes = cell.get('gh_nodes', 64)
    twin.GH_X, twin.GH_W = np.polynomial.hermite.hermgauss(nodes)
    twin.GH_W /= np.sqrt(np.pi)
    curve, s_ms = get_curve(cell)
    # alpha affects reference/policy tuning only, not simulation or twin.
    physical = {k: v for k, v in cell.items() if k not in ('name', 'axes', 'alpha', 'n_flows_min')}
    key = hashlib.sha256(json.dumps([seed, physical], sort_keys=True).encode()).hexdigest()[:24]
    path = ROOT/'raw'/f'{key}.npz'
    if path.exists():
        with np.load(path) as z:
            return {k: z[k] for k in z.files if not k.startswith('diag_')}, {k[5:]: float(z[k]) for k in z.files if k.startswith('diag_')}
    w = simulate_world_des(seed, cell)
    d = dict(twin_inputs(w, cell, curve, cell['eps_over_s']*s_ms), I_A=w['A']['D_des']-w['B']['D_des'])
    diag = {f'{name}_{k}': v for name in 'AB' for k, v in w[name]['diagnostics'].items()}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **d, **{f'diag_{k}': v for k, v in diag.items()})
    return d, diag


def reference(cal_raw, test_raw, alpha, eps):
    h0 = 0.
    for _ in range(2):
        c = _pool([orient(d, s0_trajectory(d['Iplug_A'], h0)) for d in cal_raw])
        h0 = tune_threshold(c['Iplug'], c['I'], (c['I'] < -eps).astype(float), alpha)
    cal = _pool([orient(d, s0_trajectory(d['Iplug_A'], h0)) for d in cal_raw])
    test = [orient(d, s0_trajectory(d['Iplug_A'], h0)) for d in test_raw]
    return cal, test, h0


def evaluate(cell, cal_seeds, test_seeds, n_boot=0):
    _, s_ms = get_curve(cell)
    eps, alpha = cell['eps_over_s']*s_ms, cell['alpha']
    cal_pairs = [raw(s, cell) for s in cal_seeds]
    test_pairs = [raw(s, cell) for s in test_seeds]
    cal, test, h0 = reference([p[0] for p in cal_pairs], [p[0] for p in test_pairs], alpha, eps)
    o = _pool(test)
    r = matched(o, alpha, eps)
    old = legacy_matched(test, alpha, eps)
    r['legacy_width_ms'] = float(old['d'])
    r['strict_minus_legacy_ms'] = r['width_ms'] - float(old['d'])
    r['h0'] = float(h0)
    # Exact calibration thresholds, no 400-point lambda grid approximation.
    sc = ranking_scores(cal)
    opt = {rule: optimum(score, cal['I'], cal['I'] < -eps, alpha*len(cal['I'])) for rule, score in sc.items()}
    seed_rows = []
    for seed, t in zip(test_seeds, test):
        ss = ranking_scores(t)
        row = {'seed': seed, 'headroom': float(np.maximum(t['I'], 0).mean())}
        for rule in ss:
            a = ss[rule] > opt[rule]['threshold']
            row[f'gain_{rule}'] = float((a*t['I']).mean())
            row[f'harm_{rule}'] = float((a & (t['I'] < -eps)).mean())
            row[f'switch_{rule}'] = float(a.mean())
        row['width_ms'] = row['gain_K2'] - row['gain_SC']
        seed_rows.append(row)
    for k in seed_rows[0]:
        if k != 'seed':
            r[f'oos_{k}'] = float(np.mean([x[k] for x in seed_rows]))
    width = np.array([x['width_ms'] for x in seed_rows])
    ci = stats.t.ppf(.975, len(width)-1)*width.std(ddof=1)/np.sqrt(len(width))
    r['oos_width_lo'], r['oos_width_hi'] = float(width.mean()-ci), float(width.mean()+ci)
    for rule in opt:
        r[f'cal_harm_{rule}'] = opt[rule]['harm']/len(cal['I'])
        r[f'cal_threshold_{rule}'] = opt[rule]['threshold']
    for k in test_pairs[0][1]:
        r[k] = float(np.mean([p[1][k] for p in test_pairs]))
    r['buffer_ms'] = cell['k']*s_ms
    r['service_ms'] = s_ms
    r['epsilon_ms'] = eps
    r['alpha'] = alpha
    r['capacity_mbps'] = cell['mbps']
    r['k'] = cell['k']
    r['tau'] = cell['A']['tau']
    r['T_A'] = cell['A']['T_tel']
    r['T_B'] = cell['B']['T_tel']
    r['sigma_A'] = cell['A']['sigma']
    r['rho_A'] = cell['A']['rho_bar']
    r['rho_B'] = cell['B']['rho_bar']
    r['H'] = cell['H']
    r['n_epochs'] = cell['n_epochs']
    r['n_cal'], r['n_test'] = len(cal_seeds), len(test_seeds)
    # Dimensionless identity: width_ms = service_ms * width_in_service_units.
    r['width_in_service_units'] = r['width_ms']/s_ms
    if n_boot:
        rng = np.random.default_rng(54321)
        bs = [matched(_pool([test[i] for i in rng.integers(0, len(test), len(test))]), alpha, eps)['width_ms'] for _ in range(n_boot)]
        r['width_lo'], r['width_hi'] = map(float, np.percentile(bs, [2.5, 97.5]))
    return r, seed_rows


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for row in rows for k in row}))
        w.writeheader()
        w.writerows(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', choices=['audit', 'screen', 'verify'], required=True)
    p.add_argument('--names', nargs='*')
    p.add_argument('--bootstrap', type=int, default=0)
    p.add_argument('--label', help='Artifact prefix; preserves earlier adaptive stages')
    args = p.parse_args()
    cases = configurations()
    if args.stage == 'audit':
        names = args.names or ['m069', 'm071', 'm085', 'm080', 'm083']
        cal, test = range(30001, 30021), range(20001, 20021)
    elif args.stage == 'screen':
        names = args.names or [n for n in cases if not n.startswith('m0')]
        cal, test = range(70001, 70009), range(71001, 71009)
        for c in cases.values():
            c['n_epochs'] = 4000  # screening only; full durations restored in verify
    else:
        if not args.names:
            p.error('--verify requires an explicitly recorded shortlist via --names')
        names = args.names
        cal, test = range(72001, 72021), range(73001, 73021)
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {'stage': args.stage, 'cal_seeds': list(cal), 'test_seeds': list(test), 'bootstrap': args.bootstrap,
                'configs': [cases[n] for n in names], 'status': 'exploratory, post-selection'}
    label = args.label or args.stage
    (ROOT/f'{label}_manifest.json').write_text(json.dumps(manifest, indent=2))
    rows, seeds, start = [], [], time.time()
    for name in names:
        r, sr = evaluate(cases[name], cal, test, args.bootstrap)
        rows.append(dict(name=name, **r))
        seeds.extend(dict(name=name, **x) for x in sr)
        write_csv(ROOT/f'{label}.csv', rows)
        write_csv(ROOT/f'{label}_seeds.csv', seeds)
        print(f"{name:28s} matched={r['width_ms']:+.4f} ms ({r['width_pct']:.2f}%head) "
              f"OOS={r['oos_width_ms']:+.4f} [{r['oos_width_lo']:+.4f},{r['oos_width_hi']:+.4f}] "
              f"harmK/SC={r['oos_harm_K2']/r['alpha']:.2f}/{r['oos_harm_SC']/r['alpha']:.2f}alpha "
              f"buffer={r['buffer_ms']:.1f} ms probeDropA={r['A_probe_drop_rate']:.3f} "
              f"[{time.time()-start:.1f}s]", flush=True)
    print(f'Complete: {len(rows)} cells, {time.time()-start:.1f}s', flush=True)


if __name__ == '__main__':
    main()
