"""
Extract images from Word documents and generate an image-to-document mapping.

This script scans .docx files provided by e-commerce platforms, extracts
embedded product images, assigns stable image IDs, and records metadata
for downstream OCR and structured data processing.

Designed for batch processing in freelance and remote delivery scenarios.
"""

import os
import csv
from datetime import datetime
from docx import Document

# Input directory containing raw Word documents
RAW_DOC_DIR = "data/raw_docs"

# Output directory for extracted images
IMAGE_OUTPUT_DIR = "data/images/extracted"

# Mapping file that links images back to source documents
MAPPING_OUTPUT_PATH = "data/mappings/image_mapping.csv"


def ensure_directories():
    """
    Ensure all required output directories exist before processing.
    """
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(MAPPING_OUTPUT_PATH), exist_ok=True)


def extract_images_from_docx(doc_path, doc_id, writer):
    """
    Extract embedded images from a single Word document.

    Each extracted image is saved with a generated filename and recorded
    in the mapping file to maintain traceability between documents and images.
    """
    document = Document(doc_path)
    image_index = 0

    # Iterate over document relationships to locate embedded images
    for rel in document.part._rels.values():
        if "image" in rel.reltype:
            image_index += 1
            image_blob = rel.target_part.blob

            image_id = f"{doc_id}_img_{image_index:03d}"
            image_filename = f"{image_id}.png"
            image_path = os.path.join(IMAGE_OUTPUT_DIR, image_filename)

            # Save image binary data to disk
            with open(image_path, "wb") as f:
                f.write(image_blob)

            # Record image-to-document mapping metadata
            writer.writerow({
                "image_id": image_id,
                "source_document": os.path.basename(doc_path),
                "image_filename": image_filename,
                "image_index": image_index,
                "extraction_time": datetime.utcnow().isoformat()
            })


def main():
    """
    Main entry point for batch image extraction.

    Scans all Word documents in the input directory and processes them
    sequentially to produce extracted images and a unified mapping file.
    """
    ensure_directories()

    with open(MAPPING_OUTPUT_PATH, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "image_id",
            "source_document",
            "image_filename",
            "image_index",
            "extraction_time"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, filename in enumerate(os.listdir(RAW_DOC_DIR), start=1):
            if not filename.lower().endswith(".docx"):
                continue

            doc_id = f"doc_{idx:03d}"
            doc_path = os.path.join(RAW_DOC_DIR, filename)

            extract_images_from_docx(doc_path, doc_id, writer)


if __name__ == "__main__":
    main()