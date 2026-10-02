"""n01c (L1.2) — Hai nhánh GIỮ / ÁP DỤNG trên đường B, có và không dùng chung số ngẫu nhiên (CRN).

Câu hỏi: nếu chuyển một nhóm lưu lượng Δρ = 0,1 sang B (nền ρ = 0,85), lưu lượng đang có trên B chịu thêm bao nhiêu ms?
CRN     : hai nhánh dùng CÙNG chuỗi gói nền; nhánh áp dụng chỉ trộn thêm gói của nhóm được chuyển.
ĐỘC LẬP : nhánh áp dụng dùng chuỗi gói nền KHÁC (như chạy hai lần mô phỏng riêng rẽ).
Hàng đợi M/D/1/K dùng lại engine đã kiểm f04b.workload_after. Tải nền hằng (bỏ OU) cho gọn. Seed pilot 9101.
"""
import csv
from pathlib import Path

import numpy as np

from experiments.f04b_des_gap import workload_after

S = 1512 * 8 / 10e6                    # thời gian phục vụ một gói ở 10 Mb/s (s)
FULL = (83 - 1) * S                    # workload tối đa trước khi drop (K = 83)
WARM, H, N_PROBE = 2.0, 0.5, 101       # khởi động 2 s, khoảng chấm 0,5 s


def poisson_arrivals(rng, rho, T):
    return np.sort(rng.uniform(0.0, T, rng.poisson(rho * T / S)))


def mean_delay_ms(arr):
    """Delay TB (chờ + phục vụ) của probe ảo rải đều trong [WARM, WARM + H], bỏ probe bị drop."""
    if len(arr) == 0:
        return S * 1e3
    v_after = workload_after(arr, S, FULL)
    probes = WARM + np.linspace(0.0, H, N_PROBE)
    j = np.searchsorted(arr, probes, side="right") - 1
    jj = np.maximum(j, 0)
    v = np.where(j >= 0, np.maximum(v_after[jj] - (probes - arr[jj]), 0.0), 0.0)
    ok = v <= FULL
    if not ok.any():
        raise ValueError("Không có probe được nhận; không thể tính delay có điều kiện")
    return (v[ok] + S).mean() * 1e3


def main():
    rng = np.random.default_rng(9101)
    crn, ind, rows = [], [], []
    for trial in range(300):                                          # 300 lần kiểm độc lập
        bg = poisson_arrivals(rng, 0.85, WARM + H)                # gói nền của B
        moved = poisson_arrivals(rng, 0.10, WARM + H)             # gói của nhóm được chuyển
        keep = mean_delay_ms(bg)                                  # nhánh GIỮ
        crn.append(mean_delay_ms(np.sort(np.concatenate([bg, moved]))) - keep)        # ÁP DỤNG, cùng nền
        bg_other = poisson_arrivals(rng, 0.85, WARM + H)
        ind.append(mean_delay_ms(np.sort(np.concatenate([bg_other, moved]))) - keep)  # ÁP DỤNG, nền khác
        rows.append(dict(trial=trial, keep_ms=keep, apply_crn_ms=keep+crn[-1], apply_ind_ms=keep+ind[-1],
                         effect_crn_ms=crn[-1], effect_ind_ms=ind[-1], n_background=len(bg), n_moved=len(moved)))
    assert np.isfinite(crn).all() and np.isfinite(ind).all()
    for name, x in (("CRN", np.array(crn)), ("ĐỘC LẬP", np.array(ind))):
        print(f"{name:8s} TB={x.mean():5.2f} ms  sd={x.std():5.2f}  nhỏ nhất={x.min():6.2f}  P(hiệu ứng < 0)={np.mean(x < 0):.1%}")

    out = Path(__file__).resolve().parent / "results" / "n01c_crn_trials.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Đã lưu {len(rows)} cặp kết quả: {out.name}")
    print("Lưu ý: gói chuyển được thêm từ đầu warm-up; đây là so hai chế độ tải, chưa rẽ nhánh tại t từ cùng workload.")


if __name__ == "__main__":
    main()
