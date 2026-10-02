"""Bảo vệ mẫu số, biên ε, regret và neo telemetry của minh hoạ L1.2."""
import numpy as np
import pytest

from experiments import n01b_three_sandboxes as b
from experiments.n01c_crn_two_branches import S, mean_delay_ms


def test_indifference_boundaries_and_regret_count_different_things():
    I = np.array([-2., -.5, 0., .5, 3.])
    approve = np.array([True, True, False, False, False])
    result = b.score(I, approve, np.ones(5, dtype=bool), .5)
    assert (result['n_harm'], result['n_neutral'], result['n_good']) == (1, 3, 1)
    assert result['false_approval'] == result['false_rejection'] == 1
    # Chi phí trong vùng thờ ơ vẫn là .5+.5 ms, dù không đếm là DN/TCN.
    assert result['regret_ms'] == pytest.approx(6 / 5)
    assert result['harm_given_approval'] == .5


def test_generator_changes_denominators_and_empty_classes_are_undefined():
    I = np.array([-2., -1., 1., 2.])
    approve = np.array([True, False, False, True])
    all_rows = b.score(I, approve, np.ones(4, dtype=bool), .5)
    selected = b.score(I, approve, np.array([True, False, False, True]), .5)
    no_harm = b.score(I, approve, I > 0, .5)
    assert all_rows['false_approval_given_harm'] == .5
    assert selected['false_approval_given_harm'] == 1.
    assert selected['false_rejection_given_good'] == 0.
    assert np.isnan(no_harm['false_approval_given_harm'])
    assert np.isnan(b.score(I, approve, np.zeros(4, dtype=bool), .5)['regret_ms'])


@pytest.mark.parametrize('h', [.5, 5., 30.])
def test_world_anchor_includes_age(h, monkeypatch):
    _, cell = b.controls()
    cell.update(H=h, n_epochs=8)
    world = b.world_with_state(9101, cell)
    reference = b.simulate_world(9101, cell)
    for path in 'AB':
        for field in ('rhohat', 'age', 'G_true'):
            np.testing.assert_array_equal(world[path][field], reference[path][field])
    reference['B']['age'][0] += 1
    monkeypatch.setattr(b, 'simulate_world', lambda *args: reference)
    with pytest.raises(AssertionError, match='age'):
        b.one_seed(9101, cell, None, .5)


def test_crn_null_intervention_and_empty_queue():
    arrivals = np.arange(0., 2.5, S / .85)
    original = arrivals.copy()
    keep = mean_delay_ms(arrivals)
    apply_no_packets = mean_delay_ms(np.sort(np.concatenate([arrivals, []])))
    assert apply_no_packets - keep == 0.
    np.testing.assert_array_equal(arrivals, original)
    assert mean_delay_ms(np.array([])) == S * 1e3
