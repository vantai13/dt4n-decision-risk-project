import numpy as np
import pytest
from scipy.integrate import dblquad

from experiments.scan.check_telemetry_fit import synthetic_observations
from experiments.scan.telemetry_fit import (FreshSeries, box_variance, empirical_moments,
                                           estimate, fit_covariances, fresh_series, window_covariance)


def test_covariance_matches_integral_of_ou_kernel():
    T, sig, tau = 2., .2, 7.
    for k in (1, 3):
        integral = dblquad(lambda v, u: sig**2*np.exp(-(v-u)/tau), 0, T,
                           lambda u: k*T, lambda u: (k+1)*T)[0] / T**2
        assert abs(window_covariance([k], T, sig, tau)[0] - integral) < 1e-12


def test_small_window_variance_is_stable():
    assert abs(box_variance(1e-8, .2, 100.) / .2**2 - 1.) < 1e-9


@pytest.mark.parametrize('T,tau', [(1., 15.), (1., 60.), (10., 120.)])
def test_exact_covariances_recover_sigma_and_tau(T, tau):
    lags = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256])
    sig, fit_tau, warn = fit_covariances(lags, window_covariance(lags, T, .14, tau),
                                       np.full(len(lags), 10000), T)
    assert abs(sig/.14 - 1.) < 1e-6
    assert abs(fit_tau/tau - 1.) < 1e-6
    assert not warn


def test_fresh_extraction_uses_timestamp_not_value_and_preserves_gaps():
    s = fresh_series([.8, .8, .8, .8, .8], [.1, 1.1, 2.1, .1, .1],
                     [1.1, 2.1, 3.1, 4.1, 5.1], 1.)
    np.testing.assert_array_equal(s.ticks, [0, 3, 4])
    assert len(s.values) == 3  # Hai giá trị bằng nhau vẫn là hai bản tin khác nhau.


def test_covariance_pairs_do_not_bridge_seeds_or_compress_outages():
    a = FreshSeries(np.array([0, 1, 4]), np.array([1., 2., 3.]), 3, 0)
    b = FreshSeries(np.array([0, 1, 4]), np.array([4., 5., 6.]), 3, 0)
    _, _, _, counts = empirical_moments([a, b], [1, 2, 3])
    np.testing.assert_array_equal(counts, [2, 0, 2])


def test_irregular_timestamps_fail_instead_of_assuming_equal_spacing():
    with pytest.raises(ValueError, match='lưới T'):
        fresh_series([.8, .9, .7], [.1, .1, .1], [1.1, 2.5, 3.1], 1.)


def test_insufficient_or_unidentifiable_data_fail():
    with pytest.raises(ValueError, match='>=3 lag'):
        fit_covariances([1, 2], [.1, .05], [200, 200], 1.)
    with pytest.raises(ValueError, match='>=3 lag'):
        fit_covariances([1, 2, 3], [-.1, -.05, -.02], [200]*3, 1.)


def test_synthetic_poisson_with_missing_data_and_no_oracle_input():
    obs = synthetic_observations(np.random.default_rng([20261001, 42, 0]),
                                 100000, .8, .14, 60., 1., .0006048)
    fit = estimate([obs], 1., .0006048)
    assert abs(fit.rho_bar-.8) < .02
    assert abs(fit.sigma/.14-1.) < .15
    assert abs(fit.tau/60.-1.) < .2
    # Delay/true-parameter extras must not influence a fit.
    obs.update(D=np.array([-999.]), rho=99., sigma=99., tau=99.)
    assert estimate([obs], 1., .0006048) == fit


def test_bad_physical_inputs_and_duplicate_lags_fail():
    with pytest.raises(ValueError, match='service_time_s'):
        estimate([], 1., 0.)
    with pytest.raises(ValueError, match='riêng biệt'):
        fit_covariances([1, 1, 2], [.1]*3, [200]*3, 1.)
