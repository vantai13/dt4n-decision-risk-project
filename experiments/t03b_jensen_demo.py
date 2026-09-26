"""Illustrate Jensen bias on the M/D/1/K delay curve; not an RQ result."""

import numpy as np

from ndtrisk.theory.mdk import mdk

S_MS = 1512 * 8 / 4e6 * 1e3
SD = 0.028
GRID = np.linspace(0.60, 1.30, 1401)


if __name__ == "__main__":
    standard_normal = np.random.default_rng(9301).standard_normal(200_000)
    print(f"{'K':>4} {'m':>5} | {'W(m) cắm số':>12} {'E[W(rho)]':>10} {'chênh Jensen':>13}")
    for k_sys in (11, 100):
        curve_ms = np.array([mdk(rho, k_sys).sojourn for rho in GRID]) * S_MS
        for mean_load in (0.85, 0.93, 0.97):
            plug_in = float(np.interp(mean_load, GRID, curve_ms))
            expected = float(np.interp(mean_load + SD * standard_normal, GRID, curve_ms).mean())
            print(
                f"{k_sys:4d} {mean_load:5.2f} | {plug_in:9.2f} ms {expected:7.2f} ms "
                f"{expected - plug_in:+10.2f} ms"
            )
