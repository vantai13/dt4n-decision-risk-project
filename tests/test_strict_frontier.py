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
