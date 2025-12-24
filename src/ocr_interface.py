"""
OCR interface definition.

This module defines a standard OCR interface so the pipeline remains
engine-agnostic. You can swap OCR engines (local OCR / cloud OCR)
without changing downstream cleaning and schema logic.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class OCRResult:
    """Standard OCR output for a single image."""
    image_id: str
    raw_text: str
    confidence: float  # 0.0 ~ 1.0
    status: str        # success / partial / failed


class OCREngine(Protocol):
    """Standard OCR engine interface."""

    def recognize(self, image_path: str, image_id: str) -> OCRResult:
        """
        Run OCR on one image.

        Args:
            image_path: Path to the extracted image file.
            image_id: Stable ID from image_mapping.csv (e.g., doc_001_img_001)

        Returns:
            OCRResult with raw text, confidence, and status.
        """
        ...
