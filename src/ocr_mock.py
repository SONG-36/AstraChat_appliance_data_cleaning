"""
Mock OCR engine for pipeline testing.

Used to validate the end-to-end pipeline structure before
plugging in a real OCR engine.
"""

import random
from ocr_interface import OCRResult


class MockOCREngine:
    def recognize(self, image_path: str, image_id: str) -> OCRResult:
        confidence = round(random.uniform(0.55, 0.95), 2)
        status = "success" if confidence >= 0.80 else "partial"

        # Simulated realistic OCR output
        raw_text = (
            "产品型号：P8828 "
            "额定电压：5V "
            "额定功率：4W "
            "充电时间：1.5小时 "
            "续航约60分钟 "
            "产品净重：186g"
        )

        return OCRResult(
            image_id=image_id,
            raw_text=raw_text,
            confidence=confidence,
            status=status,
        )
