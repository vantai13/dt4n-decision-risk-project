"""Dữ liệu đo từ dự án cũ phải còn nguyên vẹn, đọc được và đúng provenance."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

DATA_ROOT = Path(__file__).resolve().parents[1] / "data"
DATA = DATA_ROOT / "mininet_calibration"


@pytest.mark.parametrize("folder", ["mininet_calibration", "aoi_measured"])
def test_checksums_unchanged(folder):
    base = DATA_ROOT / folder
    lines = (base / "SHA256SUMS").read_text().strip().splitlines()
    assert lines, f"{folder}/SHA256SUMS rỗng"
    for line in lines:
        expected, name = line.split(maxsplit=1)
        actual = hashlib.sha256((base / name).read_bytes()).hexdigest()
        assert actual == expected, f"{folder}/{name} đã bị thay đổi!"


def test_truth_table_loads():
    t = pd.read_parquet(DATA / "truth_table.parquet")
    for col in ("mode", "bw", "q", "rho", "delay_mean_ms", "loss"):
        assert col in t.columns
    assert set(t["mode"]) >= {"cbr", "poisson", "h2"}


def test_aoi_estimates_meaning():
    """AoI không âm, phân vị tăng và chu kỳ collector xấp xỉ 0,5 s."""
    estimates = json.loads((DATA_ROOT / "aoi_measured" / "aoi_v7_estimates.json").read_text())
    assert estimates["schema"] == "dt4n.aoi.v7.estimates.v1"
    for mode in ("clean", "prod"):
        summary = estimates["modes"][mode]
        aoi = summary["aoi"]
        assert aoi["n_negative"] == 0
        assert 0 < aoi["p05"] < aoi["p50"] < aoi["p95"] < aoi["p99"] <= aoi["max"]
        assert abs(summary["effective_period"]["median_s"] - 0.5) < 0.01
