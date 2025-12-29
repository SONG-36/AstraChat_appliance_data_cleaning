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
OUTPUT_PATH = "data/processed/processed_products_v2_4.csv"
POWER_TYPE_PATH = "data/processed/power_type_classification_v2_4.csv"


# ---------- Utils ----------

def load_power_type_map(path):
    power_map = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            power_map[row["image_id"]] = (
                row["device_power_type"],
                row["has_battery"] == "True"
            )
    return power_map


def normalize_raw_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\n", " ").replace("\r", " ")
    text = (
        text.replace("，", ",")
            .replace("：", ":")
            .replace("；", ";")
    )
    text = (
        text.replace(" v", "V")
            .replace(" w", "W")
            .replace(" g", "g")
    )
    return " ".join(text.split())


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

CHARGING_TIME_PATTERNS = [
    re.compile(r"充电时间[:：]?\s*约?\s*([\d\.]+)\s*(小时|h)", re.IGNORECASE),
    re.compile(r"快充\s*约?\s*([\d\.]+)\s*(小时|h)", re.IGNORECASE),
    re.compile(r"充电时间[:：]?\s*(\d+)\s*分钟"),
]

RUNTIME_PATTERNS = [
    re.compile(r"续航[:：]?\s*约?\s*(\d+)\s*分钟"),
]

WEIGHT_PATTERNS = [
    re.compile(r"产品净重[:：]?\s*(\d+)\s*g", re.IGNORECASE),
    re.compile(r"净重[:：]?\s*(\d+)\s*g", re.IGNORECASE),
]

COLOR_PATTERNS = [
    re.compile(r"产品颜色\s*[:：，,]?\s*([^\s，,]+)"),
    re.compile(r"颜色\s*[:：，,]?\s*([^\s，,]+)"),
]

COLOR_KEYWORDS = ["黑色", "白色", "灰色", "银色", "红色", "蓝色", "绿色"]


# ---------- Extractors ----------

def _extract(patterns, text, cast=str):
    for p in patterns:
        m = p.search(text)
        if m:
            return cast(m.group(1))
    return None


def extract_model(text): return _extract(MODEL_CN_PATTERNS, text)
def extract_voltage(text): return _extract(VOLTAGE_CN_PATTERNS, text, int)
def extract_power(text): return _extract(POWER_CN_PATTERNS, text, int)
def extract_weight(text): return _extract(WEIGHT_PATTERNS, text, int)


def extract_charging_time(text):
    for p in CHARGING_TIME_PATTERNS:
        m = p.search(text)
        if not m:
            continue
        value = float(m.group(1))
        unit = m.group(2) if len(m.groups()) > 1 else "分钟"
        return value if unit in ("小时", "h", "H") else round(value / 60, 2)
    return None


def extract_runtime(text):
    return _extract(RUNTIME_PATTERNS, text, int)


def extract_color(text):
    for p in COLOR_PATTERNS:
        m = p.search(text)
        if m:
            for c in COLOR_KEYWORDS:
                if c in m.group(1):
                    return c
    return None


# ---------- Main ----------

def run_cleaning():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    power_type_map = load_power_type_map(POWER_TYPE_PATH)

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
            "color",
            "device_power_type",
            "has_battery",
            "confidence",
            "status",
            "raw_ocr_text",
            "created_at",
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            raw_text = normalize_raw_text(row["raw_text"])
            confidence = float(row["confidence"])
            status = row["status"]

            device_power_type, has_battery = power_type_map.get(
                row["image_id"], ("unknown", False)
            )

            model = extract_model(raw_text)
            voltage_v = extract_voltage(raw_text)
            power_w = extract_power(raw_text)
            weight_g = extract_weight(raw_text)
            color = extract_color(raw_text)

            charging_time_h = None
            runtime_min = None

            if device_power_type == "battery":
                charging_time_h = extract_charging_time(raw_text)
                runtime_min = extract_runtime(raw_text)

            elif device_power_type == "battery_or_usb":
                charging_time_h = extract_charging_time(raw_text)

            # status gating
            if model is None or voltage_v is None or power_w is None:
                status = "partial"

            if device_power_type in ("battery", "battery_or_usb") and charging_time_h is None:
                status = "partial"

            writer.writerow({
                "image_id": row["image_id"],
                "model": model,
                "power_w": power_w,
                "voltage_v": voltage_v,
                "charging_time_h": charging_time_h,
                "runtime_min": runtime_min,
                "weight_g": weight_g,
                "color": color,
                "device_power_type": device_power_type,
                "has_battery": has_battery,
                "confidence": confidence,
                "status": status,
                "raw_ocr_text": raw_text,
                "created_at": datetime.utcnow().isoformat(),
            })


if __name__ == "__main__":
    run_cleaning()
