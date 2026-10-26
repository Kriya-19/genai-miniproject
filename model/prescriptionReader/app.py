import cv2
import numpy as np
import pytesseract
import easyocr
import re
from typing import List, Tuple

class OCRProcessor:
    """OCR processing optimized for handwritten prescriptions"""

    def __init__(self):
        try:
            self.easy_reader = easyocr.Reader(['en'])
        except Exception:
            self.easy_reader = None

        self.tesseract_available = True
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, image_path: str):
        """Preprocess image for better OCR accuracy"""
        img = cv2.imread(image_path)

        # Convert to gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=10)

        # Sharpen
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(gray, -1, kernel)

        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(sharpened, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 15, 3)
        return thresh

    def extract_text_tesseract(self, image_path: str) -> List[Tuple[str, float]]:
        if not self.tesseract_available:
            return []

        processed = self.preprocess_image(image_path)
        data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)

        results = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            try:
                conf = float(data['conf'][i]) / 100.0
            except:
                conf = 0.0
            if text and conf > 0.1:
                results.append((text, conf))
        return results

    def extract_text_easyocr(self, image_path: str) -> List[Tuple[str, float]]:
        if not self.easy_reader:
            return []
        results = self.easy_reader.readtext(image_path, detail=1, paragraph=False)
        return [(text, conf) for (_, text, conf) in results]

    def extract_text_combined(self, image_path: str) -> List[Tuple[str, float]]:
        """Combine EasyOCR + Tesseract results"""
        tess_results = self.extract_text_tesseract(image_path)
        easy_results = self.extract_text_easyocr(image_path)
        combined = tess_results + easy_results

        # Debug output
        print("=== Tesseract OCR ===")
        for t, c in tess_results:
            print(t, c)
        print("=== EasyOCR ===")
        for t, c in easy_results:
            print(t, c)

        return combined


class MedicineExtractor:
    """Extract medicine names from OCR text"""

    def __init__(self, medicine_names: List[str]):
        self.ocr = OCRProcessor()
        self.medicine_names = [m.lower() for m in medicine_names]
        # Common medicine patterns
        self.medicine_patterns = [
            r'\b[A-Z][a-z]+(?:olol|pril|sartan|statin|cillin|mycin|oxacin)\b',
            r'\b[A-Z][a-z]{3,}\b',
            r'\b\d+\s*mg\b',
        ]

    def extract_medicines_from_image(self, image_path: str) -> List[str]:
        all_texts = self.ocr.extract_text_combined(image_path)
        potential = self.extract_potential_medicines(all_texts)
        matched = self.match_medicines_fuzzy(potential)
        return matched

    def extract_potential_medicines(self, text_results: List[Tuple[str, float]]) -> List[str]:
        potential_meds = []
        for text, _ in text_results:
            cleaned = re.sub(r'[^\w\s]', '', text)
            for word in cleaned.split():
                if len(word) > 3:
                    for pattern in self.medicine_patterns:
                        if re.search(pattern, word, re.IGNORECASE):
                            potential_meds.append(word.lower())
                            break
        return potential_meds

    def match_medicines_fuzzy(self, potential_meds: List[str]) -> List[str]:
        from fuzzywuzzy import process
        matched = []
        for med in potential_meds:
            best = process.extractOne(med, self.medicine_names, score_cutoff=70)
            if best:
                matched_name, score = best
                if matched_name not in matched:
                    matched.append(matched_name)
        return matched
