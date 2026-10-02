"""Kiểm tương tác/Shapley, ghép theo seed và công tắc thông tin L1.3."""
import itertools

import numpy as np
import pytest

from experiments import n02_source_factorial as f
from experiments import n02b_measurement_split as split


def test_shapley_allocates_pair_and_triple_interactions():
    reg = {(s,m,p): np.array([1.,10.,100.]) + 2*s+3*m+5*p-1.2*s*m+.9*s*p+.6*s*m*p
           for s,m,p in itertools.product((0,1),repeat=3)}
    result=f.contrasts(reg)
    np.testing.assert_allclose(result['interaction:S*M|P=0'], -1.2)
    np.testing.assert_allclose(result['interaction:S*M|P=1'], -.6)
    np.testing.assert_allclose(result['interaction:S*M*P'], .6)
    for name,value in [('S',2.05),('M',2.6),('P',5.65)]:
        np.testing.assert_allclose(result[f'shapley:{name}'],value)
    for order in itertools.permutations('SMP'):
        np.testing.assert_allclose(sum(result[f"ladder:{''.join(order)}:{x}"] for x in order), 10.3)


def test_additive_sources_have_no_order_effect_or_spurious_seed_variance():
    reg={(s,m,p):np.array([1.,10.,100.])+2*s+3*m+5*p for s,m,p in itertools.product((0,1),repeat=3)}
    result=f.contrasts(reg)
    for order in itertools.permutations('SMP'):
        for name,value in [('S',2),('M',3),('P',5)]:
            np.testing.assert_array_equal(result[f"ladder:{''.join(order)}:{name}"], np.full(3,value))
    for name,values in result.items():
        if name.startswith('interaction:'):
            np.testing.assert_array_equal(values,np.zeros(3))


@pytest.fixture
def fixture_world():
    _,cell=f.controls()
    cell['n_epochs']=12
    return cell,f.world(9101,cell)


def test_staleness_changes_endpoint_and_keeps_actuation_delay(fixture_world):
    cell,w=fixture_world
    digest=f.world_digest(w)
    for path in 'AB':
        p,ww=cell[path],w[path]
        for stale in (0,1):
            rh,gap,width,noise=f.twin_info(ww,p,cell,stale,0)
            end=ww['r_last'] if stale else ww['t_dec']
            np.testing.assert_array_equal(rh,np.interp(end,ww['tt'],ww['rho']))
            np.testing.assert_array_equal(gap,ww['t_dec']-end+cell['a'])
            assert width==1e-6 and noise==0
    assert f.world_digest(w)==digest


@pytest.mark.parametrize('stale', [0,1])
@pytest.mark.parametrize('mode,m_on', [('inst',0),('noisy',1)])
def test_nested_endpoints_equal_factorial_and_p_off_ignores_wrong_prior(fixture_world,stale,mode,m_on):
    cell,w=fixture_world
    curve,s_ms=f.get_curve(cell)
    eps=cell['eps_over_s']*s_ms
    first=f.regret_of((stale,m_on,0),w,cell,curve,eps,.80)
    second=f.regret_of((stale,m_on,0),w,cell,curve,eps,.70)
    nested=split.regret(w,stale,dict(A=mode,B=mode))
    assert first==second==nested


def test_parameter_error_propagates_to_mean_and_count_noise(fixture_world,monkeypatch):
    cell,w=fixture_world
    calls=[]
    old=f.posterior
    def capture(rhohat,gap,W,H,rho_bar,sigma,tau,R):
        calls.append((rho_bar,R))
        return old(rhohat,gap,W,H,rho_bar,sigma,tau,R)
    monkeypatch.setattr(f,'posterior',capture)
    curve,s_ms=f.get_curve(cell)
    before=f.world_digest(w)
    f.regret_of((1,1,1),w,cell,curve,.5*s_ms,.70)
    assert calls[0][0]==cell['A']['rho_bar']
    assert calls[1][0]==.70
    assert calls[1][1]==pytest.approx(.70 * (f.PKT_BITS/(cell['mbps']*1e6)) / cell['B']['T_tel'])
    assert f.world_digest(w)==before
