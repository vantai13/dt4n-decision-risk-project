import numpy as np
from experiments.scan.go_switch import fit, act, GO_SWITCH


def test_fit_respects_both_budgets_and_cost():
    rng = np.random.default_rng(4)
    o = dict(Ibar=rng.normal(3, 4, 1000), pdn=rng.uniform(.001,.4,1000))
    o['I'] = o['Ibar'] + rng.normal(0,3,1000)
    for rule in ('SC','K2'):
        params = fit(o, 1., .01, .03, 5., rule)
        a = act(o, rule, params)
        assert a.sum() <= 30
        assert (a & (o['I'] < -1)).sum() <= 10
        assert (o['I'][a]-5).sum() >= -1e-9


def test_empty_policy_when_all_net_gains_negative():
    o = dict(Ibar=np.ones(10), pdn=np.ones(10)*.1, I=np.ones(10))
    for rule in ('SC','K2'):
        assert not act(o, rule, fit(o,1.,.01,.1,5.,rule)).any()


def test_gate_requires_switch_rate_and_harm_caps():
    r=dict(lo=.1,d=.2,g_SC=1.,sw_SC=.02,sw_K2=.03,H=1.,h_SC=.001,h_K2=.001)
    assert GO_SWITCH(r,.002,30.)
    assert not GO_SWITCH(dict(r,sw_K2=.041),.002,30.)
    assert not GO_SWITCH(dict(r,h_K2=.0031),.002,30.)
