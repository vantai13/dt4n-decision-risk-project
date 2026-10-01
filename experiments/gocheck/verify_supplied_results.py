"""Compare local printed measurements with the sandbox values supplied by the user."""
import re
from pathlib import Path

OUT = Path("results/gocheck")


def main():
    fresh = (OUT / "fresh_output.txt").read_text()
    actual = [tuple(map(float, values)) for values in re.findall(
        r"delay\(SC\) − delay\(K2\) = ([+\-\d.]+) \[([+\-\d.]+), ([+\-\d.]+)\]", fresh
    )]
    expected = [(1.506, 1.229, 1.784), (.118, .020, .216),
                (.681, .411, .950), (.681, .411, .950)]
    if actual != expected:
        raise ValueError(f"Fresh mismatch: {actual}")
    for fragment in ("luôn ở A = 13.914 ms", "oracle nhìn trước = 2.579 ms",
                     "delay TB  5.675 ms", "delay TB  4.168 ms",
                     "harm 0.92·α", "harm 1.07·α"):
        if fragment not in fresh:
            raise ValueError(f"Fresh missing: {fragment}")
    print("PASS fresh: all four delay-difference CIs, primary delay/harm and scale.")

    info = (OUT / "info_outcome_output.txt").read_text()
    blocks = re.split(r"--- cooldown\s+(\d+) s · α = ([\d.]+) ---", info)
    expected = {
        (0, .002): {"FIX": (5.770, 4.024, 1.746, 1.427, 2.066),
                    "SYM": (2.785, 2.632, .153, .139, .167),
                    "FF": (3.289, 3.483, -.193, -.291, -.095)},
        (30, .002): {"FIX": (.641, .218, 1.065),
                     "SYM": (.155, -.048, .358), "FF": (-.151, -.308, .006)},
    }
    checked = set()
    for i in range(1, len(blocks), 3):
        key = (int(blocks[i]), float(blocks[i + 1]))
        block = blocks[i + 2]
        for arrangement, target in expected.get(key, {}).items():
            line = next(line for line in block.splitlines()
                        if line.strip().startswith(arrangement + " "))
            match = re.search(
                r"SC\s+([\d.]+) ms.*K2\s+([\d.]+) ms.*SC−K2 ([+\-\d.]+) \[([+\-\d.]+), ([+\-\d.]+)\]", line
            )
            values = tuple(map(float, match.groups()))
            if (values if len(target) == 5 else values[2:]) != target:
                raise ValueError(f"Info mismatch: {key}, {arrangement}: {values}")
            checked.add((key, arrangement))
    if len(checked) != 6:
        raise ValueError("Missing info result blocks.")
    for fragment in ("+1.593 [+1.273, +1.913]", "+1.940 [+1.582, +2.297]"):
        if fragment not in info:
            raise ValueError(f"Info contrast mismatch: {fragment}")
    print("PASS info: FIX/SYM/FF primary and cooldown CIs, primary differences-in-differences.")

    errors = (OUT / "posthoc_switch_errors_output.txt").read_text()
    targets = {"FIX SC": (36.9, 6.4, 14.5, 16.4),
               "FIX K2": (17.0, 3.3, 8.5, 9.1),
               "FF SC": (111.5, 116.1, 18.4, 70.9),
               "FF K2": (107.2, 93.9, 15.1, 62.0)}
    for line, (name, target) in zip(errors.splitlines(), targets.items()):
        if " ".join(line.split()[:2]).rstrip(":") != name:
            raise ValueError(f"Unexpected posthoc label: {line}")
        match = re.search(r"trung vị\s+([\d.]+) →\s+([\d.]+)\).*ĐÍCH: dự đoán TB\s+([\d.]+) → thật\s+([\d.]+)", line)
        if tuple(map(float, match.groups())) != target:
            raise ValueError(f"Posthoc mismatch: {name}")
    if len(errors.splitlines()) != 4:
        raise ValueError("Missing posthoc rows.")
    print("PASS posthoc: all four switch-time error rows match the supplied table.")
    print("Match at published rounding precision; sandbox raw data/commit are not available locally.")


if __name__ == "__main__":
    main()
