"""V6: check telemetry ages received by FIX/SYM/FF on an already-seen seed.

Run: python -m experiments.gocheck.check_wiring
No SC/K2 tuning or outcome evaluation.
"""
from experiments.gocheck.info_arrangement import arrangement_inputs, load_info_worlds
from experiments.scan import go_test as g

EXPECTED = {
    "FIX": (("T", "C"), ("T", "C")),
    "SYM": (("T", "T"), ("T", "T")),
    "FF": (("T", "C"), ("C", "T")),
}


def label(age):
    return "T" if age < 2.0 else ("C" if age > 10.0 else "?")


def main():
    scenario = g.scenarios()[0][0]
    world = load_info_worlds(scenario, range(81001, 81021), "go0_test")[0]
    inputs = arrangement_inputs(world, scenario)
    ok_all = True
    print(f"{'bố trí':6s} {'luồng đang ở':12s} {'tuổi TB A':>10s} {'tuổi TB B':>10s}  thấy  mong đợi")
    for arrangement, expected in EXPECTED.items():
        for i, where in enumerate(("A", "B")):
            data = inputs[arrangement][i]
            age_a, age_b = data["age_A"].mean(), data["age_B"].mean()
            seen = (label(age_a), label(age_b))
            ok_all &= seen == expected[i]
            print(f"{arrangement:6s} {where:12s} {age_a:8.2f} s {age_b:8.2f} s  {''.join(seen):4s}  {''.join(expected[i])}")
    print("=> V6 nối dây:", "ĐẠT" if ok_all else "TRƯỢT — dừng lại, sửa twin_outputs/arrangement_inputs")
    if not ok_all:
        raise ValueError("V6 wiring failed; stop before opening new seeds.")


if __name__ == "__main__":
    main()
