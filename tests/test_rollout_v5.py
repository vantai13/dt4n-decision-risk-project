import numpy as np

from experiments.scan import rollout_v5 as v5


def test_window_mean_forward_and_explicit_short_tail():
    np.testing.assert_allclose(v5.window_mean(np.array([1., 2., 3., 4.]), 3),
                               [2., 3., 3.5, 4.])


def test_pick_uses_window_harm_not_one_second_harm():
    r = dict(delay=np.array([[1., 2., 3.]]), harmW=np.array([[.01, .001, 0.]]),
             harm1=np.array([[0., .5, .5]]))
    assert v5.pick(r, .002) == (1, 2.)
    assert v5.pick(r, np.inf) == (0, 1.)


def test_window_harm_can_differ_from_instant_harm():
    n = 4
    z, one = np.zeros(n), np.ones(n)
    # Đổi A→B ở e=0 lợi ngay 2 ms, nhưng trung bình cam kết bị hại 2 ms.
    DA, DB, IW = np.full(n, 3.), one, np.full(n, -2.)
    result = v5.rollout(one*3, one*3, one*.01, one*.01, z, z, one*.8, one*.8,
                        DA, DB, IW, 1., np.array([1]), np.array([0.]), np.array([0.]),
                        np.zeros((1, 24)), v5.A_EDGES, v5.R_EDGES, 30)
    assert result[0][0] == 4.
    assert result[1][0] == 0.
    assert result[2][0] == 1.
    assert result[3][0] == 1.


def test_sclin_penalizes_destination_age():
    n = 3
    z, one = np.zeros(n), np.ones(n)
    result = v5.rollout(one*5, one*5, one*.01, one*.01, z, one*10, one*.8, one*.8,
                        one*3, one, one*2, 1., np.array([3]), np.array([0.]), np.array([.5]),
                        np.zeros((1, 24)), v5.A_EDGES, v5.R_EDGES, 30)
    assert result[3][0] == 0.  # score=5−0.5*10=0; ngưỡng 0, so sánh ngặt.


def test_policy_equality_checks_every_parameter_and_cell():
    a = (1, 0., 0., np.zeros(24))
    b = (1, 0., 0., np.zeros(24))
    assert v5.same_policy(a, b)
    b[3][23] = 1.
    assert not v5.same_policy(a, b)
