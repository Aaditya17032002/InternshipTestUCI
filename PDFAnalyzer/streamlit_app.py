import streamlit as st
import tempfile
import json
import os
from dotenv import load_dotenv
from analyzer import analyze_pdf

# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title="PDF Compliance Analyzer", page_icon="📄")

st.title("PDF Compliance Analyzer")
st.markdown("Upload a PDF to check formatting and content compliance.")

# Check for Gemini API Key availability
if os.getenv("GEMINI_API_KEY"):
    st.success("Gemini API key loaded from environment.")
else:
    st.warning("Gemini API key not found. LLM-based section detection will be skipped.")

uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # Analyze PDF
    st.info("Analyzing PDF file with OCR and Gemini LLM if available...")
    report = analyze_pdf(tmp_path)

    # Show JSON Report
    st.subheader("Compliance Report")
    st.json(report)

    # Format Results
    st.subheader("Formatting Results")
    for key, val in report.get("format", {}).items():
        st.write(f"**{key.replace('_', ' ').capitalize()}**: {'Pass' if val == 'pass' else ' ' + str(val)}")

    # Section Results
    st.subheader("Section Length Validation")
    for section, val in report.get("content", {}).items():
        if section.endswith("_pages"):
            continue
        pages_key = section + "_pages"
        pages = report["content"].get(pages_key, "?")
        st.write(f"**{section.replace('_', ' ').capitalize()}**: {pages} pages → {'Pass' if val == 'pass' else 'Fail'}")

    # Option to download report
    st.download_button(
        label=" Download Report as JSON",
        data=json.dumps(report, indent=2),
        file_name="compliance_report.json",
        mime="application/json"
    )
