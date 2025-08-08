
# 📄 PDF Compliance Analyzer

A Python-based tool that automatically validates uploaded PDF documents against predefined formatting and content rules. Useful for organizations that enforce strict proposal document standards.

---

## 🎯 Features

- ✅ **File Format Validation**
  - Accepts only `.pdf` files
  - Rejects invalid or corrupted PDFs

- 🖋️ **Formatting Checks**
  - Font size must be exactly **12 pt**
  - Font family must be **Times New Roman**
  - Margins must be **1 inch** on all sides

- 📚 **Content Section Detection**
  - Required sections:
    - **Technical Requirements** (Max 8 pages)
    - **Budget** (Max 4 pages)
    - **Qualification** (Max 4 pages)
  - Detects sections using keyword matching
  - Counts number of pages per section

- 🧾 **Compliance Report**
  - Outputs a structured JSON summary of all validation results
  - Sample:
```json
{
  "format": {
    "file_type": "pass",
    "font_size": "pass",
    "font_family": "fail",
    "margin": "pass"
  },
  "content": {
    "technical_requirements_pages": 9,
    "technical_requirements": "fail",
    "budget_pages": 3,
    "budget": "pass",
    "qualification_pages": 4,
    "qualification": "pass"
  }
}
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-compliance-analyzer.git
cd pdf-compliance-analyzer
```

### 2. Install Requirements

```bash
pip install pymupdf PyPDF2
```

> Optional for OCR (scanned PDFs):
```bash
sudo apt install tesseract-ocr
pip install pytesseract Pillow
```

---

## 🔎 Usage

### Run in Python

```bash
python pdf_compliance_analyzer.py
```

### Run in Google Colab

- Open the Colab notebook.
- Upload your PDF.
- View and download the JSON report.

---

## 📁 File Structure

- `pdf_compliance_analyzer.py` – Main script
- `sample_proposal.pdf` – Valid test PDF
- `invalid_file.pdf` – Corrupted test file
- `compliance_report.json` – Output report

---

## ⚠️ Known Limitations

- Section detection is keyword-based (can be improved using LLMs or layout analysis)
- Margins are detected based on standard US Letter size
- No visual annotations yet (planned feature)

---

## 📌 License

MIT License

---

## 👨‍💻 Author

Made by [Mohit](https://github.com/yourusername) – feel free to contribute or report issues!
