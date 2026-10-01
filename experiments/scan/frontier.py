"""So K2 với SC ở CÙNG một mức harm thực tế (đường cong gain–harm), thế giới DES như bậc C, seed kiểm tra của confirm.
K2 'đổi nếu Ī − λ·p₋ > 0'  ⇔  'đổi nếu Ī/p₋ > λ'  → K2 xếp hạng cơ hội đổi theo tỉ lệ LỢI/RỦI RO; SC xếp theo LỢI Ī.
Cả hai là "lấy dần từ trên xuống" theo một điểm số → đường cong tính bằng tổng cộng dồn.
Chạy từ gốc repo:   python -m experiments.scan.frontier"""
import numpy as np

from experiments.scan.cell import _pool, get_curve
from experiments.scan.confirm import CAL_SEEDS, TEST_SEEDS, decisions_paired
from experiments.scan.grid import controls, grid
from experiments.scan.rules import orient, s0_trajectory, tune_threshold

CELLS = ["m069", "m071", "m085", "m070", "m087", "m084", "m086", "m080", "m083"]   # 9 ô đạt bậc C — KHÓA
N_BOOT = 300


def scores(o):
    ratio = np.where(o["Ibar"] > 0, o["Ibar"] / np.maximum(o["pdn"], 1e-300), -np.inf)   # Ī ≤ 0 thì K2 không bao giờ đổi
    return {"S0": o["Iplug"], "SC": o["Ibar"], "K2": ratio}


def best_gain(score, I, harmful, budget):
    """Gain lớn nhất của họ luật 'lấy dần theo score' mà số lần hại ≤ budget (trên chính dữ liệu này)."""
    order = np.argsort(-score, kind="stable")
    cg = np.concatenate([[0.0], np.cumsum(I[order])])
    ch = np.concatenate([[0], np.cumsum(harmful[order])])
    return cg[ch <= budget].max()


def harm_needed(score, I, harmful, target_gain):
    """Số lần hại ít nhất để họ luật này đạt tổng gain ≥ target_gain (inf nếu không bao giờ đạt)."""
    order = np.argsort(-score, kind="stable")
    cg = np.cumsum(I[order])
    ch = np.cumsum(harmful[order])
    best_harm_so_far = np.minimum.accumulate(ch[::-1])[::-1]       # hại nhỏ nhất trong các tiền tố ĐỦ dài
    ok = cg >= target_gain
    return float(best_harm_so_far[ok].min()) if ok.any() else np.inf


def delta_at(o, alpha, eps_ms):
    """Chỉ phần cần cho bootstrap: gain(K2) − gain(SC) ở cùng ngân sách hại α (đã gộp seed)."""
    n, harmful = len(o["I"]), o["I"] < -eps_ms
    s = scores(o)
    return (best_gain(s["K2"], o["I"], harmful, alpha * n) - best_gain(s["SC"], o["I"], harmful, alpha * n)) / n


def matched(test_o, alpha, eps_ms):
    o = _pool(test_o)
    n, I, harmful = len(o["I"]), o["I"], o["I"] < -eps_ms
    budget = alpha * n
    s = scores(o)
    g = {r: best_gain(s[r], I, harmful, budget) / n for r in s}
    h_k2 = harm_needed(s["K2"], I, harmful, g["SC"] * n) / n          # K2 cần bao nhiêu hại để có gain bằng SC
    return dict(head=float(np.mean(np.maximum(I, 0))), **{f"g_{r}": v for r, v in g.items()},
                d=g["K2"] - g["SC"], harm_ratio=h_k2 / alpha)


def frontier_cell(cell, rng):
    curve, s_ms = get_curve(cell)
    eps_ms, alpha = cell["eps_over_s"] * s_ms, cell["alpha"]
    cal = [decisions_paired(s, cell, curve, eps_ms)[1] for s in CAL_SEEDS]       # [1] = sự thật DES
    test = [decisions_paired(s, cell, curve, eps_ms)[1] for s in TEST_SEEDS]
    h0 = 0.0                                                                     # quỹ đạo tham chiếu như bậc C
    for _ in range(2):
        c = _pool([orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in cal])
        h0 = tune_threshold(c["Iplug"], c["I"], (c["I"] < -eps_ms).astype(float), alpha)
    test_o = [orient(d, s0_trajectory(d["Iplug_A"], h0)) for d in test]
    res = matched(test_o, alpha, eps_ms)
    boot = [delta_at(_pool([test_o[i] for i in rng.integers(0, len(test_o), len(test_o))]), alpha, eps_ms)
            for _ in range(N_BOOT)]                                              # bootstrap theo SEED
    res["d_lo"], res["d_hi"] = np.percentile(boot, [2.5, 97.5])
    return res


def main():
    rng = np.random.default_rng(12345)
    all_cells = {c["name"]: c for c in grid()}
    print(f"{'ô':10s} {'headroom':>8s} {'gain SC':>8s} {'gain K2':>8s} | {'Δ cùng harm (ms)':>24s} {'%head':>6s} {'%SC':>5s} | K2 cần harm (×α) để bằng gain SC")
    for c in [controls()[0]] + [all_cells[n] for n in CELLS]:
        r = frontier_cell(c, rng)
        print(f"{c['name']:10s} {r['head']:8.3f} {r['g_SC']:8.3f} {r['g_K2']:8.3f} | {r['d']:+7.3f} [{r['d_lo']:+.3f}, {r['d_hi']:+.3f}] "
              f"{100 * r['d'] / r['head']:6.2f} {100 * r['d'] / max(r['g_SC'], 1e-9):5.0f} | {r['harm_ratio']:.2f}")


if __name__ == "__main__":
    main()
