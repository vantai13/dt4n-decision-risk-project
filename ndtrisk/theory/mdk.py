"""Stable stationary solution of M/D/1/K in service-time units.

Theory and provenance are documented in ``notes/theory/T1_queue.md``.  The
implementation was checked against the AI-provided reference after the author
confirmed completing the required derivations outside the repository.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import poisson

_Q_DIRECT_MIN = 1e-4
_TAIL_REL_TOL = 1e-17
_N_MAX = 200_000


@dataclass(frozen=True)
class MDKResult:
    """Stationary M/D/1/K metrics; time fields use service time S = 1."""

    rho: float
    k_sys: int
    loss: float
    wait: float
    sojourn: float
    p: np.ndarray


def _cut_weights(rho: float, n_states: int) -> np.ndarray:
    """Return unnormalised embedded-chain weights from positive cut equations."""
    a0 = np.exp(-rho)
    tail = poisson.sf(np.arange(n_states), rho)
    weights = np.empty(n_states)
    weights[0] = 1.0
    for n in range(n_states - 1):
        up_flow = weights[0] * tail[n] + np.dot(weights[1 : n + 1], tail[n:0:-1])
        weights[n + 1] = up_flow / a0
    return weights


def _tail_prob(rho: float, k_sys: int) -> float:
    """Compute Q=P_inf(N>=K), rho<1, by summing only positive terms."""
    n_states = 2 * k_sys + 50
    while True:
        tail = (1.0 - rho) * _cut_weights(rho, n_states)[k_sys:]
        tail_sum = tail.sum()
        if tail[-1] <= _TAIL_REL_TOL * tail_sum:
            return float(tail_sum)
        if n_states >= _N_MAX:
            raise RuntimeError(f"Đuôi chưa hội tụ ở rho={rho}, K={k_sys}")
        n_states = min(2 * n_states, _N_MAX)


def mdk(rho: float, k_sys: int) -> MDKResult:
    """Return the stationary M/D/1/K solution.

    ``rho`` is offered load ``lambda*S`` and ``k_sys`` includes the packet in
    service. Loss is the blocking probability seen by Poisson arrivals.
    """
    if not (isinstance(k_sys, (int, np.integer)) and k_sys >= 1):
        raise ValueError("k_sys phải là số nguyên >= 1")
    if not (np.isfinite(rho) and rho >= 0):
        raise ValueError("rho phải hữu hạn và >= 0")
    if rho == 0:
        p = np.zeros(k_sys + 1)
        p[0] = 1.0
        return MDKResult(0.0, int(k_sys), 0.0, 0.0, 1.0, p)

    weights = _cut_weights(rho, k_sys)
    weight_sum = float(weights.sum())
    if rho >= 1:
        loss = (1.0 + (rho - 1.0) * weight_sum) / (1.0 + rho * weight_sum)
    else:
        q_direct = 1.0 - (1.0 - rho) * weight_sum
        q = q_direct if q_direct > _Q_DIRECT_MIN else _tail_prob(rho, k_sys)
        loss = (1.0 - rho) * q / (1.0 - rho * q)

    pi = weights / weight_sum
    p = np.append(pi * (1.0 - loss), loss)
    queue_length = float(np.dot(np.arange(k_sys), p[1:]))
    wait = queue_length / (rho * (1.0 - loss))
    return MDKResult(float(rho), int(k_sys), float(loss), wait, wait + 1.0, p)
