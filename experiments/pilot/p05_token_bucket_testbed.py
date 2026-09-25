# ─── PROVENANCE (2026-09-25, Phase 0 v2 / L0.6) ──────────────────────────────────
# Tạo bởi : Claude (AI) theo yêu cầu tác giả, khi soạn L0.6; tác giả chạy lại và kiểm
# Sinh ra : experiments/pilot/results/p05_token_bucket_testbed_output.txt
# Trích ở : biên bản mô phỏng GVHD (L0.6); ADR K20 (đề xuất sửa); thuyết minh v15 §6.1
# Trạng thái: PILOT (exploratory) — KHÔNG phải bằng chứng RQ1/RQ2
# Seed    : 9115–9117 (chỉ dùng cho pilot này)
# Chạy lại: python experiments/pilot/p05_token_bucket_testbed.py   (~15 s)
# ──────────────────────────────────────────────────────────────────────────────
"""P05 — PILOT (EXPLORATORY). Mô hình token bucket kiểu HTB có giải thích được số đo testbed hơn M/D/1/K không?

Mô hình X1' (ứng viên "thực tế ngoài họ" chạy trong DES, K20): gói 1512 B, đến Poisson; HTB rate = bw,
burst = 1600 B (dt4n `mininet/tc_spec.py`); gói ở đầu hàng rời NGAY khi token ≥ 0 (token được phép âm),
trừ 1512 B mỗi gói; leaf bfifo chứa tối đa q gói đang chờ; OWD = thời gian chờ + 0,13 ms overhead stack
(ước lượng từ CBR tải thấp trong truth_table). So với M/D/1/K (K = q + 1): thời gian chờ và loss chính xác.
Seed 9115–9117: chỉ dùng cho pilot này. KHÔNG phải bằng chứng RQ1/RQ2.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import poisson

L_BYTES, BURST, OVH_S = 1512, 1600, 0.13e-3
BW_MBPS, Q, N_PKT, SEEDS = 4, 10, 200_000, (9115, 9116, 9117)
DATA = Path(__file__).resolve().parents[2] / "data" / "mininet_calibration" / "truth_table.parquet"


def token_bucket(rho, seed):
    rng = np.random.default_rng(seed)
    rate = BW_MBPS * 1e6 / 8                                   # byte/s
    arrivals = np.cumsum(rng.exponential(L_BYTES / (rho * rate), N_PKT))
    tok, tok_t, last_dep = float(BURST), 0.0, 0.0
    waiting, waits, drops = [], [], 0
    for a in arrivals:
        waiting = [d for d in waiting if d > a]                 # gói đã rời trước lúc a ra khỏi bfifo
        if len(waiting) >= Q:
            drops += 1
            continue
        start = max(a, last_dep)
        tok_now = min(BURST, tok + (start - tok_t) * rate)
        if tok_now < 0:                                        # chờ tới khi token về 0
            start += -tok_now / rate
            tok_now = 0.0
        tok, tok_t, last_dep = tok_now - L_BYTES, start, start
        waiting.append(start)
        waits.append(start - a)
    return np.mean(waits) + OVH_S, drops / N_PKT


def mdk_exact(rho, k):
    """M/D/1/K, S = 1: (loss, thời gian chờ theo đơn vị S) qua chuỗi Markov nhúng."""
    a = poisson.pmf(np.arange(k + 60), rho)
    p_mat = np.zeros((k, k))
    for i in range(k):
        base = 0 if i == 0 else i - 1
        for j, aj in enumerate(a):
            p_mat[i, min(base + j, k - 1)] += aj
    A = p_mat.T - np.eye(k); A[-1, :] = 1.0
    b = np.zeros(k); b[-1] = 1.0
    pi = np.linalg.solve(A, b)
    p = np.append(pi / (pi[0] + rho), 1 - 1 / (pi[0] + rho))
    loss = p[k]
    return loss, np.arange(k + 1) @ p / (rho * (1 - loss)) - 1.0


if __name__ == "__main__":
    s_ms = L_BYTES * 8 / (BW_MBPS * 1e6) * 1e3
    t = pd.read_parquet(DATA)
    sel = t[(t["mode"] == "poisson") & (t["bw"] == BW_MBPS) & (t["q"] == Q)].sort_values("rho")
    print(f"poisson, bw = {BW_MBPS} Mb/s, q = {Q}, S = {s_ms:.3f} ms; token bucket: {len(SEEDS)} seed × {N_PKT} gói")
    print(f"{'rho':>5s} | {'OWD đo':>7s} {'TB':>7s} {'M/D/1/K':>8s} | {'lệch TB':>7s} {'lệch MDK':>8s} | "
          f"{'loss đo':>8s} {'loss TB':>8s} {'loss MDK':>8s}")
    err_tb, err_mdk = [], []
    for _, r in sel.iterrows():
        res = np.array([token_bucket(r.rho, s) for s in SEEDS])
        tb_ms, tb_loss = 1e3 * res[:, 0].mean(), res[:, 1].mean()
        mdk_loss, mdk_wait = mdk_exact(r.rho, Q + 1)
        mdk_ms = mdk_wait * s_ms + OVH_S * 1e3
        e1, e2 = tb_ms / r.delay_mean_ms - 1, mdk_ms / r.delay_mean_ms - 1
        err_tb.append(abs(e1)); err_mdk.append(abs(e2))
        print(f"{r.rho:5.2f} | {r.delay_mean_ms:7.3f} {tb_ms:7.3f} {mdk_ms:8.3f} | {e1:+7.1%} {e2:+8.1%} | "
              f"{r.loss:8.3%} {tb_loss:8.3%} {mdk_loss:8.3%}")
    print(f"\nsai số tương đối |OWD|: token bucket TB {np.mean(err_tb):.1%}, max {np.max(err_tb):.1%}; "
          f"M/D/1/K TB {np.mean(err_mdk):.1%}, max {np.max(err_mdk):.1%}")
