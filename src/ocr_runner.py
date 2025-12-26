"""
OCR runner.

Reads image_mapping.csv, applies OCR engine to each image,
and writes raw OCR results to a CSV file.
"""

import csv
import os

from ocr_mock import MockOCREngine


IMAGE_DIR = "data/images/extracted"
MAPPING_PATH = "data/mappings/image_mapping.csv"
OUTPUT_PATH = "data/ocr/ocr_results.csv"


def ensure_output_dir():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


def run_ocr():
    ensure_output_dir()
    engine = MockOCREngine()

    with open(MAPPING_PATH, "r", encoding="utf-8") as infile, \
         open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = ["image_id", "raw_text", "confidence", "status"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            image_id = row["image_id"]
            image_filename = row["image_filename"]
            image_path = os.path.join(IMAGE_DIR, image_filename)

            result = engine.recognize(image_path, image_id)

            writer.writerow({
                "image_id": result.image_id,
                "raw_text": result.raw_text,
                "confidence": result.confidence,
                "status": result.status,
            })


if __name__ == "__main__":
    run_ocr()
