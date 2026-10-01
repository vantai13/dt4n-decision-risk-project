import copy
import json
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from experiments.scan import rollout_v6 as v6
from experiments.scan.check_telemetry_fit import synthetic_observations


def scenario():
    path = dict(mbps=20.,k=10,T_tel=1.,d=.1,rho=.8,sigma=.14,tau=60.)
    return dict(name='synthetic_only',H=1.,a=.05,eps_ms=1.,A=path.copy(),B=path.copy())


def test_twin_config_copies_and_replaces_every_true_parameter():
    sc = scenario()
    before = copy.deepcopy(sc)
    fits = {q: SimpleNamespace(rho_bar=.7,sigma=.1,tau=12.) for q in 'AB'}
    tw = v6.twin_config(sc,fits)
    assert sc == before
    assert tw is not sc and tw['A'] is not sc['A']
    for q in 'AB':
        assert (tw[q]['rho'],tw[q]['sigma'],tw[q]['tau']) == (.7,.1,12.)
        assert all(tw[q][k] == sc[q][k] for k in ('mbps','k','T_tel','d'))


def test_full_telemetry_to_twin_blind_to_true_params_bit_exact():
    sc = scenario()
    obs = [synthetic_observations(np.random.default_rng([20261001,66,i]),
                                  2048,.8,.14,10.,1.,.0006048) for i in (0,1)]
    raw = dict(A=dict(rhohat=obs[0]['rhohat'],age=obs[0]['age']),
               B=dict(rhohat=obs[1]['rhohat'],age=obs[1]['age']),
               decision_times=obs[0]['decision_times'])
    fits = v6.calibration_fits([raw],sc,n=2048)
    original = v6.decisions_from_telemetry(raw,sc,fits)
    poisoned = copy.deepcopy(sc)
    for q in 'AB':
        poisoned[q].update(rho=float('nan'),sigma=999.,tau=-1.)
    new_fits = v6.calibration_fits([raw],poisoned,n=2048)
    assert new_fits == fits
    changed = v6.decisions_from_telemetry(raw,poisoned,new_fits)
    for k in ('Ibar_A','pdn_A','pup_A','Iplug_A'):
        assert np.isfinite(original[k]).all()
        np.testing.assert_array_equal(original[k],changed[k])


def test_twin_does_not_consume_delay_or_future_window_labels():
    sc = scenario()
    fits = {q: SimpleNamespace(rho_bar=.8,sigma=.14,tau=60.) for q in 'AB'}
    t = {q: dict(rhohat=np.array([.7,.8,.9]),age=np.array([.2,2.,30.])) for q in 'AB'}
    before = v6.decisions_from_telemetry(t,sc,fits)
    for q in 'AB':
        t[q].update(D=np.array([999.,-999.,float('nan')]),IW_A='forbidden_future')
    after = v6.decisions_from_telemetry(t,sc,fits)
    for k in ('Ibar_A','pdn_A','pup_A'):
        np.testing.assert_array_equal(before[k],after[k])


def test_calibration_fit_excludes_padding_and_true_parameters():
    raw = {'decision_times':np.arange(8.)}
    for q in 'AB':
        raw[q] = dict(rhohat=np.arange(8.),age=np.zeros(8),D=np.full(8,999.))
    with patch.object(v6,'estimate',return_value='fit') as fit:
        result = v6.calibration_fits([raw],scenario(),n=5)
    assert result == dict(A='fit',B='fit')
    for call in fit.call_args_list:
        obs = call.args[0][0]
        assert set(obs) == {'rhohat','age','decision_times'}
        assert all(len(x) == 5 for x in obs.values())


def test_window_labels_never_shorten_final_commitment():
    np.testing.assert_allclose(v6.full_window_mean(np.arange(34.),5,30),
                               np.arange(5.)+14.5)
    with pytest.raises(ValueError,match='Thiếu padding'):
        v6.full_window_mean(np.arange(5.),5,30)


def test_extended_generator_separates_decisions_and_label_padding():
    def fake(*args):
        times = args[7]
        return dict(rhohat=np.zeros(len(times)),age=np.zeros(len(times)),D=np.zeros(len(times)))
    with patch.object(v6.v2,'des_path_outage',side_effect=fake) as engine:
        raw = v6.simulate_extended(123,scenario(),n=5,hd=3)
    assert len(raw['decision_times']) == 7
    assert len(raw['A']['D']) == 7
    assert engine.call_count == 2


def test_draft_guard_stops_before_any_seed():
    draft = json.dumps(dict(status='draft_awaiting_author_prediction',author_prediction=None))
    with patch.object(v6.Path,'read_text',return_value=draft), \
         patch.object(v6,'simulate_extended') as simulate:
        with pytest.raises(ValueError,match='chưa khoá'):
            v6.main()
    simulate.assert_not_called()


def test_invalid_fit_never_falls_back_to_oracle():
    fits = {q:SimpleNamespace(rho_bar=.8,sigma=0.,tau=60.) for q in 'AB'}
    with pytest.raises(ValueError,match='không fallback'):
        v6.twin_config(scenario(),fits)


def test_validity_classifies_audit_only_vs_unsafe_warnings():
    fits = dict(A=SimpleNamespace(warnings=('old_updates_rejected',)),
                B=SimpleNamespace(warnings=('weak_identification: example',)))
    assert v6.validity_warnings(fits) == dict(B=['weak_identification: example'])


@pytest.mark.parametrize('delta,meaning',[(1.,'K2 tốt hơn'),(0.,'Chưa phân giải'),(-1.,'SClin tốt hơn')])
def test_interpretation_fixed_for_all_ci_outcomes(delta,meaning):
    assert meaning in v6.comparison(np.full(60,delta))['verdict']
