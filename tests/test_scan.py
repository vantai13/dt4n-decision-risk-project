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


# ---------- Phần xác nhận (DES + tune bằng hại thật) ----------
from experiments.scan.des_world import simulate_world_des            # noqa: E402
from experiments.scan.rules import tune_lambda_realized              # noqa: E402
from ndtrisk.theory.mdk import mdk                                   # noqa: E402


def test_des_matches_mdk_under_constant_load():
    p = dict(rho_bar=0.8, sigma=1e-6, tau=10.0, T_tel=0.5, d=0.1, stall_p=0.0, stall_mean=0.0)
    w = simulate_world_des(7, dict(mbps=4, k=11, H=0.5, a=0.05, n_epochs=20000, A=p, B=p))
    D = np.concatenate([w["A"]["D_des"], w["B"]["D_des"]])
    assert abs(D.mean() / (mdk(0.8, 11).sojourn * S4_MS) - 1) < 0.03       # DES khớp nghiệm M/D/1/K
    assert abs(w["A"]["rhohat"].mean() - 0.8) < 0.005                     # telemetry đếm gói không lệch


def test_realized_lambda_respects_budget():
    rng = np.random.default_rng(2)
    Ibar, pdn = rng.normal(0.5, 2.0, 40_000), rng.uniform(0, 0.5, 40_000)
    I = Ibar + rng.normal(0, 2.0, 40_000)
    harm = (I < -0.5).astype(float)
    lam = tune_lambda_realized(Ibar, pdn, I, harm, 0.01)
    assert harm[Ibar - lam * pdn > 0].sum() <= 0.01 * len(I)              # hại THẬT không vượt ngân sách
