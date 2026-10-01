"""Thế giới mô phỏng: tải OU trên 2 path, telemetry có tuổi/treo, tải thật trên khoảng giữ."""
import numpy as np
from scipy.signal import lfilter

PKT_BITS = 1512 * 8


def simulate_ou(rng, n, dt, rho_bar, sigma, tau):
    """Tải đề nghị ρ(t) = ρ̄ + OU, rời rạc chính xác bước dt, điểm đầu lấy từ phân phối dừng."""
    phi = np.exp(-dt / tau)
    e = rng.standard_normal(n)
    e[0] /= np.sqrt(1 - phi**2)
    return rho_bar + lfilter([sigma * np.sqrt(1 - phi**2)], [1.0, -phi], e)


def box_avg(cs, dt, t1, t2):
    """Tải trung bình trên [t1, t2], tính từ tích phân cộng dồn cs (cs[i] = ∫ từ 0 tới i·dt)."""
    tt = np.arange(len(cs)) * dt
    return (np.interp(t2, tt, cs) - np.interp(t1, tt, cs)) / (t2 - t1)


def telemetry_view(rng, cs, dt, s_sec, path, t_dec, t_end):
    """Bản tin telemetry của 1 path và bản tin MỚI NHẤT mà twin có ở mỗi thời điểm quyết định."""
    T = path["T_tel"]
    r = np.arange(rng.uniform(0, T) + T, t_end, T)
    true_w = box_avg(cs, dt, r - T, r)
    n_pkt = rng.poisson(np.maximum(true_w, 0.0) * T / s_sec)
    rhohat = n_pkt * s_sec / T
    stall = np.where(rng.random(len(r)) < path["stall_p"], rng.exponential(path["stall_mean"], len(r)), 0.0)
    avail = r + path["d"] + stall

    order = np.argsort(avail)
    r_o, rh_o = r[order], rhohat[order]
    is_fresher = r_o >= np.maximum.accumulate(r_o)
    freshest = np.maximum.accumulate(np.where(is_fresher, np.arange(len(r_o)), 0))
    k = np.searchsorted(avail[order], t_dec, side="right") - 1
    assert (k >= 0).all(), "quyết định đầu tiên xảy ra trước khi có bản tin nào"
    j = freshest[k]
    return rh_o[j], t_dec - r_o[j]


def simulate_world(seed, cell):
    """Một seed: trả về, cho mỗi path, tải đo được, tuổi, tải thật trên khoảng giữ tại từng quyết định."""
    rng = np.random.default_rng(seed)
    s_sec = PKT_BITS / (cell["mbps"] * 1e6)
    H, a, n = cell["H"], cell["a"], cell["n_epochs"]
    paths = (cell["A"], cell["B"])
    dt = min(min(p["T_tel"] for p in paths), H) / 10
    dt = min(dt, min(p["tau"] for p in paths) / 20)
    warm = 3 * max(p["T_tel"] for p in paths) + max(p["d"] + 5 * p["stall_mean"] for p in paths)
    t_dec = warm + H * np.arange(n)
    t_end = t_dec[-1] + a + 2 * H
    n_grid = int(np.ceil(t_end / dt)) + 1
    out = {}
    for name, p in zip("AB", paths):
        rho = simulate_ou(rng, n_grid, dt, p["rho_bar"], p["sigma"], p["tau"])
        cs = np.concatenate([[0.0], np.cumsum(rho) * dt])
        rhohat, age = telemetry_view(rng, cs, dt, s_sec, p, t_dec, t_end)
        out[name] = dict(rhohat=rhohat, age=age, G_true=box_avg(cs, dt, t_dec + a, t_dec + a + H))
    return out
