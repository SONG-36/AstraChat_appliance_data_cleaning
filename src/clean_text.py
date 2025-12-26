"""
Clean OCR text and extract structured product fields (V2).

Converts raw OCR output into a structured dataset suitable
for delivery or downstream analytics.
"""

import csv
import re
import os
from datetime import datetime


INPUT_PATH = "data/ocr/ocr_results.csv"
OUTPUT_PATH = "data/processed/processed_products_v2.csv"


# ---------- Regex patterns ----------

MODEL_CN_PATTERNS = [
    re.compile(r"产品型号[:：]?\s*([A-Z0-9\-]+)"),
    re.compile(r"型号[:：]?\s*([A-Z0-9\-]+)"),
]

VOLTAGE_CN_PATTERNS = [
    re.compile(r"额定电压[:：]?\s*(\d+)\s*V", re.IGNORECASE),
    re.compile(r"电压[:：]?\s*(\d+)\s*V", re.IGNORECASE),
]

POWER_CN_PATTERNS = [
    re.compile(r"额定功率[:：]?\s*(\d+)\s*W", re.IGNORECASE),
    re.compile(r"功率[:：]?\s*(\d+)\s*W", re.IGNORECASE),
]

CHARGING_TIME_CN_PATTERNS = [
    re.compile(r"充电时间[:：]?\s*([\d\.]+)\s*小时"),
    re.compile(r"快充\s*([\d\.]+)\s*小时"),
]

RUNTIME_CN_PATTERNS = [
    re.compile(r"续航[:：]?\s*约?\s*(\d+)\s*分钟"),
    re.compile(r"续航约(\d+)分钟"),
]

WEIGHT_CN_PATTERNS = [
    re.compile(r"产品净重[:：]?\s*(\d+)\s*g", re.IGNORECASE),
    re.compile(r"净重[:：]?\s*(\d+)\s*g", re.IGNORECASE),
]


# ---------- Extractors ----------

def _extract(patterns, text, cast_fn):
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return cast_fn(match.group(1))
    return None


def extract_model(text): return _extract(MODEL_CN_PATTERNS, text, str)
def extract_voltage(text): return _extract(VOLTAGE_CN_PATTERNS, text, int)
def extract_power(text): return _extract(POWER_CN_PATTERNS, text, int)
def extract_charging_time(text): return _extract(CHARGING_TIME_CN_PATTERNS, text, float)
def extract_runtime(text): return _extract(RUNTIME_CN_PATTERNS, text, int)
def extract_weight(text): return _extract(WEIGHT_CN_PATTERNS, text, int)


# ---------- Main ----------

def run_cleaning():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as infile, \
         open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = [
            "image_id",
            "model",
            "power_w",
            "voltage_v",
            "charging_time_h",
            "runtime_min",
            "weight_g",
            "confidence",
            "status",
            "raw_ocr_text",
            "created_at",
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            raw_text = row["raw_text"]
            confidence = float(row["confidence"])
            status = row["status"]

            model = extract_model(raw_text)
            voltage_v = extract_voltage(raw_text)
            power_w = extract_power(raw_text)

            charging_time_h = extract_charging_time(raw_text)
            runtime_min = extract_runtime(raw_text)
            weight_g = extract_weight(raw_text)

            if model is None or voltage_v is None or power_w is None:
                status = "partial"

            writer.writerow({
                "image_id": row["image_id"],
                "model": model,
                "power_w": power_w,
                "voltage_v": voltage_v,
                "charging_time_h": charging_time_h,
                "runtime_min": runtime_min,
                "weight_g": weight_g,
                "confidence": confidence,
                "status": status,
                "raw_ocr_text": raw_text,
                "created_at": datetime.utcnow().isoformat(),
            })


if __name__ == "__main__":
    run_cleaning()