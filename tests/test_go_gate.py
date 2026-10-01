from experiments.scan.go_test import actual_harm_ratio, verdict, TWIN_ERRORS


def test_ratio_uses_actual_sc_harm_and_zero_harm_is_not_reduction():
    assert actual_harm_ratio(.004, .005) == .8
    assert actual_harm_ratio(0., 0.) == float('inf')


def test_go_at_second_alpha_beats_conditional_at_first():
    rows = [dict(name='R', twin=e, alpha=a, eps=1., passed=(a==.002 or e=='đúng'), oos_lo=.1)
            for a in (.01, .002) for e in TWIN_ERRORS]
    assert verdict(rows, 'R') == ('GO', .002, .1)


def test_extra_epsilon_and_incomplete_variants_cannot_produce_go():
    rows = [dict(name='R', twin='đúng', alpha=.01, eps=1., passed=True, oos_lo=.1)]
    rows += [dict(name='R', twin=e, alpha=.002, eps=8.1, passed=True, oos_lo=9.) for e in TWIN_ERRORS]
    assert verdict(rows, 'R')[0].startswith('GO CÓ ĐIỀU KIỆN')
    assert verdict([], 'R')[0] == 'NO-GO'
