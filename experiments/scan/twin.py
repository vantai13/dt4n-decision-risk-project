"""Twin: đường cong delay M/D/1/K + hậu nghiệm Gauss của tải trên khoảng giữ → Ī (tâm) và p₋ (rủi ro)."""
import numpy as np
from scipy.stats import norm

from ndtrisk.theory.mdk import mdk

GH_X, GH_W = np.polynomial.hermite.hermgauss(64)
GH_W = GH_W / np.sqrt(np.pi)


class DelayCurve:
    """T(ρ): delay trung bình (chờ + phục vụ) của gói được nhận, đơn vị ms."""

    def __init__(self, k, s_ms, rho_max=1.4, n=561):
        self.rho = np.linspace(0.0, rho_max, n)
        self.T = np.array([mdk(float(r), int(k)).sojourn for r in self.rho]) * s_ms
        assert np.all(np.diff(self.T) > 0), "T(ρ) phải tăng ngặt để nghịch đảo được"

    def __call__(self, rho):
        return np.interp(rho, self.rho, self.T)

    def inverse(self, t):
        """ρ sao cho T(ρ) = t. Vượt trần → +inf; dưới sàn → −inf."""
        out = np.interp(t, self.T, self.rho)
        out = np.where(t > self.T[-1], np.inf, out)
        return np.where(t < self.T[0], -np.inf, out)


def var_box(L, sigma, tau):
    """Phương sai của tải OU lấy trung bình trên một khoảng dài L."""
    x = L / tau
    return 2 * sigma**2 * (x - 1 + np.exp(-x)) / x**2


def posterior(rhohat, gap, W, H, rho_bar, sigma, tau, R):
    """Hậu nghiệm N(m, v) của tải TB trên khoảng giữ, biết 1 cửa sổ đo."""
    VW, VG = var_box(W, sigma, tau), var_box(H, sigma, tau)
    cov = sigma**2 * tau**2 * (1 - np.exp(-W / tau)) * (1 - np.exp(-H / tau)) * np.exp(-gap / tau) / (W * H)
    beta = cov / (VW + R)
    return rho_bar + beta * (rhohat - rho_bar), np.maximum(VG - cov * beta, 1e-12)


def twin_view(curve, mA, vA, mB, vB, eps_ms):
    """Tính tâm lợi ích và xác suất đổi gây hại theo hai hướng."""
    sA, sB = np.sqrt(2 * vA)[:, None], np.sqrt(2 * vB)[:, None]
    TA = curve(mA[:, None] + sA * GH_X[None, :])
    TB = curve(mB[:, None] + sB * GH_X[None, :])
    Ibar = (TA - TB) @ GH_W
    p_dn = norm.sf((curve.inverse(TA + eps_ms) - mB[:, None]) / np.sqrt(vB)[:, None]) @ GH_W
    p_up = norm.sf((curve.inverse(TB + eps_ms) - mA[:, None]) / np.sqrt(vA)[:, None]) @ GH_W
    return Ibar, p_dn, p_up
