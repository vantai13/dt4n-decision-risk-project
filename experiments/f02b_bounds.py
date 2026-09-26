"""f02b — Đọc lại F2 bằng cận trên (T3 §6). Không mô phỏng mới, không seed; chỉ đọc JSON của F2.

Chuỗi bất đẳng thức (dọc cùng quỹ đạo tham chiếu, decision-level):
    gain_tĩnh(α) ≤ gain_K2(α) ≤ gain_K2(∞) ≈ E[(Ī − c)+] ≤ headroom = E[(I_D − c)+]
Ba khoảng liên tiếp = giá trị THÍCH NGHI | giá của AN TOÀN | giá trị THÔNG TIN hoàn hảo.
Hệ quả cho SESOI:  gap ≤ headroom − gain_tĩnh            (trần CHẶT, đúng với mọi luật chỉ dùng F)
                   gap ≲ gain_K2(∞) − gain_tĩnh            (trần XẤP XỈ, với chất lượng thông tin F hiện có)
Trần < m nghĩa là phán quyết "không đáng kể" đã được định sẵn: ô đó không kiểm được giả thuyết nào.
"""
import json
from pathlib import Path

M_SESOI_MS = 8.1
RESULTS = Path(__file__).resolve().parent / "results" / "f02" / "f02_results.json"


def main():
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    print(f"{'ô (c = 0)':18s} {'thích nghi':>10s} {'an toàn':>8s} {'thông tin':>9s} | "
          f"{'trần chặt':>9s} {'trần x.xỉ':>9s} | phân loại theo m = {M_SESOI_MS} ms")
    n_testable = 0
    for name, res in data.items():
        r = res["0.0"]
        static, k2, k2_inf, head = (r[k][0] for k in ("gain_static", "gain_k2", "gain_k2_inf", "headroom"))
        strict, approx = head - static, k2_inf - static
        if strict < M_SESOI_MS:
            label = "KHÔNG THỂ đạt m"
        elif approx < M_SESOI_MS:
            label = "gần như không thể"
        else:
            label, n_testable = "kiểm được", n_testable + 1
        print(f"{name:18s} {k2 - static:10.3f} {k2_inf - k2:8.3f} {head - k2_inf:9.3f} | "
              f"{strict:9.3f} {approx:9.3f} | {label}")
    print(f"\nSố ô/biến thể thật sự kiểm được SESOI: {n_testable}/{len(data)}")


if __name__ == "__main__":
    main()
