"""P01 — PILOT KHÁM PHÁ (EXPLORATORY). KHÔNG dùng làm bằng chứng cho báo cáo/paper.

Câu hỏi duy nhất: trạng thái tải (cũ) mà NDT thấy có giúp xếp hạng quyết định "nguy hiểm"
tốt hơn các cách không dùng trạng thái hiện tại không? Và dạng dùng tải nào là đủ?

Thế giới đồ chơi: 2 đường, mỗi đường 1 link nút cổ chai độc lập.
  rho_k(t) = m_k(t) (OU chậm, thời gian T_reg) + x_k(t) (OU nhanh, tau = 1)
  C_k(t)   = prop_k + Q(rho_k(t)),  Q = M/M/1 hoặc đường cong đo Mininet
Twin thấy rho(t - z) và dùng ĐÚNG hàm Q (chỉ có sai do dữ liệu cũ). Thời gian tính theo đơn vị tau.
"""
import numpy as np
from scipy.signal import lfilter

# data/mininet_calibration/truth_table.parquet: mode=poisson, bw=6, q=13 (delay_mean_ms theo rho)
MEAS_RHO = np.round(np.arange(0.50, 1.041, 0.02), 2)
MEAS_MS = np.array([.427, .452, .497, .556, .625, .710, .785, .889, 1.012, 1.150, 1.296, 1.513, 1.747,
                    2.021, 2.342, 2.601, 3.174, 3.720, 4.365, 5.075, 5.725, 6.978, 8.079, 9.247, 10.477,
                    11.755, 13.048, 14.202])

CFG = dict(dt=0.05, z=0.5, sig_f=0.06, sig_m=0.12, mu=0.72, prop=np.array([10.0, 11.0]),
           w_hist=10.0, t_dec=0.1, horizon=4000.0, eps=1.0, alpha=0.01, n_mc=60)


def q_delay(rho, kind):
    if kind == "mm1":
        return 0.7 / (1.0 - np.clip(rho, 0.0, 0.985))
    return np.interp(rho, MEAS_RHO, MEAS_MS)          # ngoài dải đo: giữ giá trị biên (xem cảnh báo)


def q_slope(rho, kind, floor=1e-3):
    if kind == "mm1":
        return 0.7 / (1.0 - np.clip(rho, 0.0, 0.985)) ** 2
    h = 0.02                                           # sai phân trung tâm trên đường cong đo
    return np.maximum((q_delay(rho + h, kind) - q_delay(rho - h, kind)) / (2 * h), floor)


def ou(n, tau, sd, rng, dt):
    phi = np.exp(-dt / tau)
    e = rng.normal(0.0, sd * np.sqrt(1 - phi ** 2), size=(n, 2))
    e[0] = rng.normal(0.0, sd, size=2)                 # khởi tạo từ phân phối dừng
    return lfilter([1.0], [1.0, -phi], e, axis=0)


def coverage_at_risk(score, harm, alpha):
    """Coverage lớn nhất khi ACCEPT các quyết định score cao nhất sao cho P(harm | ACCEPT) <= alpha.
    Ngưỡng chọn trên chính dữ liệu test: chỉ đo khả năng XẾP HẠNG, chưa đo hiệu chỉnh."""
    o = np.argsort(-score, kind="stable")
    ok = np.where(np.cumsum(harm[o]) / np.arange(1, len(o) + 1) <= alpha)[0]
    return 0.0 if len(ok) == 0 else (ok.max() + 1) / len(o)


