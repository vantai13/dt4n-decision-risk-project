"""GO-check: closed-loop rollout evaluation for SC and K2.

Run from the repository root:
    python -m experiments.gocheck.rollout --seeds go0
    python -m experiments.gocheck.rollout --seeds fresh
"""
import argparse
import pickle
import subprocess
import time
from pathlib import Path

import numpy as np
from scipy import stats

from experiments.scan import go_test as g

SEEDS = {
    "go0": (range(80001, 80021), range(81001, 81021)),
    "fresh": (range(92001, 92021), range(93001, 93021)),
}
EPS = 1.0
ALPHAS = (0.002, 0.01)
COOLDOWNS = (0, 30)
GRID = {
    "SC": np.r_[np.linspace(0, 10, 41), np.linspace(11, 80, 70), np.inf],
    "K2": np.r_[np.logspace(-1, 6, 120), np.inf],
}
RAW = Path("results/gocheck/raw")


def require_committed_spec(path):
    """Reject incomplete or uncommitted preregistration before opening fresh seeds."""
    spec = Path(path)
    content = spec.read_text()
    if "Trạng thái: locked" not in content or "CHƯA ĐIỀN" in content:
        raise ValueError(f"{path}: cần dự đoán tác giả và Trạng thái: locked trước seed mới.")
    committed = subprocess.run(
        ["git", "show", f"HEAD:{path}"], capture_output=True, check=False
    )
    if committed.returncode or committed.stdout != spec.read_bytes():
        raise ValueError(f"{path}: cần commit spec khóa trước seed mới.")


def score(rule, ibar, p_harm):
    """Rank one switching opportunity."""
    if rule == "SC":
        return ibar
    return ibar / max(p_harm, 1e-300) if ibar > 0 else -np.inf


def rollout(d, w, rule, thr, cooldown):
    """Return mean delay, harmful switches/epoch and switches/1000 epochs."""
    ibar_a, p_dn, p_up = d["Ibar_A"], d["pdn_A"], d["pup_A"]
    d_a, d_b = w["A"]["D"], w["B"]["D"]
    n = len(ibar_a)
    on_a, last_switch = True, -10**9
    total_delay, n_harm, n_switch = 0.0, 0, 0
    for k in range(n):
        if rule != "stayA" and k - last_switch >= cooldown:
            ibar = ibar_a[k] if on_a else -ibar_a[k]
            p_harm = p_dn[k] if on_a else p_up[k]
            if score(rule, ibar, p_harm) > thr:
                d_cur, d_new = (d_a[k], d_b[k]) if on_a else (d_b[k], d_a[k])
                n_harm += (d_cur - d_new) < -EPS
                n_switch += 1
                on_a, last_switch = not on_a, k
        total_delay += d_a[k] if on_a else d_b[k]
    return total_delay / n, n_harm / n, 1000 * n_switch / n


def tune(rule, cal_d, cal_w, alpha, cooldown):
    """Tune on calibration rollout subject to the harm budget."""
    best_delay, best_thr = np.inf, np.inf
    for thr in GRID[rule]:
        results = np.array(
            [rollout(d, w, rule, thr, cooldown) for d, w in zip(cal_d, cal_w)]
        )
        if results[:, 1].mean() <= alpha and results[:, 0].mean() < best_delay:
            best_delay, best_thr = results[:, 0].mean(), thr
    return best_thr


def paired_ci(values):
    values = np.asarray(values)
    half_width = (
        stats.t.ppf(0.975, len(values) - 1)
        * values.std(ddof=1)
        / np.sqrt(len(values))
    )
    return values.mean(), values.mean() - half_width, values.mean() + half_width


def load_worlds(scenario, seeds, tag):
    RAW.mkdir(parents=True, exist_ok=True)
    cache = RAW / f"{scenario['name']}_{tag}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    worlds = [g.simulate(seed, scenario) for seed in seeds]
    cache.write_bytes(pickle.dumps(worlds))
    return worlds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", choices=SEEDS, default="go0")
    args = parser.parse_args()
    if args.seeds == "fresh":
        require_committed_spec("notes/gocheck/GO_check_spec.md")
    cal_seeds, test_seeds = SEEDS[args.seeds]
    scenario = g.scenarios()[0][0]
    started = time.time()
    cal_w = load_worlds(scenario, cal_seeds, f"{args.seeds}_cal")
    test_w = load_worlds(scenario, test_seeds, f"{args.seeds}_test")
    cal_d = [g.decisions(w, scenario, {}, EPS) for w in cal_w]
    test_d = [g.decisions(w, scenario, {}, EPS) for w in test_w]
    print(
        f"R1 · seed '{args.seeds}' · mô phỏng xong sau {time.time() - started:.0f} s"
    )

    stay = np.array(
        [rollout(d, w, "stayA", None, 0) for d, w in zip(test_d, test_w)]
    )
    hindsight = np.array(
        [np.minimum(w["A"]["D"], w["B"]["D"]).mean() for w in test_w]
    )
    print(
        f"Thang đo (test): luôn ở A = {stay[:, 0].mean():.3f} ms · "
        f"oracle nhìn trước = {hindsight.mean():.3f} ms "
        "(cận dưới KHÔNG đạt được; chỉ để biết trần lợi ích)"
    )

    for cooldown in COOLDOWNS:
        for alpha in ALPHAS:
            results = {}
            for rule in ("SC", "K2"):
                threshold = tune(rule, cal_d, cal_w, alpha, cooldown)
                results[rule] = np.array(
                    [
                        rollout(d, w, rule, threshold, cooldown)
                        for d, w in zip(test_d, test_w)
                    ]
                )
            mean, low, high = paired_ci(
                results["SC"][:, 0] - results["K2"][:, 0]
            )
            print(f"\n--- cooldown {cooldown:>2} s · α = {alpha} ---")
            for rule, values in results.items():
                print(
                    f"  {rule}: delay TB {values[:, 0].mean():6.3f} ms · "
                    f"harm {values[:, 1].mean() / alpha:4.2f}·α · "
                    f"{values[:, 2].mean():5.1f} lần đổi/1000 epoch"
                )
            print(
                f"  delay(SC) − delay(K2) = {mean:+.3f} "
                f"[{low:+.3f}, {high:+.3f}] ms   (dương = K2 tốt hơn)"
            )
    print(f"\n({time.time() - started:.0f} s)")


if __name__ == "__main__":
    main()
