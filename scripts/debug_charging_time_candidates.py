"""
Debug script: find charging-time related OCR texts.

This script scans raw OCR results and prints rows that
likely contain charging time information, so we can
manually analyze expression patterns before improving regex.
"""

import csv

INPUT_PATH = "data/ocr/ocr_results.csv"

# Keywords that may indicate charging time
KEYWORDS = [
    "充电",
    "快充",
    "小时",
    "h",
    "H",
]

def contains_any_keyword(text: str) -> bool:
    if not text:
        return False
    return any(keyword in text for keyword in KEYWORDS)


def main():
    total = 0
    matched = 0

    with open(INPUT_PATH, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            total += 1
            raw_text = row.get("raw_text", "")

            if contains_any_keyword(raw_text):
                matched += 1
                print("=" * 80)
                print(f"image_id : {row.get('image_id')}")
                print(f"confidence: {row.get('confidence')}")
                print(f"status    : {row.get('status')}")
                print("- raw_text ----------------------------------------")
                print(raw_text.strip())
                print()

    print("=" * 80)
    print(f"Total rows    : {total}")
    print(f"Matched rows : {matched}")
    print(f"Match ratio  : {matched / total * 100:.2f}%")


if __name__ == "__main__":
    main()
