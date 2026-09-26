"""Render the preregistered c=0 F2 gap map from the saved JSON."""

import json
from pathlib import Path

import matplotlib.pyplot as plt

RESULT = Path("experiments/results/f02/f02_results.json")
OUTPUT = Path("experiments/results/f02/f02_gap.png")
M_SESOI_MS = 8.1


if __name__ == "__main__":
    data = json.loads(RESULT.read_text())
    names = [name for name in data if name.startswith(("K11_", "K100_"))]
    gaps = [data[name]["0.0"]["gap"][0] for name in names]
    half_widths = [data[name]["0.0"]["gap"][1] for name in names]
    colors = ["#4477AA" if name.startswith("K11_") else "#CC6677" for name in names]

    fig, axis = plt.subplots(figsize=(12, 5.5))
    axis.errorbar(
        range(len(names)), gaps, yerr=half_widths, fmt="none", ecolor="0.35", capsize=3
    )
    axis.scatter(range(len(names)), gaps, c=colors, s=30, zorder=3)
    axis.axhline(M_SESOI_MS, color="black", linestyle="--", label="SESOI m = 8.1 ms")
    axis.axhline(0, color="0.6", linewidth=0.8)
    axis.set_xticks(range(len(names)), names, rotation=65, ha="right", fontsize=8)
    axis.set_ylabel("K2 − static gain (ms/epoch), mean ± CI95 half-width")
    axis.set_title("F2 surrogate: every preregistered cell remains below the absolute SESOI")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT, dpi=180)
