import csv
from collections import Counter

FIELDS = ["model","voltage_v","power_w","charging_time_h","runtime_min","weight_g","color"]

counter = Counter()
total = 0

with open("data/processed/processed_products_v2.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        for f in FIELDS:
            if row.get(f):
                counter[f] += 1

print(f"Total rows: {total}")
for f in FIELDS:
    rate = counter[f] / total * 100 if total else 0
    print(f"{f:18}: {counter[f]:4} ({rate:.1f}%)")
