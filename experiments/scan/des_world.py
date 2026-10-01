"""Thế giới DES ghép cặp (theo thiết kế f04b): cùng tải OU, cùng gói đến, cùng số đếm telemetry
→ HAI sự thật trên cùng một thế giới:  PSA = T(tải TB khoảng giữ) như bộ quét;  DES = delay gói thật trong hàng đợi."""
import numpy as np

from experiments.f04b_des_gap import workload_after     # engine DES đã kiểm (f04: khớp M/D/1/K, khớp từng bit)
from experiments.scan.world import PKT_BITS, box_avg, simulate_ou

N_PROBE = 101                                           # số "gói thăm dò" rải đều trong mỗi khoảng giữ


def latest_available(r, rhohat, avail, t_dec):
    """Bản tin mới nhất (theo thời điểm đo) mà twin đã nhận được tại mỗi quyết định — cùng logic world.py."""
    order = np.argsort(avail)
    r_o, rh_o = r[order], rhohat[order]
    freshest = np.maximum.accumulate(np.where(r_o >= np.maximum.accumulate(r_o), np.arange(len(r_o)), 0))
    k = np.searchsorted(avail[order], t_dec, side="right") - 1
    assert (k >= 0).all(), "quyết định đầu tiên xảy ra trước khi có bản tin nào"
    j = freshest[k]
    return rh_o[j], t_dec - r_o[j]


def des_path(rng, cell, p, t_dec, t_end, dt):
    s = PKT_BITS / (cell["mbps"] * 1e6)
    n_grid = int(np.ceil(t_end / dt)) + 1
    rho = simulate_ou(rng, n_grid, dt, p["rho_bar"], p["sigma"], p["tau"])
    cs = np.concatenate([[0.0], np.cumsum(rho) * dt])
    G_true = box_avg(cs, dt, t_dec + cell["a"], t_dec + cell["a"] + cell["H"])          # cho sự thật PSA

    # Gói đến: Poisson không đồng nhất, cường độ ρ(t)/S (đổi thời gian từ Poisson cường độ 1)
    t_grid = np.arange(n_grid + 1) * dt
    cum_lam = np.concatenate([[0.0], np.cumsum(np.clip(rho, 0.0, None) / s * dt)])
    u = np.cumsum(rng.exponential(1.0, int(cum_lam[-1] * 1.05) + 1000))
    arrivals = np.interp(u[u < cum_lam[-1]], cum_lam, t_grid)
    full = (cell["k"] - 1) * s
    v_after = workload_after(arrivals, s, full)                                       # hàng đợi M/D/1/K thật

    # Telemetry: đếm gói THẬT trong cửa sổ (kể cả gói bị drop = tải đề nghị), có tuổi/treo như world.py
    T = p["T_tel"]
    r = np.arange(rng.uniform(0, T) + T, t_end, T)
    count = np.searchsorted(arrivals, r) - np.searchsorted(arrivals, r - T)
    stall = np.where(rng.random(len(r)) < p["stall_p"], rng.exponential(p["stall_mean"], len(r)), 0.0)
    rhohat, age = latest_available(r, count * s / T, r + p["d"] + stall, t_dec)

    # Sự thật DES: delay của gói thăm dò rải đều trong khoảng giữ (bỏ gói bị drop; drop hết → K·S, như f04b)
    probes = (t_dec + cell["a"])[:, None] + np.linspace(0.0, cell["H"], N_PROBE)[None, :]
    j = np.maximum(np.searchsorted(arrivals, probes, side="right") - 1, 0)
    v = np.maximum(v_after[j] - (probes - arrivals[j]), 0.0)
    v = np.where(probes >= arrivals[0], v, 0.0)
    ok = v <= full
    n_ok = ok.sum(1)
    D = np.where(n_ok > 0, np.where(ok, v + s, 0.0).sum(1) / np.maximum(n_ok, 1), cell["k"] * s) * 1e3
    return dict(rhohat=rhohat, age=age, G_true=G_true, D_des=D)


def simulate_world_des(seed, cell):
    """Một seed của thế giới DES: thời điểm quyết định và lưới thời gian dựng giống hệt world.simulate_world."""
    rng = np.random.default_rng(seed)
    H, a, n = cell["H"], cell["a"], cell["n_epochs"]
    paths = (cell["A"], cell["B"])
    dt = min(min(p["T_tel"] for p in paths), H) / 10
    dt = min(dt, min(p["tau"] for p in paths) / 20)
    warm = 3 * max(p["T_tel"] for p in paths) + max(p["d"] + 5 * p["stall_mean"] for p in paths)
    t_dec = warm + H * np.arange(n)
    t_end = t_dec[-1] + a + 2 * H
    return {name: des_path(rng, cell, p, t_dec, t_end, dt) for name, p in zip("AB", paths)}
