"""t06 (P1v2/L1.5) — Lịch sử đáng bao nhiêu? R² của tải trung bình trên khoảng giữ theo số cửa sổ đo.

Mô hình: tải OU(μ, σ, τ); n cửa sổ liền nhau dài W, cửa sổ mới nhất kết thúc tại t_m; khoảng giữ [t_m + g, t_m + g + H],
g = lag + a. Mỗi số đo = trung bình tải của cửa sổ + nhiễu đếm độc lập phương sai R = ρ̄·S/W.
R² = 1 − Var(G | y₁…yₙ)/Var(G): tỉ lệ phương sai tải-khoảng-giữ mà n số đo giải thích (điều kiện hoá Gauss = Kalman).
Hai cách tính độc lập: (A) lưới dt = 0,01 s, hạt nhân σ²·e^(−|u−v|/τ), trọng số hình thang (như f02);
(B) công thức đóng: Cov hai trung bình khoảng rời nhau = σ²·τ²(1 − e^(−L₁/τ))(1 − e^(−L₂/τ))e^(−khe/τ)/(L₁L₂).
Kiểm lý thuyết (không mô phỏng ngẫu nhiên, không seed). Provenance: Claude (AI) soạn theo L1.5; tác giả kiểm.
Chạy: python experiments/t06_history_information.py | tee experiments/results/t06_history_information_output.txt
"""
import numpy as np

S_MS = 1512 * 8 / 4e6 * 1e3                  # 3,024 ms ở 4 Mb/s
W, H, LAG, ACT, DT = 0.5, 0.5, 0.37, 0.05, 0.01
N_WIN = (1, 2, 5, 10, 20)
CELLS = {                                      # tên: (ρ̄, σ, τ)
    "P1 (0,85; 0,03; 10 s)": (0.85, 0.03, 10.0),
    "K100/0,95/0,03/10 s": (0.95, 0.03, 10.0),
    "P2 (0,95; 0,10; 2 s)": (0.95, 0.10, 2.0),
}
REFERENCE = {                                  # đáp án đối chiếu của PHASE_1v2 L1.5 (±0,005)
    "P1 (0,85; 0,03; 10 s)": (0.126, 0.211, 0.340, 0.405, 0.423),
    "K100/0,95/0,03/10 s": (0.115, 0.194, 0.319, 0.386, 0.406),
    "P2 (0,95; 0,10; 2 s)": (0.292, 0.318, 0.322, 0.322, 0.322),
}


def intervals(n):
    """Các khoảng [bắt đầu, kết thúc] (giây, gốc t_m = 0): n cửa sổ đo (mới nhất trước) rồi khoảng giữ."""
    wins = [(-(k + 1) * W, -k * W) for k in range(n)]
    return wins, (LAG + ACT, LAG + ACT + H)


def cov_grid(i1, i2, sigma, tau):
    """(A) Hiệp phương sai của hai trung bình khoảng, tính trên lưới dt với trọng số hình thang."""
    def pts(iv):
        x = np.arange(iv[0], iv[1] + DT / 2, DT)
        w = np.ones(len(x))
        w[0] = w[-1] = 0.5
        return x, w / w.sum()
    (x1, w1), (x2, w2) = pts(i1), pts(i2)
    return float(w1 @ (sigma**2 * np.exp(-np.abs(x1[:, None] - x2[None, :]) / tau)) @ w2)


def cov_closed(i1, i2, sigma, tau):
    """(B) Công thức đóng; hai khoảng trùng nhau dùng V(L) của T2 §4."""
    l1, l2 = i1[1] - i1[0], i2[1] - i2[0]
    if i1 == i2:
        x = l1 / tau
        return 2 * sigma**2 * (x - 1 + np.exp(-x)) / x**2
    first, second = (i1, i2) if i1[1] <= i2[0] else (i2, i1)
    gap = second[0] - first[1]
    assert gap >= -1e-12, "chỉ dùng cho hai khoảng rời nhau hoặc trùng nhau"
    return float(sigma**2 * tau**2 * (1 - np.exp(-l1 / tau)) * (1 - np.exp(-l2 / tau)) * np.exp(-gap / tau) / (l1 * l2))


def r2(n, rho_bar, sigma, tau, cov):
    wins, hold = intervals(n)
    noise = rho_bar * S_MS * 1e-3 / W
    sy = np.array([[cov(a, b, sigma, tau) for b in wins] for a in wins]) + noise * np.eye(n)
    c = np.array([cov(a, hold, sigma, tau) for a in wins])
    v_g = cov(hold, hold, sigma, tau)
    return 1.0 - (v_g - c @ np.linalg.solve(sy, c)) / v_g


if __name__ == "__main__":
    print("t06 — R² của tải trung bình khoảng giữ theo số cửa sổ (A: lưới 0,01 s | B: công thức đóng)")
    print(f"{'ô':24s} | " + " ".join(f"{n:>13d}" for n in N_WIN) + " | tối đa lệch so với đáp án")
    for name, (rho_bar, sigma, tau) in CELLS.items():
        grid = [r2(n, rho_bar, sigma, tau, cov_grid) for n in N_WIN]
        closed = [r2(n, rho_bar, sigma, tau, cov_closed) for n in N_WIN]
        dev = max(abs(a - b) for a, b in zip(grid, REFERENCE[name]))
        print(f"{name:24s} | " + " ".join(f"{a:.3f} | {b:.3f}  " for a, b in zip(grid, closed)) + f" | {dev:.4f}")
        assert dev <= 0.005, f"{name}: lệch đáp án đối chiếu > 0,005"
        assert max(abs(a - b) for a, b in zip(grid, closed)) <= 0.005, "lưới và công thức đóng không khớp"
    print("Tự kiểm: khớp đáp án đối chiếu ±0,005; hai cách tính khớp nhau ±0,005.")
