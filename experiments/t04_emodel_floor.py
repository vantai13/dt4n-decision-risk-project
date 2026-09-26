"""Derive the absolute SESOI floor from ITU-T G.107 (06/2015) section 7.4.

Question: in the most delay-sensitive region of the default E-model curve,
how many additional milliseconds produce a chosen loss of R points?
No random seed is used. This is a theory check, not F2 output.
"""

import numpy as np


def idd(ta_ms):
    """Pure-delay impairment in R points for mouth-to-ear delay Ta (ms)."""
    ta = np.asarray(ta_ms, dtype=float)
    x = np.log(np.maximum(ta, 100.0) / 100.0) / np.log(2.0)
    value = 25.0 * (
        (1 + x**6) ** (1 / 6) - 3 * (1 + (x / 3) ** 6) ** (1 / 6) + 2
    )
    return np.where(ta <= 100.0, 0.0, value)


def slope(ta_ms, h=0.01):
    """Central-difference dIdd/dTa in R points per millisecond."""
    ta = np.asarray(ta_ms, dtype=float)
    return (idd(ta + h) - idd(ta - h)) / (2 * h)


if __name__ == "__main__":
    grid = np.arange(100.5, 500.01, 0.5)
    slopes = slope(grid)
    index = int(np.argmax(slopes))
    print(f"Độ dốc lớn nhất: {slopes[index]:.4f} điểm R/ms tại Ta = {grid[index]:.1f} ms")
    for delta_r in (1, 3, 5):
        print(
            f"  mất {delta_r} điểm R cần ít nhất "
            f"{delta_r/slopes[index]:5.1f} ms trễ thêm (ở vùng nhạy nhất)"
        )
    for ta in (120, 150, 200, 250, 300, 400):
        print(
            f"Ta = {ta:3d} ms: Idd = {float(idd(ta)):6.2f} điểm R;  "
            f"{float(slope(ta)):.4f} điểm R/ms"
        )
