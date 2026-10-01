import numpy as np

from experiments.scan.strict_frontier import optimum, harm_for_gain, matched


def test_tied_scores_cannot_be_split():
    score = np.array([2., 2., 1.])
    gain = np.array([10., -2., 1.])
    harm = np.array([0., 1., 0.])
    assert optimum(score, gain, harm, 0)['gain'] == 0
    r = optimum(score, gain, harm, 1)
    assert np.array_equal(score > r['threshold'], [True, True, True])
    assert r['gain'] == 9


def test_k2_ineligible_never_selected_and_empty_action_exists():
    score = np.array([2., -np.inf, -np.inf])
    assert optimum(score, np.array([1., 100., 200.]), np.zeros(3), 3)['gain'] == 1
    assert harm_for_gain(score, np.ones(3), np.ones(3), 0) == 0
    assert np.isinf(harm_for_gain(score, np.ones(3), np.ones(3), 2))
    assert optimum(np.full(3, -np.inf), np.ones(3), np.ones(3), 3)['count'] == 0


def test_threshold_optimum_matches_exhaustive_search():
    rng = np.random.default_rng(10)
    for _ in range(30):
        score = rng.integers(-2, 4, 30).astype(float)
        score[0] = -np.inf
        gain = rng.normal(0, 2, 30)
        harm = gain < -0.5
        candidates = [np.inf] + [np.nextafter(s, -np.inf) for s in np.unique(score[np.isfinite(score)])]
        expected = max(gain[score > t].sum() for t in candidates if harm[score > t].sum() <= 3)
        assert abs(optimum(score, gain, harm, 3)['gain'] - expected) < 1e-12


def test_disagreement_decomposition():
    o = dict(I=np.array([4., 2., -1., 3.]), Ibar=np.array([2., 3., 1., -1.]),
             Iplug=np.array([2., 3., 1., -1.]), pdn=np.array([.01, .2, .4, .5]))
    r = matched(o, .25, .5)
    assert abs(r['width_ms'] - (r['k2_only_rate']*r['k2_only_mean_ms'] - r['sc_only_rate']*r['sc_only_mean_ms'])) < 1e-12


def test_physical_time_similarity_of_des():
    from copy import deepcopy
    from experiments.scan.des_world import simulate_world_des
    from experiments.scan.grid import make_cell
    c = make_cell('test', r_f=300e3, tau=10., T_tel_A=.5, probe_B=30., rho_B=.95, alpha=.002)
    c['n_epochs'] = 100
    scaled = deepcopy(c)
    q = 4.
    scaled['mbps'] /= q
    scaled['H'] *= q
    scaled['a'] *= q
    for path in ('A', 'B'):
        for key in ('tau', 'T_tel', 'd', 'stall_mean'):
            scaled[path][key] *= q
    w, ws = simulate_world_des(8, c), simulate_world_des(8, scaled)
    for path in ('A', 'B'):
        np.testing.assert_allclose(ws[path]['D_des'], q*w[path]['D_des'], rtol=1e-10, atol=1e-9)
        np.testing.assert_allclose(ws[path]['rhohat'], w[path]['rhohat'], rtol=1e-12)
        np.testing.assert_allclose(ws[path]['age'], q*w[path]['age'], rtol=1e-12)
