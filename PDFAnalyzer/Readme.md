# 📄 PDF Compliance Analyzer

The **PDF Compliance Analyzer** is a web-based tool built using **Streamlit**, which checks uploaded PDF documents for:

- ✅ **Formatting compliance** using `pdfplumber`
- 🔍 **OCR fallback** using `pytesseract`
- 🤖 **Section analysis** using Google's **Gemini Flash API (optional)**

This tool is ideal for validating documents such as project proposals, academic submissions, and tenders, based on formatting and content rules.

---

## ✨ Features

- **Font Size Check**: Ensures font size is `12pt`
- **Font Family Check**: Validates if the font is `Times New Roman`
- **Margin Check**: Detects if margins are at least `1 inch` on all sides
- **OCR Fallback**: Uses Tesseract for scanned/image PDFs
- **Section Detection (Optional)**: Uses Gemini Flash LLM to identify and evaluate:
  - Technical Requirements
  - Budget
  - Qualification
- **Fallback Mechanism**: If Gemini API is not available, app skips LLM-based validation

---

## 🧰 Tech Stack

- Python 3.9+
- Streamlit
- pdfplumber
- pytesseract
- Google Gemini API (optional)
- dotenv

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/pdf-compliance-analyzer.git
cd pdf-compliance-analyzer

## On Windows
python -m venv venv
venv\Scripts\activate

## On Mac/os
python3 -m venv venv
source venv/bin/activate

## Install
pip install -r requirements.txt

## Set Up .env
GEMINI_API_KEY=your_actual_gemini_api_key_here

## Run the App 
streamlit run streamlit_app.py


