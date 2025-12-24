"""
Clean OCR text and extract structured product fields (V1).

This script converts raw OCR output into a minimal, stable
structured dataset suitable for first delivery.
"""

import csv
import re
from datetime import datetime


INPUT_PATH = "data/ocr/ocr_results.csv"
OUTPUT_PATH = "data/processed/processed_products_v1.csv"


MODEL_PATTERN = re.compile(r"Model\s+([A-Z0-9\-]+)", re.IGNORECASE)
POWER_PATTERN = re.compile(r"Power\s+(\d+)\s*W", re.IGNORECASE)
VOLTAGE_PATTERN = re.compile(r"Voltage\s+(\d+)\s*V", re.IGNORECASE)

# Chinese product model patterns
MODEL_CN_PATTERNS = [
    re.compile(r"产品型号[:：]?\s*([A-Z0-9\-]+)"),
    re.compile(r"型号[:：]?\s*([A-Z0-9\-]+)")
]
<<<<<<< HEAD
=======

VOLTAGE_CN_PATTERNS = [
    re.compile(r"额定电压[:：]?\s*(\d+)\s*V", re.IGNORECASE),
    re.compile(r"电压[:：]?\s*(\d+)\s*V", re.IGNORECASE),
]

POWER_CN_PATTERNS = [
    re.compile(r"额定功率[:：]?\s*(\d+)\s*W", re.IGNORECASE),
    re.compile(r"功率[:：]?\s*(\d+)\s*W", re.IGNORECASE),
]
>>>>>>> f79185a (feat: add Chinese product model extraction(v2.0))

def extract_model(text: str):
    match = MODEL_PATTERN.search(text)
    return match.group(1) if match else None

def extract_model_cn(text: str):
    """
    Extract product model from Chinese OCR text.
    Example matches:
    - 产品型号：P8828
    - 型号 P8828
    """
    for pattern in MODEL_CN_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None
<<<<<<< HEAD
=======

def extract_voltage_cn(text: str):
    """
    Extract voltage value from Chinese OCR text.
    Example matches:
    - 额定电压：5V
    - 电压 5V
    """
    for pattern in VOLTAGE_CN_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def extract_power_cn(text: str):
    """
    Extract power value from Chinese OCR text.
    Example matches:
    - 额定功率：4W
    - 功率 4W
    """
    for pattern in POWER_CN_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None
>>>>>>> f79185a (feat: add Chinese product model extraction(v2.0))

def extract_power(text: str):
    match = POWER_PATTERN.search(text)
    return int(match.group(1)) if match else None


def extract_voltage(text: str):
    match = VOLTAGE_PATTERN.search(text)
    return int(match.group(1)) if match else None


def run_cleaning():
    import os
    os.makedirs("data/processed", exist_ok=True)

    with open(INPUT_PATH, "r", encoding="utf-8") as infile, \
         open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = [
            "image_id",
            "model",
            "power_w",
            "voltage_v",
            "confidence",
            "status",
            "created_at",
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            raw_text = row["raw_text"]
            confidence = float(row["confidence"])
            status = row["status"]

            # Model extraction (EN -> CN)
            model = extract_model(raw_text)
            if model is None:
                model = extract_model_cn(raw_text)

<<<<<<< HEAD
            power_w = extract_power(raw_text)
=======
            # Voltage extraction (EN -> CN)
>>>>>>> f79185a (feat: add Chinese product model extraction(v2.0))
            voltage_v = extract_voltage(raw_text)
            if voltage_v is None:
                voltage_v = extract_voltage_cn(raw_text)

            # Power extraction (EN -> CN)
            power_w = extract_power(raw_text)
            if power_w is None:
                power_w = extract_power_cn(raw_text)

            # If critical fields are missing, downgrade status
            if model is None or power_w is None or voltage_v is None:
                status = "partial"

            writer.writerow({
                "image_id": row["image_id"],
                "model": model,
                "power_w": power_w,
                "voltage_v": voltage_v,
                "confidence": confidence,
                "status": status,
                "created_at": datetime.utcnow().isoformat(),
            })


if __name__ == "__main__":
    run_cleaning()
