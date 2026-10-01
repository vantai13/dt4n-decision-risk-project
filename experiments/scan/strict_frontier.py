"""Exact deterministic score-threshold families, with ties and no-action handled.

K2 scores use -inf for ineligible Ibar <= 0; those entries never enter a prefix.
All summaries normalize by ALL decisions, including ineligible ones.
"""
import numpy as np


def ranking_scores(o):
    ratio = np.full(len(o['Ibar']), -np.inf)
    positive = o['Ibar'] > 0
    ratio[positive] = o['Ibar'][positive] / np.maximum(o['pdn'][positive], 1e-300)
    return {'S0': o['Iplug'], 'SC': o['Ibar'], 'K2': ratio}


def prefixes(score, gain, harm):
    score, gain, harm = map(np.asarray, (score, gain, harm))
    if not (score.shape == gain.shape == harm.shape):
        raise ValueError('shape mismatch')
    if np.isnan(score).any() or np.isposinf(score).any():
        raise ValueError('scores must be finite or -inf (ineligible)')
    order = np.flatnonzero(np.isfinite(score))
    order = order[np.argsort(-score[order], kind='stable')]
    s = score[order]
    ends = np.flatnonzero(np.r_[s[:-1] != s[1:], True]) if len(s) else np.array([], dtype=int)
    cg = np.r_[0., np.cumsum(gain[order])[ends]]
    ch = np.r_[0., np.cumsum(harm[order])[ends]]
    count = np.r_[0, ends + 1]
    # Threshold just below included score: includes the ENTIRE tie group.
    thresholds = np.r_[np.inf, np.nextafter(s[ends], -np.inf)]
    return cg, ch, count, thresholds


def optimum(score, gain, harm, budget):
    cg, ch, count, thresholds = prefixes(score, gain, harm)
    j = int(np.argmax(np.where(ch <= budget, cg, -np.inf)))
    return dict(gain=float(cg[j]), harm=float(ch[j]), count=int(count[j]), threshold=float(thresholds[j]))


def harm_for_gain(score, gain, harm, target):
    if target <= 0:
        return 0.
    cg, ch, _, _ = prefixes(score, gain, harm)
    ok = cg >= target
    return float(ch[ok].min()) if ok.any() else np.inf


def matched(o, alpha, eps_ms):
    n = len(o['I'])
    harmful = o['I'] < -eps_ms
    s = ranking_scores(o)
    opt = {r: optimum(v, o['I'], harmful, alpha*n) for r, v in s.items()}
    a = {r: s[r] > opt[r]['threshold'] for r in s}
    out = {'headroom': float(np.maximum(o['I'], 0).mean())}
    for r in s:
        for k in ('gain', 'harm', 'count'):
            out[f'{k}_{r}'] = opt[r][k]/n
    out['width_ms'] = out['gain_K2'] - out['gain_SC']
    out['width_pct'] = 100*out['width_ms']/out['headroom'] if out['headroom'] else 0.
    out['harm_ratio'] = harm_for_gain(s['K2'], o['I'], harmful, opt['SC']['gain'])/(alpha*n)
    only_k = a['K2'] & ~a['SC']
    only_c = a['SC'] & ~a['K2']
    out['k2_only_rate'], out['sc_only_rate'] = float(only_k.mean()), float(only_c.mean())
    out['k2_only_mean_ms'] = float(o['I'][only_k].mean()) if only_k.any() else 0.
    out['sc_only_mean_ms'] = float(o['I'][only_c].mean()) if only_c.any() else 0.
    out['disagree_rate'] = float((only_k | only_c).mean())
    out['per_disagree_ms'] = out['width_ms']/out['disagree_rate'] if out['disagree_rate'] else 0.
    out['k2_calibrated_risk_on_selected'] = float(o['pdn'][a['K2']].mean()) if a['K2'].any() else 0.
    out['k2_actual_risk_on_selected'] = float(harmful[a['K2']].mean()) if a['K2'].any() else 0.
    return out
