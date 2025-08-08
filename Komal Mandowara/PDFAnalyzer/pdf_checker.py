import sys
import fitz  # PyMuPDF
import json

def is_pdf(file_path):
    return file_path.lower().endswith('.pdf')

def validate_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        return doc
    except:
        return None

def check_margins(page):
    # Page rect in points (1 inch = 72 pts)
    mediabox = page.rect
    cropbox = page.cropbox if hasattr(page, 'cropbox') else mediabox
    # We'll check margins by comparing cropbox and mediabox
    left_margin = cropbox.x0 - mediabox.x0
    right_margin = mediabox.x1 - cropbox.x1
    top_margin = cropbox.y0 - mediabox.y0
    bottom_margin = mediabox.y1 - cropbox.y1
    margins = [left_margin, right_margin, top_margin, bottom_margin]
    # Check if all margins approx 72 pts ±5 pts tolerance
    for m in margins:
        if abs(m - 72) > 5:
            return False
    return True

def analyze_fonts(doc):
    font_sizes = []
    font_families = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for line in b['lines']:
                    for span in line['spans']:
                        font_sizes.append(span['size'])
                        font_families.append(span['font'])
    # Check if all font sizes are 12 ±0.5 tolerance
    size_ok = all(abs(fs - 12) < 0.5 for fs in font_sizes)
    # Check font families contain "Times New Roman" (case insensitive)
    family_ok = any("times" in ff.lower() and "new" in ff.lower() and "roman" in ff.lower() for ff in font_families)
    return size_ok, family_ok

def detect_sections(doc):
    # Simple keyword search for each section on each page
    sections = {
        "technical_requirements": {"keywords": ["technical requirements"], "pages": set()},
        "budget": {"keywords": ["budget"], "pages": set()},
        "qualification": {"keywords": ["qualification"], "pages": set()}
    }

    for i, page in enumerate(doc):
        text = page.get_text("text").lower()
        for sec, data in sections.items():
            for kw in data["keywords"]:
                if kw in text:
                    data["pages"].add(i + 1)  # pages indexed from 1

    # Now count pages per section
    # Assume continuous pages from first occurrence to last occurrence (simple approach)
    result = {}
    for sec, data in sections.items():
        if data["pages"]:
            pages = data["pages"]
            min_page = min(pages)
            max_page = max(pages)
            count = max_page - min_page + 1
        else:
            count = 0
        result[sec] = count
    return result

def main(file_path):
    report = {
        "format": {
            "file_type": "fail",
            "font_size": "fail",
            "font_family": "fail",
            "margin": "fail"
        },
        "content": {
            "technical_requirements_pages": 0,
            "technical_requirements": "fail",
            "budget_pages": 0,
            "budget": "fail",
            "qualification_pages": 0,
            "qualification": "fail"
        }
    }

    # Check extension
    if not is_pdf(file_path):
        print(json.dumps(report, indent=2))
        return

    # Check valid PDF
    doc = validate_pdf(file_path)
    if not doc:
        print(json.dumps(report, indent=2))
        return
    report["format"]["file_type"] = "pass"

    # Font analysis
    size_ok, family_ok = analyze_fonts(doc)
    report["format"]["font_size"] = "pass" if size_ok else "fail"
    report["format"]["font_family"] = "pass" if family_ok else "fail"

    # Margin check (all pages must pass)
    margin_ok = all(check_margins(page) for page in doc)
    report["format"]["margin"] = "pass" if margin_ok else "fail"

    # Content section detection
    sections_pages = detect_sections(doc)
    # Update report and pass/fail according to limits
    limits = {
        "technical_requirements": 8,
        "budget": 4,
        "qualification": 4
    }
    for sec, max_pages in limits.items():
        pages = sections_pages.get(sec, 0)
        report["content"][f"{sec}_pages"] = pages
        report["content"][sec] = "pass" if 0 < pages <= max_pages else "fail"

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_checker.py <file.pdf>")
        sys.exit(1)
    main(sys.argv[1])
