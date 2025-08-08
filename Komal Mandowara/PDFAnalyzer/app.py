import streamlit as st
import fitz  # PyMuPDF
import json
import tempfile
from io import BytesIO

def is_pdf(file_path):
    return file_path.lower().endswith('.pdf')

def validate_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        return doc
    except:
        return None

def check_margins(page):
    mediabox = page.rect
    cropbox = page.cropbox if hasattr(page, 'cropbox') else mediabox
    left_margin = cropbox.x0 - mediabox.x0
    right_margin = mediabox.x1 - cropbox.x1
    top_margin = cropbox.y0 - mediabox.y0
    bottom_margin = mediabox.y1 - cropbox.y1
    margins = [left_margin, right_margin, top_margin, bottom_margin]
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
    size_ok = all(abs(fs - 12) < 0.5 for fs in font_sizes)
    family_ok = any("times" in ff.lower() and "new" in ff.lower() and "roman" in ff.lower() for ff in font_families)
    return size_ok, family_ok

def detect_sections(doc):
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
                    data["pages"].add(i + 1)
    result = {}
    for sec, data in sections.items():
        if data["pages"]:
            min_page = min(data["pages"])
            max_page = max(data["pages"])
            count = max_page - min_page + 1
        else:
            count = 0
        result[sec] = count
    return result

def analyze_pdf(file_path):
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

    if not is_pdf(file_path):
        return report

    doc = validate_pdf(file_path)
    if not doc:
        return report
    report["format"]["file_type"] = "pass"

    size_ok, family_ok = analyze_fonts(doc)
    report["format"]["font_size"] = "pass" if size_ok else "fail"
    report["format"]["font_family"] = "pass" if family_ok else "fail"

    margin_ok = all(check_margins(page) for page in doc)
    report["format"]["margin"] = "pass" if margin_ok else "fail"

    sections_pages = detect_sections(doc)
    limits = {
        "technical_requirements": 8,
        "budget": 4,
        "qualification": 4
    }
    for sec, max_pages in limits.items():
        pages = sections_pages.get(sec, 0)
        report["content"][f"{sec}_pages"] = pages
        report["content"][sec] = "pass" if 0 < pages <= max_pages else "fail"

    return report

# Streamlit App UI
st.set_page_config(page_title="PDF Compliance Checker", layout="centered")
st.title("PDF Compliance Checker")
st.markdown("Upload your PDF to check for formatting and content compliance.")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    with st.spinner("Analyzing PDF..."):
        result = analyze_pdf(tmp_file_path)

    st.success("✅ Analysis Complete!")
    st.json(result)

    # Download JSON
    json_bytes = json.dumps(result, indent=2).encode('utf-8')
    st.download_button("📥 Download Report as JSON", data=json_bytes, file_name="report.json", mime="application/json")
