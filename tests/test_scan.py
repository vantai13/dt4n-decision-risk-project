"""Kiểm nền móng của bộ quét. Chạy: python -m pytest tests/test_scan.py -q"""
import numpy as np

from experiments.scan.rules import s0_trajectory, tune_lambda, tune_threshold
from experiments.scan.twin import DelayCurve, posterior, twin_view, var_box

S4_MS = 1512 * 8 / 4e6 * 1e3


def test_delay_curve_matches_verified_mdk():
    assert abs(float(DelayCurve(11, 1.0)(0.8)) - 2.878) < 1e-3


def test_posterior_reproduces_t06_r2():
    R = 0.95 * S4_MS / 1e3 / 0.5
    _, v = posterior(np.array([0.95]), np.array([0.42]), 0.5, 0.5, 0.95, 0.10, 2.0, R)
    assert abs((1 - v[0] / var_box(0.5, 0.10, 2.0)) - 0.292) < 2e-3


def test_twin_risk_matches_monte_carlo():
    curve, eps, rng = DelayCurve(100, S4_MS), 0.5 * S4_MS, np.random.default_rng(0)
    mA, vA, mB, vB = 0.97, 0.004, 0.93, 0.006
    _, pdn, pup = twin_view(curve, *(np.array([x]) for x in (mA, vA, mB, vB)), eps)
    I = curve(rng.normal(mA, vA**0.5, 400_000)) - curve(rng.normal(mB, vB**0.5, 400_000))
    assert abs(pdn[0] - (I < -eps).mean()) < 0.005 and abs(pup[0] - (I > eps).mean()) < 0.005


def test_rules_coincide_when_risk_is_monotone_in_center():
    rng = np.random.default_rng(1)
    Ibar = rng.normal(0.5, 2.0, 50_000)
    pdn = 1 / (1 + np.exp(3 * Ibar))
    a_fix = Ibar > tune_threshold(Ibar, Ibar, pdn, 0.01)
    a_k2 = Ibar - tune_lambda(Ibar, pdn, 0.01) * pdn > 0
    assert np.mean(a_fix != a_k2) < 1e-3


def test_trajectory_extremes():
    x = np.array([1.0, -1.0, 2.0])
    assert s0_trajectory(x, np.inf).all()
    assert list(s0_trajectory(np.ones(4), 0.5)) == [True, False, False, False]
