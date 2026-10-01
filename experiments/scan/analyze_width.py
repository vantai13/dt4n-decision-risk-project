"""Regenerate mechanism attribution, five-rule checks and research figures."""
import csv
import itertools
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from experiments.scan.explore_width import ROOT, configurations, raw, write_csv
from experiments.scan.cell import evaluate_cell, get_curve
from experiments.scan.confirm import confirmed


def read(name):
    with (ROOT/f'{name}.csv').open() as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in r:
            if k != 'name':
                try:
                    r[k] = float(r[k])
                except ValueError:
                    pass
    return {r['name']: r for r in rows}


def five_rules():
    rows = []
    for name in ('joint_small', 'joint_large', 'joint_large_tau30', 'joint_large_gh256', 'quietB'):
        c = configurations()[name]
        _, s = get_curve(c)
        cal = [raw(seed, c)[0] for seed in range(72001, 72021)]
        test = [raw(seed, c)[0] for seed in range(73001, 73021)]
        r = evaluate_cell(cal, test, c['alpha'], c['eps_over_s']*s, s, tuning='realized')
        r['confirmed_C'] = confirmed(r, c['alpha'])
        rows.append(dict(name=name, **r))
    write_csv(ROOT/'five_rules_holdout.csv', rows)


def main():
    audit, screen, verify, factorial = map(read, ('audit', 'screen', 'verify', 'factorial'))
    # Shapley decomposition of the FULL 2^4 intervention table (not fitted regression).
    factors = ['flow rate 300k -> 600k', 'mean load .95 -> .8', 'T_A .5 -> .1 s', 'T_B 30 -> 60 s']
    shapley = []
    for i, name in enumerate(factors):
        value = 0.
        for bits in itertools.product((0, 1), repeat=4):
            if bits[i]:
                continue
            other = list(bits)
            other[i] = 1
            k = sum(bits)
            weight = math.factorial(k)*math.factorial(3-k)/math.factorial(4)
            a, b = 'factor_'+''.join(map(str, bits)), 'factor_'+''.join(map(str, other))
            value += weight*(factorial[b]['width_ms'] - factorial[a]['width_ms'])
        shapley.append(dict(name=name, contribution_ms=value))
    assert abs(sum(r['contribution_ms'] for r in shapley) - (factorial['factor_1111']['width_ms']-factorial['factor_0000']['width_ms'])) < 1e-10
    write_csv(ROOT/'factor_attribution.csv', shapley)

    for dataset in (audit, screen, verify, factorial):
        for r in dataset.values():
            assert abs(r['width_ms'] - r['disagree_rate']*r['per_disagree_ms']) < 1e-9
            assert abs(r['width_ms'] - r['k2_only_rate']*r['k2_only_mean_ms'] + r['sc_only_rate']*r['sc_only_mean_ms']) < 1e-9
    for field in ('width_ms', 'headroom', 'gain_SC', 'gain_K2', 'oos_width_ms'):
        assert abs(verify['similarity_16'][field] - 16*verify['base_m069'][field]) < 1e-7

    plt.rcParams.update({'font.size': 10})
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    names = ['base_m069', 'joint_small', 'quietB', 'joint_medium', 'joint_large', 'joint_large_tau30']
    labels = ['Original', 'Joint, K=83', 'Quiet B, K=83', 'Joint, K=332', 'Joint, K=664', 'Joint, K=664, tau=30']
    x = np.arange(len(names))
    y = np.array([verify[n]['width_ms'] for n in names])
    lo = y - np.array([verify[n]['width_lo'] for n in names])
    hi = np.array([verify[n]['width_hi'] for n in names]) - y
    ax.errorbar(x, y, yerr=[lo, hi], fmt='o', capsize=4, label='Test-optimized frontier (95% bootstrap CI)')
    oy = np.array([verify[n]['oos_width_ms'] for n in names])
    ol = oy - np.array([verify[n]['oos_width_lo'] for n in names])
    oh = np.array([verify[n]['oos_width_hi'] for n in names]) - oy
    ax.errorbar(x+.13, oy, yerr=[ol, oh], fmt='s', capsize=3, label='Calibration-fit policies (95% paired t CI)')
    ax.axhline(8.1, color='red', linestyle='--', label='Old delay SESOI 8.1 ms')
    ax.set_xticks(x, labels, rotation=24, ha='right')
    ax.set_ylabel('K2 - SC, ms per decision')
    ax.set_title('Fresh holdout: effect and physical scenario change')
    ax.legend(fontsize=7)
    ax = axes[0, 1]
    for ns, label in [(['base_m069', 'buffer_166', 'buffer_332', 'buffer_664'], 'Buffer only (screen)'),
                      (['joint_small', 'joint_medium', 'joint_large'], 'Joint mechanism (holdout)')]:
        data = screen if label.startswith('Buffer') else verify
        ax.plot([data[n]['buffer_ms'] for n in ns], [data[n]['width_ms'] for n in ns], 'o-', label=label)
    ax.set_xlabel('Buffer time K*S, ms')
    ax.set_ylabel('Matched frontier width, ms')
    ax.set_title('Larger headroom has a queue-delay cost')
    ax.legend()
    ax = axes[1, 0]
    ax.barh([r['name'] for r in shapley], [r['contribution_ms'] for r in shapley])
    ax.set_xlabel('Shapley contribution to width increase, ms')
    ax.set_title('4-factor attribution at original 100 ms buffer\nExploration seeds; interactions averaged over all orders')
    ax = axes[1, 1]
    n = 'm069'
    r = audit[n]
    vals = [r['k2_only_rate']*r['k2_only_mean_ms'], -r['sc_only_rate']*r['sc_only_mean_ms'], r['width_ms']]
    ax.bar(['K2-only contribution', 'SC-only subtracted', 'Net width'], vals, color=['#228833', '#cc6677', '#4477aa'])
    for i, v in enumerate(vals):
        ax.text(i, v, f'{v:+.3f}', ha='center', va='bottom' if v >= 0 else 'top')
    ax.axhline(0, color='black', linewidth=.6)
    ax.set_ylabel('ms per ALL decisions')
    ax.set_title('Why original m069 is small: few changed decisions\nDisagreement = 4.855%; net per disagreement = 13.34 ms')
    fig.savefig(ROOT/'width_mechanisms.png', dpi=180)
    fig.savefig(ROOT/'width_mechanisms.pdf')
    plt.close(fig)
    five_rules()
    print('Verified decomposition and exact x16 scaling; saved attribution, figures and five-rule comparison.')


if __name__ == '__main__':
    main()
