"""n01b (L1.2) — Ba sandbox trên CÙNG thế giới: thực tế, lý tưởng, biết trước tương lai.

Thực tế  : twin cũ (telemetry cũ + nhiễu đếm)                     → cell.twin_inputs
Lý tưởng : biết ĐÚNG tải tức thời ρ(t) lúc kiểm + đúng mô hình     → posterior(ρ(t), gap=a, W→0, R=0)
Biết trước: biết luôn I (kết quả thật)                             → duyệt ⇔ I > 0
Cả ba dùng CÙNG luật "duyệt ⇔ lợi ích kỳ vọng > 0" để so được với nhau.
Đơn giản hoá: luôn coi đang ở A. Ô POS_probeB, seed pilot 9101+. Thế giới PSA (sự thật = T(tải TB khoảng giữ)).
Chạy: python -m experiments.n01b_three_sandboxes --H 0.5
"""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

from experiments.scan.cell import get_curve, twin_inputs
from experiments.scan.grid import controls
from experiments.scan.twin import posterior, twin_view
from experiments.scan.world import PKT_BITS, box_avg, simulate_ou, simulate_world, telemetry_view


def world_with_state(seed, cell):
    """Chép đúng thứ tự gọi rng của world.simulate_world, trả thêm ρ(t) tức thời tại mỗi lần kiểm."""
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
        out[name] = dict(rhohat=rhohat, age=age, G_true=box_avg(cs, dt, t_dec + a, t_dec + a + H),
                         rho_now=np.interp(t_dec, np.arange(n_grid) * dt, rho))
    return out


def one_seed(seed, cell, curve, eps):
    w = world_with_state(seed, cell)
    ref = simulate_world(seed, cell)                                  # neo: phải TRÙNG TỪNG BIT với thế giới gốc
    for p in "AB":
        for field in ("rhohat", "age", "G_true"):
            assert np.array_equal(ref[p][field], w[p][field]), (seed, p, field)
    tw = twin_inputs(w, cell, curve, eps)
    post = {}
    for p in "AB":
        q = cell[p]
        m, v = posterior(w[p]["rho_now"], cell["a"], 1e-6, cell["H"], q["rho_bar"], q["sigma"], q["tau"], 0.0)
        post[p] = (m, np.full_like(m, v))
    return dict(I=curve(w["A"]["G_true"]) - curve(w["B"]["G_true"]),
                real=tw["Ibar_A"], ideal=twin_view(curve, *post["A"], *post["B"], eps)[0], plug=tw["Iplug_A"])


def score(I, approve, selected, eps):
    """Mẫu số là tập đề xuất được chọn; regret vẫn tính cả vùng thờ ơ."""
    I, approve = I[selected], approve[selected]
    harm, good = I < -eps, I > eps
    neutral = ~(harm | good)
    dn, tcn = int((approve & harm).sum()), int((~approve & good).sum())
    ratio = lambda numerator, denominator: numerator / denominator if denominator else float("nan")
    regret = np.maximum(I, 0) - approve * I
    result = dict(n=len(I), n_approve=int(approve.sum()), n_harm=int(harm.sum()), n_good=int(good.sum()),
                  n_neutral=int(neutral.sum()), false_approval=dn, false_rejection=tcn,
                  approve_good=int((approve & good).sum()), approve_neutral=int((approve & neutral).sum()),
                  reject_harm=int((~approve & harm).sum()), reject_neutral=int((~approve & neutral).sum()),
                  approval_rate=ratio(approve.sum(), len(I)), harm_rate=ratio(harm.sum(), len(I)),
                  false_approval_all=ratio(dn, len(I)), false_rejection_all=ratio(tcn, len(I)),
                  false_approval_given_harm=ratio(dn, harm.sum()), false_rejection_given_good=ratio(tcn, good.sum()),
                  harm_given_approval=ratio(dn, approve.sum()),
                  headroom_ms=float(np.maximum(I, 0).mean()) if len(I) else float("nan"),
                  gain_ms=float((approve * I).mean()) if len(I) else float("nan"),
                  regret_ms=float(regret.mean()) if len(I) else float("nan"))
    if len(I):
        assert np.all(regret >= 0)
        assert np.isclose(result["regret_ms"], result["headroom_ms"] - result["gain_ms"])
    return result


