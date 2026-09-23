"""Dữ liệu đo từ dự án cũ phải còn nguyên vẹn và đọc được."""
import hashlib
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "mininet_calibration"


def test_checksums_unchanged():
    lines = (DATA / "SHA256SUMS").read_text().strip().splitlines()
    assert lines, "SHA256SUMS rỗng"
    for line in lines:
        expected, name = line.split(maxsplit=1)
        actual = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
        assert actual == expected, f"{name} đã bị thay đổi!"


def test_truth_table_loads():
    t = pd.read_parquet(DATA / "truth_table.parquet")
    for col in ("mode", "bw", "q", "rho", "delay_mean_ms", "loss"):
        assert col in t.columns
    assert set(t["mode"]) >= {"cbr", "poisson", "h2"}
