"""Kiểm closed-loop và đồng nhất hai kernel, không dùng seed DES chính."""
import copy
import unittest
from unittest.mock import mock_open, patch

import numpy as np

from experiments.scan import rollout_v2 as v2
from experiments.scan import rollout_v3 as v3
from experiments.scan import rollout_v4 as v4


class RolloutTests(unittest.TestCase):
    def data(self):
        return dict(Iplug_A=np.array([3., -3., 3., -3., 3., -3.]),
                    Ibar_A=np.array([3., -3., 3., -3., 3., -3.]),
                    pdn_A=np.full(6, .01), pup_A=np.full(6, .01),
                    age_A=np.array([0., 2., 10., 30., 0., 3.]),
                    age_B=np.array([30., 10., 2., 0., 3., 0.]),
                    DA=np.array([5., 1., 5., 1., 5., 1.]),
                    DB=np.array([1., 5., 1., 5., 1., 5.]),
                    rh_A=np.array([.7, .75, .9, .8, .6, 1.]),
                    rh_B=np.array([1., .6, .8, .9, .75, .7]))

    def run_one(self, hd, tab=None, kind=1, data=None):
        return v2.run([self.data() if data is None else data],
                      np.array([kind]), np.array([0.]),
                      np.zeros((1, 8)) if tab is None else tab, 1., hd)

    def test_own_path_and_delay_after_switch(self):
        delay, harm, switches = self.run_one(0)
        self.assertEqual(delay[0, 0], 1.)
        self.assertEqual(harm[0, 0], 0.)
        self.assertEqual(switches[0, 0], 1.)

    def test_hold_down_counts_since_last_actual_switch(self):
        delay, harm, switches = self.run_one(3)
        self.assertEqual(delay[0, 0], 14 / 6)
        self.assertEqual(harm[0, 0], 0.)
        self.assertEqual(switches[0, 0], 2 / 6)

    def test_infinite_threshold_never_switches(self):
        delay, harm, switches = self.run_one(0, np.full((1, 8), np.inf))
        self.assertEqual(delay[0, 0], 3.)
        self.assertEqual(harm[0, 0], 0.)
        self.assertEqual(switches[0, 0], 0.)

    def test_harm_is_per_all_epochs(self):
        d = self.data()
        d['DA'], d['DB'] = d['DB'], d['DA']
        _, harm, switches = self.run_one(0, data=d)
        self.assertEqual(harm[0, 0], 1.)
        self.assertEqual(switches[0, 0], 1.)

    def test_k2_reverses_probability_with_direction(self):
        d = self.data()
        d['pup_A'][:] = 1.
        delay, harm, switches = self.run_one(0, np.full((1, 8), 10.), 2, d)
        self.assertEqual(switches[0, 0], 1 / 6)
        self.assertEqual(delay[0, 0], 3.)

    def test_expanded_table_matches_eight_bucket_kernel(self):
        d = self.data()
        tab8 = np.array([[0., 2., 4., 1., 2., 0., 1., 4.]])
        for hd in (0, 3, 30):
            base = self.run_one(hd, tab8)
            raw = v4.rollout_tab24(d['Ibar_A'], d['age_A'], d['age_B'],
                                  d['rh_A'], d['rh_B'], d['DA'], d['DB'],
                                  np.repeat(tab8, 3, axis=1), v2.AGE_EDGES,
                                  v4.RHO_EDGES, hd)
            for i, j in enumerate((0, 2, 1)):
                np.testing.assert_array_equal(base[i][0], raw[j] / 6)

    def test_twin_horizon_does_not_change_world_or_scenario(self):
        sc = v2.worlds()[0]
        before = copy.deepcopy(sc)
        world = {q: dict(D=np.arange(4.)) for q in 'AB'}
        with patch.object(v3.g, 'decisions', return_value={}) as mock:
            result = v3.twin_for([world], sc, 30)
        self.assertEqual(sc, before)
        self.assertEqual(mock.call_args.args[1]['H'], 30.)
        self.assertIs(result[0]['DA'], world['A']['D'])

    def test_tab24_audit_counts_harm_and_preserves_run_interface(self):
        d = self.data()
        d['DA'], d['DB'] = d['DB'], d['DA']
        tab = np.zeros((1, 24))
        delay, harm, switches = v4.audit24([d], tab)
        self.assertEqual(harm[0, 0], 1 / 6)
        self.assertEqual(switches[0, 0], 1 / 6)
        old_delay, old_switches = v4.run24([d], tab)
        np.testing.assert_array_equal(old_delay, delay)
        np.testing.assert_array_equal(old_switches, switches)

    def test_outage_disabled_preserves_reference_generator(self):
        sc = v2.worlds()[0]
        with patch.object(v2.g, 'simulate', return_value='reference') as mock:
            self.assertEqual(v2.simulate(123, sc), 'reference')
            mock.assert_called_once_with(123, sc)

    def test_outage_disabled_keeps_every_message(self):
        lost = v2.outage_mask(np.random.default_rng(1), np.arange(10.), 0, 0)
        self.assertFalse(lost.any())

    def test_append_rejects_world_already_saved(self):
        with patch.object(v4.Path, 'open', mock_open(read_data='world\nR1_dualISP\n')):
            with self.assertRaises(ValueError):
                v4.result_path(('R1_dualISP',), True)
            self.assertEqual(v4.result_path(('R3_outageB',), True),
                             v4.Path('results/go_test/rollout_v4_seeds.csv'))

    def test_repeated_world_argument_rejected_before_writing(self):
        with patch.object(v4.v2, 'begin_results') as mock:
            with self.assertRaises(ValueError):
                v4.result_path(('R1_dualISP', 'R1_dualISP'), False)
            mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
