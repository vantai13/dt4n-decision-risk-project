"""Evaluate the K2 rule on the three preregistered toy worlds.

The author confirmed completing the derivations externally and requested this
implementation from the lesson pseudocode. This is a theory check, not an RQ result.
"""

import numpy as np
from scipy.stats import norm

EPS, ALPHA, C, N = 0.5, 0.01, 0.0, 400_000


def world(kind, seed):
    """Return (i_bar, s, p_minus) for a preregistered toy world."""
    rng = np.random.default_rng(seed)
    if kind == "A":
        i_bar = rng.normal(0.5, 2.0, N)
        s = np.exp(rng.normal(0.0, 0.7, N))
    elif kind == "B":
        i_bar = rng.normal(0.5, 2.0, N)
        s = 0.3 + 0.5 * np.abs(i_bar)
    elif kind == "C":
        i_bar = rng.normal(0.0, 0.3, N)
        s = np.full(N, 0.05)
    else:
        raise ValueError(f"Thế giới không hợp lệ: {kind}")
    p_minus = norm.cdf((-EPS - i_bar) / s)
    return i_bar, s, p_minus


def gain(action, i_bar, c=C):
    """Expected net milliseconds per epoch, including epochs that stay."""
    return float(np.mean(action * (i_bar - c)))


def harm(action, p_minus):
    """Expected harmful-switch probability per epoch."""
    return float(np.mean(action * p_minus))


def static_best(i_bar, p_minus, alpha, c=C):
    """Return the exact best threshold action via sorting and prefix sums."""
    order = np.argsort(i_bar)[::-1]
    useful = i_bar[order] > c
    cumulative_harm = np.cumsum(p_minus[order])
    feasible = useful & (cumulative_harm <= alpha * len(i_bar))
    n_selected = int(np.count_nonzero(feasible))
    action = np.zeros(len(i_bar), dtype=bool)
    action[order[:n_selected]] = True
    return action


def k2_rule(i_bar, p_minus, alpha, c=C):
    """Return action and smallest feasible nonnegative Lagrange multiplier."""
    unconstrained = i_bar > c
    if harm(unconstrained, p_minus) <= alpha:
        return unconstrained, 0.0

    def action_at(lam):
        return i_bar - c - lam * p_minus > 0

    low, high = 0.0, 1.0
    while harm(action_at(high), p_minus) > alpha:
        high *= 2.0
    for _ in range(100):
        middle = (low + high) / 2.0
        if harm(action_at(middle), p_minus) <= alpha:
            high = middle
        else:
            low = middle
    return action_at(high), high


def headroom(i_bar, s, c=C):
    """Return E[(I-c)+] averaged over epochs for Gaussian I|F."""
    mean = i_bar - c
    z = mean / s
    return float(np.mean(s * norm.pdf(z) + mean * norm.cdf(z)))


if __name__ == "__main__":
    expected = {
        "A": (0.8616, 0.9568, 9.91, 0.0952),
        "B": (0.9435, 0.9435, 38.90, 0.0),
        "C": (0.1193, 0.1193, 0.0, 0.0),
    }
    print(
        f"{'world':>5} | {'static':>8} {'K2':>8} {'lambda':>8} {'gap':>8} | "
        f"{'harm S':>8} {'harm K2':>8} {'switch S':>8} {'switch K2':>9} | "
        "adapt safety info headroom"
    )
    for kind, seed in (("A", 9101), ("B", 9102), ("C", 9103)):
        i_bar, s, p_minus = world(kind, seed)
        static = static_best(i_bar, p_minus, ALPHA)
        adaptive, lam = k2_rule(i_bar, p_minus, ALPHA)
        static_gain, adaptive_gain = gain(static, i_bar), gain(adaptive, i_bar)
        unconstrained_gain = float(np.mean(np.maximum(i_bar - C, 0)))
        perfect_gain = headroom(i_bar, s)
        gap = adaptive_gain - static_gain
        adaptation = gap
        safety = unconstrained_gain - adaptive_gain
        information = perfect_gain - unconstrained_gain

        assert harm(static, p_minus) <= ALPHA + 1e-12
        assert harm(adaptive, p_minus) <= ALPHA + 1e-12
        if kind == "C":
            assert lam == 0
        if kind == "B":
            assert np.array_equal(static, adaptive)
        all_budget, all_lam = k2_rule(i_bar, p_minus, 1.0)
        assert all_lam == 0 and np.array_equal(all_budget, i_bar > C)
        assert static_gain <= adaptive_gain + 1e-12
        assert adaptive_gain <= unconstrained_gain + 1e-12
        assert unconstrained_gain <= perfect_gain + 1e-12
        reference_static, reference_k2, reference_lam, reference_gap = expected[kind]
        assert abs(static_gain - reference_static) <= 0.002
        assert abs(adaptive_gain - reference_k2) <= 0.002
        assert abs(gap - reference_gap) <= 0.002
        assert abs(lam - reference_lam) <= 0.02  # bảng chỉ báo lambda đến 0,01 ms

        print(
            f"{kind:>5} | {static_gain:8.4f} {adaptive_gain:8.4f} {lam:8.2f} {gap:8.4f} | "
            f"{harm(static,p_minus):8.5f} {harm(adaptive,p_minus):8.5f} "
            f"{static.mean():8.4f} {adaptive.mean():9.4f} | "
            f"{adaptation:.4f} {safety:.4f} {information:.4f} {perfect_gain:.4f}"
        )
    print("Tự kiểm: 6/6 nhóm đạt; alpha=100% trùng từng epoch với Î>0.")
