"""Tests for the stable M/D/1/K analytical reference."""

import numpy as np
import pytest

from ndtrisk.theory.mdk import mdk

RHOS = [0.1, 0.5, 0.8, 0.95, 0.99, 1.0, 1.05, 1.5]
KS = [1, 2, 11, 100]


@pytest.mark.parametrize("k_sys", KS)
@pytest.mark.parametrize("rho", RHOS)
def test_valid_distribution(rho, k_sys):
    result = mdk(rho, k_sys)
    assert np.all(result.p >= 0)
    assert result.p.sum() == pytest.approx(1.0, abs=1e-12)
    assert 0 <= result.loss < 1
    assert result.wait >= 0


@pytest.mark.parametrize("rho", RHOS)
def test_busy_balance(rho):
    result = mdk(rho, 11)
    assert 1 - result.p[0] == pytest.approx(rho * (1 - result.loss), rel=1e-12)


@pytest.mark.parametrize("rho", [0.3, 0.8, 1.0, 1.5])
def test_closed_forms_k1_k2(rho):
    result_k1 = mdk(rho, 1)
    assert result_k1.loss == pytest.approx(rho / (1 + rho), rel=1e-12)
    assert result_k1.wait == 0.0
    result_k2 = mdk(rho, 2)
    assert result_k2.loss == pytest.approx(1 - 1 / (np.exp(-rho) + rho), rel=1e-12)


@pytest.mark.parametrize(
    "rho, loss, wait",
    [(0.8, 0.00235336842946, 1.878267525), (1.0, 0.0461538461543, 4.836021505)],
)
def test_k11_reference_values(rho, loss, wait):
    result = mdk(rho, 11)
    assert result.loss == pytest.approx(loss, rel=1e-9)
    assert result.wait == pytest.approx(wait, rel=1e-8)


@pytest.mark.parametrize(
    "rho, loss",
    [(0.8, 5.18343592704e-20), (0.5, 3.15295397482e-55), (0.1, 1.120401944e-156)],
)
def test_tiny_loss_stays_positive_and_accurate(rho, loss):
    assert mdk(rho, 100).loss == pytest.approx(loss, rel=1e-8)


@pytest.mark.parametrize("rho", [0.5, 0.8, 0.9])
def test_large_k_converges_to_pollaczek_khinchine(rho):
    assert mdk(rho, 1000).wait == pytest.approx(rho / (2 * (1 - rho)), rel=1e-9)


def test_loss_decreases_with_capacity():
    losses = [mdk(0.9, k_sys).loss for k_sys in (1, 2, 5, 11, 30, 100)]
    assert all(left > right for left, right in zip(losses, losses[1:]))


@pytest.mark.parametrize("rho,k_sys", [(-0.1, 5), (np.inf, 5), (0.5, 0), (0.5, 1.5)])
def test_invalid_input(rho, k_sys):
    with pytest.raises(ValueError):
        mdk(rho, k_sys)


def test_zero_load():
    result = mdk(0.0, 11)
    assert result.loss == 0
    assert result.wait == 0
    assert result.sojourn == 1
    assert result.p[0] == 1
