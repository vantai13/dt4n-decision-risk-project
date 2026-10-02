"""n01 (L1.2) — Tự kiểm các ví dụ số của N-3 và N-4 (không dùng số ngẫu nhiên → không cần seed)."""
from scipy.stats import norm

# (1) Hai loại sự thật. Sandbox LÝ TƯỞNG thấy lợi ích kỳ vọng mu > 0 nên duyệt.
#     Lợi ích THỰC HIỆN I ~ N(mu, sd²) vì tương lai còn ngẫu nhiên.
mu, eps = 0.5, 0.5                                   # ms
for sd in (3.0, 1.0):
    p_neg = norm.cdf((0 - mu) / sd)                  # I < 0  (gồm cả vùng thờ ơ)
    p_fa = norm.cdf((-eps - mu) / sd)                # I < −ε : đây mới là "duyệt nhầm"
    p_mid = norm.cdf((eps - mu) / sd) - p_fa         # |I| ≤ ε : vùng thờ ơ
    print(f"sd={sd}: P(I<0)={p_neg:.4f}  P(I<-eps)={p_fa:.4f}  P(|I|<=eps)={p_mid:.4f}")
#     mong đợi sd=3: 0.4338 / 0.3694 / 0.1306 ; sd=1: 0.3085 / 0.1587 / 0.3413

# (2) Base rate: cùng một sandbox, P(hại | duyệt) đổi theo tỉ lệ đề xuất có hại.
catch, keep = 0.90, 0.90          # từ chối đúng 90% đề xuất hại; duyệt đúng 90% đề xuất lợi
for p_harm in (0.10, 0.50):
    harm_ok = p_harm * (1 - catch)                   # đề xuất hại mà bị duyệt
    good_ok = (1 - p_harm) * keep                    # đề xuất lợi được duyệt
    print(f"p_harm={p_harm}: P(hại|duyệt)={harm_ok / (harm_ok + good_ok):.4f}")   # 0.0122 và 0.1000