def export(runs, pooled, cell, eps, elapsed):
    """Lưu số đo theo seed và pooled; không thay các phép tính của lesson."""
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    tag = f"H{cell['H']:g}"
    rows = []
    for seed, d in [(9101 + i, r) for i, r in enumerate(runs)] + [("pooled", pooled)]:
        I = d["I"]
        policies = dict(clairvoyant=I > 0, ideal=d["ideal"] > 0,
                        real=d["real"] > 0, reject_all=np.zeros_like(I, dtype=bool))
        for generator, selected in dict(G_all=np.ones_like(I, dtype=bool), G_greedy=d["plug"] > 0).items():
            for policy, approve in policies.items():
                rows.append(dict(H_s=cell["H"], seed=seed, generator=generator, sandbox=policy,
                                 **score(I, approve, selected, eps)))
    target = out / f"n01b_{tag}_metrics.csv"
    with target.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    raw = out.parent.parent / "results" / "raw" / "n01"
    raw.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(raw / f"n01b_{tag}_epochs.npz", **pooled,
                        seed=np.repeat(np.arange(9101, 9101 + len(runs)), cell["n_epochs"]),
                        epoch=np.tile(np.arange(cell["n_epochs"]), len(runs)))
    (out / f"n01b_{tag}_run.json").write_text(json.dumps(dict(
        cell=cell, seeds=list(range(9101, 9101 + len(runs))), eps_ms=eps,
        elapsed_seconds=elapsed, world_anchor="rhohat, age, G_true: bitwise equal for A/B on every seed",
        ideal_implementation="lesson posterior W=1e-6, R=0; numerical approximation, not an exact oracle",
        raw_path=str((raw / f"n01b_{tag}_epochs.npz").relative_to(out.parent.parent))), indent=2) + "\n")
    print(f"\nNeo rhohat/age/G_true: ĐẠT trên {len(runs)} seed; thời gian {elapsed:.3f} s")
    print(f"Đã lưu {target.relative_to(out.parent.parent)}; dữ liệu epoch: results/raw/n01/n01b_{tag}_epochs.npz")


def main():
    started = time.perf_counter()
    ap = argparse.ArgumentParser()
    ap.add_argument("--H", type=float, default=0.5)
    ap.add_argument("--seeds", type=int, default=10)
    args = ap.parse_args()
    if not np.isfinite(args.H) or args.H <= 0 or not 1 <= args.seeds <= 899:
        ap.error("H phải hữu hạn và >0; seeds trong [1,899] để chỉ dùng pilot 9101–9999")
    _, cell = controls()
    cell["H"] = args.H
    curve, s_ms = get_curve(cell)
    eps = cell["eps_over_s"] * s_ms
    runs = [one_seed(9101 + i, cell, curve, eps) for i in range(args.seeds)]
    d = {k: np.concatenate([r[k] for r in runs]) for k in runs[0]}
    I = d["I"]
    harm, good = I < -eps, I > eps
    headroom = np.mean(np.maximum(I, 0))
    print(f"H={args.H} s | {len(I)} lần kiểm | ε={eps:.3f} ms | lớp: lợi {good.mean():.1%}, thờ ơ "
          f"{1 - good.mean() - harm.mean():.1%}, hại {harm.mean():.1%} | headroom={headroom:.3f} ms")
    print(f"{'sandbox':10s}{'duyệt':>8s}{'DN/mọi':>9s}{'TCN/mọi':>9s}{'DN|hại':>9s}{'TCN|lợi':>9s}{'regret ms':>11s}")
    regret = {}
    for name, a in [("biết trước", I > 0), ("lý tưởng", d["ideal"] > 0), ("thực tế", d["real"] > 0),
                    ("luôn từ chối", np.zeros_like(I, bool))]:
        regret[name] = headroom - np.mean(a * I)                      # = chi phí của mọi lần sai, tính bằng ms
        print(f"{name:10s}{a.mean():8.1%}{np.mean(a & harm):9.2%}{np.mean(~a & good):9.2%}"
              f"{np.sum(a & harm) / harm.sum():9.1%}{np.sum(~a & good) / good.sum():9.1%}{regret[name]:11.3f}")
    print(f"Phân rã regret: thực tế {regret['thực tế']:.3f} = không tránh được {regret['lý tưởng']:.3f}"
          f" + do sandbox không hoàn hảo {regret['thực tế'] - regret['lý tưởng']:.3f} ms")

    print("\nCùng sandbox THỰC TẾ, đổi BỘ SINH ĐỀ XUẤT:")
    aR = d["real"] > 0
    for name, g in [("G_all: mọi lần kiểm đều là đề xuất", np.ones_like(aR)),
                    ("G_greedy: đề xuất khi số đo thô nói B tốt hơn", d["plug"] > 0)]:
        h, gd = g & harm, g & good
        print(f"  {name:46s} hại/đề xuất={h.sum() / g.sum():5.1%}  DN|hại={np.sum(aR & h) / h.sum():5.1%}"
              f"  TCN|lợi={np.sum(~aR & gd) / gd.sum():5.1%}  P(hại|duyệt)={np.sum(aR & h) / np.sum(aR & g):5.1%}")

    export(runs, d, cell, eps, time.perf_counter() - started)


if __name__ == "__main__":
    main()
