# scripts/classify_power_type.py
"""
Classify device power type based on raw OCR text.

V2.4 Step 1:
- battery
- battery_or_usb
- mains
- unknown
"""

import csv
import os


INPUT_PATH = "data/ocr/ocr_results.csv"
OUTPUT_PATH = "data/processed/power_type_classification_v2_4.csv"


BATTERY_KEYWORDS = [
    "内置电池",
    "电池容量",
    "电池大小",
    "mAh",
    "续航",
    "充电时间",
]

BATTERY_OR_USB_KEYWORDS = [
    "USB",
    "Type-C",
    "充电接口",
]

MAINS_KEYWORDS = [
    "220V",
    "插电",
    "额定电压：220",
    "交流电",
]


def classify_power_type(text: str):
    """
    Classify power type from OCR text.

    Returns:
        (device_power_type, has_battery)
    """
    if not text:
        return "unknown", False

    t = text.lower()

    for kw in BATTERY_KEYWORDS:
        if kw.lower() in t:
            return "battery", True

    for kw in BATTERY_OR_USB_KEYWORDS:
        if kw.lower() in t:
            return "battery_or_usb", True

    for kw in MAINS_KEYWORDS:
        if kw.lower() in t:
            return "mains", False

    return "unknown", False


def run():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as infile, \
         open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = [
            "image_id",
            "device_power_type",
            "has_battery",
            "raw_ocr_text",
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            raw_text = row.get("raw_text", "")
            power_type, has_battery = classify_power_type(raw_text)

            writer.writerow({
                "image_id": row["image_id"],
                "device_power_type": power_type,
                "has_battery": has_battery,
                "raw_ocr_text": raw_text,
            })


if __name__ == "__main__":
    run()
