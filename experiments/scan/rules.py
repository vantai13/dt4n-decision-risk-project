"""Luật đổi/giữ và cách tune chúng dưới CÙNG một ngân sách harm α."""
import numpy as np


def s0_trajectory(Iplug_A, h):
    """Quỹ đạo của luật cố định S0 (đổi nếu Î_plug > h)."""
    cur = np.empty(len(Iplug_A), dtype=bool)
    on_a = True
    for k, x in enumerate(Iplug_A):
        cur[k] = on_a
        if (x if on_a else -x) > h:
            on_a = not on_a
    return cur


def orient(d, cur_a):
    """Đổi dữ liệu sang góc nhìn đường hiện tại so với đường còn lại."""
    sgn = np.where(cur_a, 1.0, -1.0)
    return dict(Iplug=sgn * d["Iplug_A"], Ibar=sgn * d["Ibar_A"], I=sgn * d["I_A"],
                pdn=np.where(cur_a, d["pdn_A"], d["pup_A"]),
                age=np.maximum(d["age_A"], d["age_B"]))


def _cut(sorted_scores, j):
    s = sorted_scores
    return 0.5 * (s[j] + s[j + 1]) if j + 1 < len(s) else s[j] - 1e-9


def tune_threshold(score, gain, harm, alpha):
    order = np.argsort(-score)
    cg, ch = np.cumsum(gain[order]), np.cumsum(harm[order])
    ok = ch <= alpha * len(score)
    if not ok.any():
        return np.inf
    j = int(np.argmax(np.where(ok, cg, -np.inf)))
    return _cut(score[order], j) if cg[j] > 0 else np.inf


def tune_bucket_thresholds(score, bucket, gain, harm, alpha, n_bucket):
    def best_for(lam):
        th, h_tot = np.full(n_bucket, np.inf), 0.0
        for b in range(n_bucket):
            m = bucket == b
            if not m.any():
                continue
            order = np.argsort(-score[m])
            val = np.cumsum((gain[m] - lam * harm[m])[order])
            j = int(np.argmax(val))
            if val[j] > 0:
                th[b] = _cut(score[m][order], j)
                h_tot += np.cumsum(harm[m][order])[j]
        return th, h_tot

    budget = alpha * len(score)
    th, h_tot = best_for(0.0)
    if h_tot <= budget:
        return th
    lo, hi = 0.0, 1e6
    for _ in range(60):
        lam = 0.5 * (lo + hi)
        lo, hi = (lam, hi) if best_for(lam)[1] > budget else (lo, lam)
    return best_for(hi)[0]


def tune_lambda(Ibar, pdn, alpha):
    budget = alpha * len(Ibar)
    if pdn[Ibar > 0].sum() <= budget:
        return 0.0
    lo, hi = 0.0, 1e6
    for _ in range(80):
        lam = 0.5 * (lo + hi)
        lo, hi = (lam, hi) if pdn[Ibar - lam * pdn > 0].sum() > budget else (lo, lam)
    return hi
