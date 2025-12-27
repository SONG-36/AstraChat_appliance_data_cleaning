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

COLOR_KEYWORDS = [
    "黑色", "白色", "灰色", "银色",
    "红色", "蓝色", "绿色",
]

def infer_power_source(voltage_v, charging_time_h):
    """
    Infer device power source based on extracted specs.
    """

    if charging_time_h is not None:
        return "battery", True

    if voltage_v is not None:
        if voltage_v <= 5:
            return "battery_or_usb", True
        if voltage_v >= 12:
            return "mains", False

    return "unknown", False

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
    # 标准：充电时间：1.5小时
    re.compile(r"充电时间[:：]?\s*([\d\.]+)\s*(小时|h)", re.IGNORECASE),

    # 快充1.5小时
    re.compile(r"快充\s*([\d\.]+)\s*(小时|h)", re.IGNORECASE),

    # 容错：时间 1.5B（OCR 把 小时 识成 B）
    re.compile(r"时间\s*([\d\.]+)\s*[bB]", re.IGNORECASE),
]

RUNTIME_CN_PATTERNS = [
    # 标准：续航约60分钟 / 续航60分钟
    re.compile(r"续航[:：]?\s*约?\s*(\d+)\s*分钟"),

    # 续航时间60分钟
    re.compile(r"续航时间[:：]?\s*(\d+)\s*分钟"),
]


WEIGHT_NET_CN_PATTERNS = [
    # 产品净重：186g
    re.compile(r"产品净重[:：]?\s*(\d+)\s*g", re.IGNORECASE),

    # 净重：186g
    re.compile(r"净重[:：]?\s*(\d+)\s*g", re.IGNORECASE),
]

COLOR_CN_PATTERNS = [
    re.compile(r"产品颜色\s*[:：，,]?\s*([^\s，,]+)"),
    re.compile(r"颜色\s*[:：，,]?\s*([^\s，,]+)"),
]

# ---------- Fallback numeric patterns ----------

VOLTAGE_FALLBACK_PATTERNS = [
    re.compile(r"\b(\d{1,3})\s*V\b", re.IGNORECASE),
]

POWER_FALLBACK_PATTERNS = [
    re.compile(r"\b(\d{1,4})\s*W\b", re.IGNORECASE),
]

WEIGHT_FALLBACK_PATTERNS = [
    re.compile(r"\b(\d{2,5})\s*(g|sg)\b", re.IGNORECASE),
]

# ---------- Extractors ----------
def normalize_raw_text(text: str) -> str:
    """
    Light normalization for OCR raw text.
    Goal: improve regex match rate without losing information.
    """

    if not text:
        return ""

    # 1. 统一换行为空格
    text = text.replace("\n", " ").replace("\r", " ")

    # 2. 中文标点统一
    text = (
        text.replace("，", ",")
            .replace("：", ":")
            .replace("；", ";")
    )

    # 3. 单位前后的多余空格
    text = (
        text.replace(" v", "V")
            .replace(" w", "W")
            .replace(" g", "g")
    )

    # 4. 多空格压缩
    text = " ".join(text.split())

    return text

def _extract(patterns, text, cast_fn):
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return cast_fn(match.group(1))
    return None

def extract_with_fallback(primary_patterns, fallback_patterns, text, cast_fn):
    # 1. Try strong patterns
    for p in primary_patterns:
        m = p.search(text)
        if m:
            return cast_fn(m.group(1))

    # 2. Try fallback numeric patterns
    for p in fallback_patterns:
        m = p.search(text)
        if m:
            return cast_fn(m.group(1))

    return None

def extract_model(text): return _extract(MODEL_CN_PATTERNS, text, str)
def extract_voltage(text):
    return extract_with_fallback(
        VOLTAGE_CN_PATTERNS,
        VOLTAGE_FALLBACK_PATTERNS,
        text,
        int,
    )


def extract_power(text):
    return extract_with_fallback(
        POWER_CN_PATTERNS,
        POWER_FALLBACK_PATTERNS,
        text,
        int,
    )


def extract_weight(text):
    return extract_with_fallback(
        WEIGHT_NET_CN_PATTERNS,
        WEIGHT_FALLBACK_PATTERNS,
        text,
        int,
    )

def extract_charging_time(text: str):
    for pattern in CHARGING_TIME_CN_PATTERNS:
        match = pattern.search(text)
        if match:
            return float(match.group(1))
    return None

def extract_runtime(text: str):
    for pattern in RUNTIME_CN_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None

def extract_color(text: str):
    for pattern in COLOR_CN_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1)
            for color in COLOR_KEYWORDS:
                if color in candidate:
                    return color
    return None

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
            "color",
            "confidence",
            "status",
            "raw_ocr_text",
            "created_at",
            "power_source",
            "battery_possible"
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            raw_text = normalize_raw_text(row["raw_text"])
            confidence = float(row["confidence"])
            status = row["status"]

            model = extract_model(raw_text)
            voltage_v = extract_voltage(raw_text)
            power_w = extract_power(raw_text)

            charging_time_h = extract_charging_time(raw_text)
            runtime_min = extract_runtime(raw_text)
            weight_g = extract_weight(raw_text)
            color = extract_color(raw_text)
            power_source, battery_possible = infer_power_source(
                voltage_v,
                charging_time_h
            )


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
                "color": color,
                "confidence": confidence,
                "status": status,
                "raw_ocr_text": raw_text,
                "power_source": power_source,
                "battery_possible": battery_possible,
                "created_at": datetime.utcnow().isoformat(),
            })

if __name__ == "__main__":
    run_cleaning()