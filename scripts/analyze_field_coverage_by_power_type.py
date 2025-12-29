import csv
from collections import defaultdict

INPUT_PATH = "data/processed/processed_products_v2_4.csv"


FIELDS_TO_ANALYZE = [
    "charging_time_h",
    "runtime_min",
    "power_w",
    "voltage_v",
    "weight_g",
    "color",
]


def run():
    groups = defaultdict(list)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            groups[row["device_power_type"]].append(row)

    for power_type, rows in groups.items():
        print(f"\n=== {power_type} ===")
        total = len(rows)
        print(f"Total rows: {total}")

        for field in FIELDS_TO_ANALYZE:
            filled = sum(
                1 for r in rows
                if r.get(field) not in ("", None)
            )
            ratio = filled / total * 100 if total else 0
            print(f"{field:18}: {filled:4d} ({ratio:.1f}%)")


if __name__ == "__main__":
    run()