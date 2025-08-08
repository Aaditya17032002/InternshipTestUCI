import pdfplumber
import pytesseract
import os
import re
import requests
import base64
from dotenv import load_dotenv
load_dotenv() 

REQUIRED_FONT_SIZE = 12
REQUIRED_FONT = "Times New Roman"
REQUIRED_MARGIN_INCHES = 1

SECTION_LIMITS = {
    "technical requirements": 8,
    "budget": 4,
    "qualification": 4
}

GEMINI_API_KEY = os.getenv("")  # or hardcode if local
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def extract_text_with_ocr_fallback(pdf_path):
    extracted_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
            else:
                img = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(img)
                extracted_text.append(ocr_text)
    return extracted_text


def detect_sections_with_gemini(pages):
    content = "\n\n".join([f"Page {i+1}:\n{p}" for i, p in enumerate(pages)])
    prompt = f"""
You are a document analysis assistant. Detect the page ranges for the following sections in the text below:
- Technical Requirements
- Budget
- Qualification

Return the output as a JSON with section names and number of pages for each.
Example:
{{
  "technical requirements": 7,
  "budget": 3,
  "qualification": 4
}}

Text:
{content[:15000]}  # Truncate for token limits
"""

    response = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    if response.status_code == 200:
        try:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except Exception:
            return {}
    return {}


def analyze_pdf(file_path):
    if not file_path.endswith(".pdf"):
        return {"error": "Invalid file type. Only PDF allowed."}

    if not os.path.exists(file_path):
        return {"error": "File not found."}

    result = {
        "format": {
            "file_type": "pass",
            "font_size": "unknown",
            "font_family": "unknown",
            "margin": "unknown"
        },
        "content": {}
    }

    try:
        font_size_check = []
        font_family_check = []
        margin_check = True
        all_page_text = []

        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    img = page.to_image(resolution=300).original
                    text = pytesseract.image_to_string(img)

                all_page_text.append(text or "")

                # Font validation
                words = page.extract_words(extra_attrs=["size", "fontname"])
                for word in words:
                    if "size" in word:
                        font_size_check.append(round(float(word.get("size", 0))))
                    if "fontname" in word:
                        font_family_check.append(word.get("fontname", "").lower())

                # Margin check (content bounding box)
                bbox = page.bbox
                w, h = page.width, page.height
                if not (
                    bbox[0] >= 72 and bbox[1] >= 72 and
                    w - bbox[2] >= 72 and h - bbox[3] >= 72
                ):
                    margin_check = False

        # Font results
        if font_size_check:
            common_size = max(set(font_size_check), key=font_size_check.count)
            result["format"]["font_size"] = "pass" if common_size == REQUIRED_FONT_SIZE else "fail"

        if font_family_check:
            common_font = max(set(font_family_check), key=font_family_check.count)
            result["format"]["font_family"] = "pass" if REQUIRED_FONT.lower() in common_font else "fail"

        result["format"]["margin"] = "pass" if margin_check else "fail"

        # Gemini Section Detection
        gemini_sections = detect_sections_with_gemini(all_page_text)
        for section, max_pages in SECTION_LIMITS.items():
            pages = gemini_sections.get(section, 0)
            result["content"][f"{section.replace(' ', '_')}_pages"] = pages
            result["content"][section] = "pass" if 0 < pages <= max_pages else "fail"

    except Exception as e:
        result["error"] = f"Error processing PDF: {str(e)}"

    return result
