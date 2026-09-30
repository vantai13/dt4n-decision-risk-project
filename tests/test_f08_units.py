"""Kiểm đơn vị cho f08 (P1v2/L1.9): Riccati, bộ lọc, tương đương f04b, bất biến oracle, R² AR(1) ≤ tốt nhất."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import f02_existence_surrogate as f  # noqa: E402
import f04b_des_gap as g  # noqa: E402
import f07_asym_risk as r7  # noqa: E402
import f08_history_twin as h  # noqa: E402

CELLS = [g.CELLS[name][0] for name in h.WORLDS.values()]


def test_riccati_fixed_point_and_gain_range():
    for cell in CELLS:
        kp = h.kalman_params(cell)
        P, R, Q, phi = kp["P_prior"], kp["R"], kp["Q"], kp["phi"]
        assert abs(P - (phi**2 * P * R / (P + R) + Q)) < 1e-15
        assert 0.0 < kp["K"] < 1.0 and 0.0 < kp["a"] < phi
        assert kp["P_post"] < kp["V"]                  # lịch sử luôn giảm phương sai so với không biết gì


def test_filter_impulse_response_is_geometric():
    kp = h.kalman_params(CELLS[0])
    y = np.zeros(30) + kp["mu"]
    y[0] += 1.0
    x = (h.kalman_center(y, kp) - kp["mu"]) / kp["c"]
    assert np.allclose(x, kp["K"] * kp["a"] ** np.arange(30), rtol=0, atol=1e-15)


def test_filter_tracks_measurement_when_noise_vanishes():
    cell = CELLS[0]
    kp = dict(h.kalman_params(cell))
    kp["R"] = 1e-12
    bq = kp["R"] * (1 - kp["phi"] ** 2) - kp["Q"]
    P = 0.5 * (-bq + np.sqrt(bq * bq + 4 * kp["Q"] * kp["R"]))
    kp["K"] = P / (P + kp["R"])
    kp["a"] = kp["phi"] * (1 - kp["K"])
    y = cell.rho_bar + 0.05 * np.sin(np.arange(50))
    x = (h.kalman_center(y, kp) - kp["mu"]) / kp["c"]
    assert np.allclose(x, y - kp["mu"], atol=1e-9)


def test_extended_simulation_is_bit_exact_f04b():
    cell, stream = g.CELLS["K100_r0.95_s03t10"]
    psa = r7.psa_for(cell.k)
    ch = np.random.SeedSequence([9711, stream]).spawn(2)[0]
    t_dec = g.BURN_IN + cell.lag + cell.win + cell.hold * np.arange(f.N_EPOCH)
    rh_ref, des_ref, _, nan_ref, _ = g.one_path(np.random.default_rng(ch), cell, psa, t_dec)
    p = h.path_series(np.random.default_rng(ch), cell, psa)
    assert np.array_equal(p["rh"], rh_ref) and np.array_equal(p["des"], des_ref) and p["n_nan"] == nan_ref
    assert len(p["rh_all"]) == f.N_EPOCH + h.N_PRE


def test_f1_episode_equals_f04b_and_fh_shares_truth():
    cell, stream = g.CELLS["P2"]
    ep = h.simulate(cell, (9711,), stream)
    ref = g.simulate_pair(cell, r7.psa_for(cell.k), 9711, stream)[0]
    for k in ("rh_A", "rh_B", "D_A", "D_B", "I_A", "Ihat_A", "Chat_A", "Chat_B"):
        assert np.array_equal(ep["F1"][0][k], ref[k])
    for k in ("D_A", "D_B", "I_A"):                     # CRN: sự thật giống hệt, chỉ twin khác
        assert np.array_equal(ep["FH"][0][k], ep["F1"][0][k])
    assert not np.array_equal(ep["FH"][0]["rh_A"], ep["F1"][0]["rh_A"])


def test_oracle_invariant_to_common_rescaling_of_centers():
    """Vì sao hệ số dự báo e^(−g/τ) không ảnh hưởng oracle: cạnh phân vị gộp đổi theo cùng phép biến đổi đơn điệu."""
    rng = np.random.default_rng(7)
    raw = [(rng.normal(size=500), rng.normal(size=500), rng.normal(size=500)) for _ in range(40)]
    mk = lambda scale: [dict(rh_cur=scale * rc, rh_alt=scale * ra, I=I, dir=np.zeros(500, np.int64))
                        for rc, ra, I in raw]
    a, b = mk(1.0), mk(0.5)                           # lũy thừa của 2: phép nhân chính xác trong dấu phẩy động
    oa, ob = r7.DirOracle(a, 1.5, use_dir=False), r7.DirOracle(b, 1.5, use_dir=False)
    for x, y in zip(a[:5], b[:5]):
        assert all(np.array_equal(u, v) for u, v in zip(oa.predict(x), ob.predict(y)))


def test_ar1_kalman_r2_between_one_window_and_best():
    for cell in CELLS:
        th = h.ar1_vs_exact(cell)
        assert th["exact"][1] - 1e-12 <= th["r2_corr"] <= th["exact"][80] + 1e-9
        assert th["r2_mse"] <= th["r2_corr"] + 1e-12   # hệ số sai chỉ làm MSE tệ đi, không làm tương quan đổi


def test_seed_ranges_disjoint():
    s = h.SEEDS
    assert not set(s["cal"]) & set(s["test"]) and not set(s["cal"]) & set(s["orc"]) and not set(s["test"]) & set(s["orc"])
    assert len(s["test"]) == 90 and len(s["orc"]) == 597
