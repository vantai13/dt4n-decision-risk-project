"""Kiểm tương đương cho phần code MỚI của f07 — không chạy thế giới F7 nào (không lộ outcome).

Ý tưởng: mỗi thành phần mới phải trùng TỪNG BIT với thành phần cũ đã kiểm khi đặt về trường hợp suy biến:
  - luật hai ngưỡng với hai ngưỡng bằng nhau  ≡ f02.static_run;
  - oracle có chiều khi tắt chiều             ≡ f05.GridOracle('F', 20);
  - mô phỏng theo khe (CRN)                    ≡ f04b.simulate_pair trên đúng seed và khoá của f04b.
Cộng hai kiểm nhỏ: CI dùng bậc tự do theo số seed thật; tune hai chiều trả ngưỡng khả thi.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
f07 = pytest.importorskip("f07_asym_risk")
import f02_existence_surrogate as f  # noqa: E402
import f04b_des_gap as g  # noqa: E402
import f05_oracle_age as q  # noqa: E402


@pytest.fixture(scope="module")
def synth():
    rng = np.random.default_rng(7)
    return [f07.synthetic_ep(rng, (1.0, 0.8)) for _ in range(4)]


@pytest.mark.parametrize("kind", ["abs", "rel"])
def test_static_run_dir_equals_static_run_when_thresholds_equal(synth, kind):
    thr = np.array([0.0, 0.3, 2.5, 7.0]) if kind == "abs" else np.array([0.0, 0.05, 0.2, 0.6])
    for ep in synth:
        a1, h1 = f.static_run(ep, kind, thr)
        a2, h2 = f07.static_run_dir(ep, kind, thr, thr)
        assert np.array_equal(a1, a2) and np.array_equal(h1, h2)


def test_dir_oracle_without_direction_equals_grid_oracle(synth):
    eps_ms = f.EPS_OVER_S * f07.PATH["A"].s_ms
    orients = [f07.orient_dir(ep, f.static_run(ep, "abs", 1.0)[1][0]) for ep in synth]
    new = f07.DirOracle(orients, eps_ms, use_dir=False)
    old = q.GridOracle(orients, "F", 20, 0, eps_ms)
    for o in orients:
        ib_new, pd_new, _, _ = new.predict(o)
        ib_old, pd_old = old.predict(o)
        assert np.array_equal(ib_new, ib_old) and np.array_equal(pd_new, pd_old)
    assert new.frac_sparse == old.frac_sparse


def test_slot_simulation_equals_f04b_pair():
    cell, stream = g.CELLS["K100_r0.85_s10t2"]
    seed = f.TEST_SEEDS[0]
    ref = g.simulate_pair(cell, f07.psa_for(cell.k), seed, stream)[0]
    new = f07.episode(f07.slot_path(seed, stream, 0, cell), f07.slot_path(seed, stream, 1, cell), cell.s_ms, cell.k)
    for key in ("rh_A", "rh_B", "D_A", "D_B", "I_A", "Ihat_A", "Chat_A", "Chat_B"):
        assert np.array_equal(ref[key], new[key]), key
    assert ref["n_nan"] == new["n_nan"]


def test_ci_uses_actual_degrees_of_freedom():
    x = np.random.default_rng(1).standard_normal(90)
    m, h = f07.ci_n(x)
    assert h == pytest.approx(stats.t.ppf(0.975, 89) * x.std(ddof=1) / np.sqrt(90))
    assert h < f.ci(x)[1]                     # f02.ci cố định t cho 8 seed ⇒ rộng hơn, không dùng cho 90 seed


def test_tune_static_dir_returns_feasible_pair(synth):
    eps_ms = f.EPS_OVER_S * f07.PATH["A"].s_ms
    out = f07.tune_static_dir(synth[:2], "abs", eps_ms, n_grid=20, n_fine=5)
    assert out is not None
    (t12, t21), _ = out
    harm = np.mean([f07.own_J_H(ep, ("dir", "abs", (t12, t21), 0.0), eps_ms)[1] for ep in synth[:2]])
    assert harm <= f.ALPHA + 1e-12
