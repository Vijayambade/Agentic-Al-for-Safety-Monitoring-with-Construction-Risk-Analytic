"""
=========================================================
Document Analyzer
=========================================================
"""

import io
import os
import shutil
import pdfplumber
import pytesseract
from PIL import Image

from core.ai import ask_ai, get_project_context,is_construction_document


# --------------------------------------------------------
# TESSERACT LOCATION
# --------------------------------------------------------
# Keeps working on Windows at the original hard-coded path.
# On macOS/Linux (or if Tesseract is on the PATH / installed
# elsewhere), it falls back to auto-detection so OCR doesn't
# silently break when the app is run outside Windows.

_WINDOWS_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(_WINDOWS_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT_PATH
else:
    _detected = shutil.which("tesseract")
    if _detected:
        pytesseract.pytesseract.tesseract_cmd = _detected
    # else: leave pytesseract's default, and extract_image_text()
    # will raise a clear error only if OCR is actually used.


# --------------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------------

def extract_pdf_text(uploaded_file):

    text = ""

    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    uploaded_file.seek(0)

    return text.strip()


# --------------------------------------------------------
# IMAGE OCR
# --------------------------------------------------------

def extract_image_text(uploaded_file):

    image = Image.open(uploaded_file)

    text = pytesseract.image_to_string(image)

    uploaded_file.seek(0)

    return text.strip()


# --------------------------------------------------------
# DOCUMENT EXTRACTION
# --------------------------------------------------------

def extract_document_text(uploaded_file):

    extension = uploaded_file.name.lower().split(".")[-1]

    if extension == "pdf":
        return extract_pdf_text(uploaded_file)

    elif extension in ["png", "jpg", "jpeg"]:
        return extract_image_text(uploaded_file)

    return ""


# --------------------------------------------------------
# AI DOCUMENT ANALYSIS
# --------------------------------------------------------

def analyze_document(project_name, document_text):
    if not is_construction_document(document_text):
        return """
        🚫 This uploaded file is not a construction document.
        Please upload:
        • Structural Drawing
        • Architectural Drawing
        • BOQ
        • Site Report
        • Contract
        • Material Estimate
        """
    project_context = get_project_context(project_name)

    prompt = f"""
You are an expert Construction Document Analyzer.

Your job is to analyze ONLY the uploaded document.

========================================================
SELECTED PROJECT
========================================================

{project_context}

========================================================
UPLOADED DOCUMENT CONTENT
========================================================

{document_text}

========================================================
TASK
========================================================

Step 1

Determine whether the uploaded document is actually related to construction.

Examples of VALID construction documents:

• Architectural Drawing
• Structural Drawing
• Foundation Drawing
• Site Layout
• BOQ (Bill of Quantities)
• Material Estimate
• Tender Document
• Construction Contract
• Site Inspection Report
• DPR
• Project Schedule
• Safety Checklist
• Quality Checklist
• Engineering Specification

Examples of INVALID documents:

• Resume
• CV
• Biography
• Medical Report
• Bank Statement
• Invoice unrelated to construction
• Newspaper
• Story
• College Assignment
• Examination Paper
• Personal Letter

--------------------------------------------------------

If the uploaded document is NOT a construction document,

reply ONLY:

🚫 This uploaded file is not a construction document.

Please upload one of the following:

• Construction Drawing
• BOQ
• Site Report
• Structural Drawing
• Contract
• Material Estimate
• Construction Specification

Do not generate any analysis.

--------------------------------------------------------

If it IS a construction document,

first determine whether it belongs to the selected project.

If it clearly belongs to another project,

reply:

⚠ This document appears to be a construction document,
but it does not belong to the selected project.

Then provide only a short summary of the uploaded document.

Do NOT mix information from the selected project.

--------------------------------------------------------

If the document belongs to the selected project,
generate a professional report with these sections.

1. Executive Summary

2. Drawing / Document Overview

3. Materials Mentioned

4. Construction Activities

5. Possible Risks

6. Missing Information

7. Safety Recommendations

8. Quality Control Checklist

9. Cost Saving Suggestions

10. Final Recommendations

========================================================
RULES
========================================================

• Analyze ONLY the uploaded document.

• Never invent information.

• Never assume information.

• If something is missing, write:
"Not Available in the Uploaded Document."

• Do not copy information from the selected project unless the uploaded document clearly belongs to that project.

• Keep the response under 400 words.

• Use professional headings.

• Use bullet points wherever appropriate.
"""

    return ask_ai(prompt)