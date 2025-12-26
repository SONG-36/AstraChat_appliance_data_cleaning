# src/ocr_tesseract.py
import pytesseract
from PIL import Image
from ocr_interface import OCRResult

class TesseractOCREngine:
    def recognize(self, image_path: str, image_id: str) -> OCRResult:
        try:
            img = Image.open(image_path)
            raw_text = pytesseract.image_to_string(img, lang="chi_sim")

            raw_text = raw_text.strip()
            confidence = 0.85 if raw_text else 0.0
            status = "success" if raw_text else "failed"

            return OCRResult(
                image_id=image_id,
                raw_text=raw_text,
                confidence=confidence,
                status=status,
            )

        except Exception as e:
            return OCRResult(
                image_id=image_id,
                raw_text="",
                confidence=0.0,
                status="failed",
            )
