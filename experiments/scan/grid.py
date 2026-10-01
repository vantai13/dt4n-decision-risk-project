"""Bản đồ v0: các trục cần quét + 2 ô đối chứng."""
import itertools

import numpy as np

BASE = dict(mbps=10, k=83, H=0.5, a=0.05, eps_over_s=0.5, rho_A=0.95, d=0.1)

AXES = dict(
    r_f=[30e3, 300e3],
    tau=[2.0, 10.0, 60.0],
    T_tel_A=[0.5, 5.0],
    probe_B=["same", 30.0],
    rho_B=[0.95, 0.85],
    alpha=[0.01, 0.002],
)


def make_path(rho, r_f, mbps, tau, T_tel, d):
    sigma = float(np.sqrt(rho * r_f / (mbps * 1e6)))
    return dict(rho_bar=rho, sigma=sigma, tau=tau, T_tel=T_tel, d=d, stall_p=0.0, stall_mean=0.0)


def make_cell(name, **kw):
    p = {**BASE, **kw}
    T_B = p["T_tel_A"] if p["probe_B"] == "same" else float(p["probe_B"])
    return dict(name=name, mbps=p["mbps"], k=p["k"], H=p["H"], a=p["a"], eps_over_s=p["eps_over_s"],
                alpha=p["alpha"], n_epochs=max(4000, int(100 * p["tau"] / p["H"])),
                A=make_path(p["rho_A"], p["r_f"], p["mbps"], p["tau"], p["T_tel_A"], p["d"]),
                B=make_path(p["rho_B"], p["r_f"], p["mbps"], p["tau"], T_B, p["d"]),
                n_flows_min=min(p["rho_A"], p["rho_B"]) * p["mbps"] * 1e6 / p["r_f"],
                axes={k: p[k] for k in AXES})


def grid():
    for i, values in enumerate(itertools.product(*AXES.values())):
        yield make_cell(f"m{i:03d}", **dict(zip(AXES, values)))


def controls():
    """ÂM: góc P2 cũ. DƯƠNG: B chỉ được probe thưa + α chặt."""
    neg = make_cell("NEG_P2_cu", mbps=4, k=100, r_f=0.10**2 * 4e6 / 0.95, tau=2.0,
                    T_tel_A=0.5, probe_B="same", rho_B=0.95, alpha=0.01)
    pos = make_cell("POS_probeB", r_f=300e3, tau=10.0, T_tel_A=0.5, probe_B=30.0, rho_B=0.85, alpha=0.002)
    return neg, pos