def simulate(kind, t_reg, seed, c=CFG):
    rng = np.random.default_rng(seed)
    dt = c["dt"]; n = int(c["horizon"] / dt)
    lag = int(round(c["z"] / dt)); wn = int(round(c["w_hist"] / dt))
    m = c["mu"] + ou(n, t_reg, c["sig_m"], rng, dt)
    x = ou(n, 1.0, c["sig_f"], rng, dt)
    rho = m + x
    C = c["prop"] + q_delay(rho, kind)                 # sự thật
    D = C[:, 1] - C[:, 0]

    fit_end = n // 5                                   # 20% đầu: chỉ để ước lượng tham số (quá khứ)
    gamma = np.mean((rho[lag:fit_end] - rho[:fit_end - lag]) ** 2, axis=0)
    ar = []
    for k in range(2):                                 # rho(u) ~ a + b * rho(u - z) + nhiễu
        X, Y = rho[:fit_end - lag, k], rho[lag:fit_end, k]
        b, a = np.polyfit(X, Y, 1)
        ar.append((a, b, np.std(Y - (a + b * X), ddof=2)))

    inc2 = np.zeros(n); inc2[lag:] = (D[lag:] - D[:-lag]) ** 2
    csum = np.concatenate([[0.0], np.cumsum(inc2)])

    t_idx = np.arange(fit_end + wn + lag, n, int(round(c["t_dec"] / dt)))
    s = t_idx - lag                                    # thời điểm của telemetry twin đang thấy
    rho_hat, C_hat, C_now = rho[s], C[s], C[t_idx]
    rows = np.arange(len(t_idx))
    a1 = np.argmin(C_hat, axis=1)
    harm = (C_now[rows, a1] - C_now.min(axis=1)) > c["eps"]
    m_hat = np.abs(C_hat[:, 1] - C_hat[:, 0])

    s_hist = np.sqrt((csum[s + 1] - csum[s + 1 - wn]) / wn)                 # học từ lịch sử gần
    s_mag = np.sqrt(np.sum(q_delay(rho_hat, kind) ** 2, axis=1))            # kiểu OpenTwin
    s_sens = np.sqrt(np.sum(q_slope(rho_hat, kind) ** 2 * gamma, axis=1))   # độ nhạy (delta method)

    def p_harm(sample_rho):                            # đẩy phân phối tải qua đường cong độ trễ
        Cs = c["prop"] + q_delay(sample_rho, kind)
        reg = np.take_along_axis(Cs, a1[:, None, None].repeat(Cs.shape[1], 1), 2)[..., 0] - Cs.min(axis=2)
        return np.mean(reg > c["eps"], axis=1)

    nm = c["n_mc"]
    prop_samp = np.stack([ar[k][0] + ar[k][1] * rho_hat[:, k][:, None]
                          + rng.normal(0, ar[k][2], (len(s), nm)) for k in range(2)], axis=2)
    pm, px = np.exp(-c["z"] / t_reg), np.exp(-c["z"])
    orac_samp = (c["mu"] + (m[s] - c["mu"])[:, None, :] * pm
                 + rng.normal(0, c["sig_m"] * np.sqrt(1 - pm ** 2), (len(s), nm, 2))
                 + x[s][:, None, :] * px + rng.normal(0, c["sig_f"] * np.sqrt(1 - px ** 2), (len(s), nm, 2)))

    tie = 1e-6 / (1.0 + m_hat)                         # phá hoà giữa các P(harm) bằng nhau
    scores = {"margin": m_hat, "history": m_hat / s_hist, "magnitude": m_hat / s_mag,
              "sens(delta)": m_hat / s_sens, "PROPAGATED": -p_harm(prop_samp) + tie,
              "oracle*": -p_harm(orac_samp) + tie}
    return harm.mean(), {k: coverage_at_risk(v, harm, c["alpha"]) for k, v in scores.items()}


def diagnose_curves():
    r = np.array([0.55, 0.65, 0.75, 0.85, 0.90, 0.95, 1.00])
    print("Chẩn đoán T'/T (gần hằng số => chuẩn hoá theo độ lớn ~ chuẩn hoá theo độ nhạy):")
    for kind in ("mm1", "measured"):
        print(f"  {kind:8s} rho={r} -> T'/T = {np.round(q_slope(r, kind) / q_delay(r, kind), 1)}")


if __name__ == "__main__":
    np.seterr(divide="ignore", invalid="ignore")
    diagnose_curves()
    cells = [(0.5, 0.03, 20.0), (0.5, 0.06, 20.0), (0.5, 0.06, 100.0), (2.0, 0.03, 20.0), (2.0, 0.06, 100.0)]
    head = None
    for kind in ("mm1", "measured"):
        for z, sf, t_reg in cells:
            cfg = dict(CFG, z=z, sig_f=sf)
            res = [simulate(kind, t_reg, seed, cfg) for seed in (9001, 9002, 9003)]  # seed pilot: 9000+
            base = np.mean([r[0] for r in res])
            cov = {k: np.mean([r[1][k] for r in res]) for k in res[0][1]}
            if head is None:
                head = list(cov)
                print(f"\n{'delay':8s} {'z':>4s} {'sigF':>5s} {'Treg':>5s} | {'harm':>5s} | " + " ".join(f"{h:>11s}" for h in head))
            flag = "  <- suy biến" if base <= 2 * CFG["alpha"] else ""
            print(f"{kind:8s} {z:4.1f} {sf:5.2f} {t_reg:5.0f} | {base:5.3f} | "
                  + " ".join(f"{cov[h]:11.3f}" for h in head) + flag)
