"""
Document processor: local PDF/CSV/Excel extract + optional Groq Llama 3.3 structuring.
Works without GROQ_API_KEY in extract-only mode.
"""

import os
from pathlib import Path

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert document processing assistant. You analyze documents and extract structured information clearly and professionally.

When processing invoices or bills, always extract:
- Vendor / Company name
- Invoice number
- Invoice date & due date
- Line items (description, quantity, unit price, total)
- Subtotal, tax, and total amount
- Currency
- Billing address
- Payment terms

Format your response cleanly using markdown:
- Use tables for structured data
- Use headings to organize sections
- Use bold for important values
- Be concise and professional - no filler phrases

If multiple documents are provided, process each one and clearly separate the results."""

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def _groq_client():
    key = (os.environ.get("GROQ_API_KEY") or "").strip()
    if not key:
        return None
    from groq import Groq
    return Groq(api_key=key)


def extract_pdf(path: Path) -> str:
    if not HAS_PDFPLUMBER:
        return f"[PDF: {path.name} - pdfplumber not installed]"
    lines = []
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            tables = page.extract_tables() or []
            if text:
                lines.append(f"--- Page {i+1} ---\n{text}")
            for table in tables:
                rows = [" | ".join(str(c or "") for c in row) for row in table]
                lines.append("\n".join(rows))
    return "\n\n".join(lines) or f"[No text found in {path.name}]"


def extract_csv_excel(path: Path) -> str:
    if not HAS_PANDAS:
        return f"[{path.name} - pandas not installed]"
    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(str(path))
        return df.to_markdown(index=False)
    else:
        result = []
        xf = pd.ExcelFile(str(path))
        for sheet in xf.sheet_names:
            df = xf.parse(sheet)
            result.append(f"**Sheet: {sheet}**\n{df.to_markdown(index=False)}")
        return "\n\n".join(result)


def extract_all(files: list[Path]) -> str:
    img_exts = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp"}
    parts = []

    for path in files:
        ext = path.suffix.lower()
        parts.append(f"\n### Document: {path.name}\n")

        if ext in img_exts:
            parts.append(
                f"[Image file: {path.name} - no OCR in this free demo. "
                "Please upload PDF, CSV, or Excel instead.]"
            )
        elif ext == ".pdf":
            parts.append(extract_pdf(path))
        elif ext in {".csv", ".xlsx", ".xls", ".xlsm"}:
            parts.append(extract_csv_excel(path))
        else:
            try:
                parts.append(path.read_text(encoding="utf-8", errors="replace")[:4000])
            except Exception:
                parts.append(f"[Could not read {path.name}]")

    return "\n".join(parts)


def process_documents(files: list[Path], task: str) -> str:
    extracted = extract_all(files)
    client = _groq_client()

    if client is None:
        # Honest extract-only mode for portfolio demos without secrets
        header = (
            "## Extract-only mode\n\n"
            "_No `GROQ_API_KEY` configured - showing local text/table extraction. "
            "Set `GROQ_API_KEY` on the host to enable Llama 3.3 structuring._\n\n"
            f"**Your task (noted):** {task}\n\n---\n"
        )
        if not files:
            return header + "_No files uploaded. Drop a PDF, CSV, or Excel file and try again._"
        return header + extracted

    full_content = extracted + f"\n\n---\n**Task:** {task}"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_content},
        ],
        max_tokens=4096,
    )
    return response.choices[0].message.content
