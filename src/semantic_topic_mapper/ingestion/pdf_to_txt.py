"""
Optional utility: convert a PDF file to plain text.

This is not part of the main ingestion pipeline. The pipeline ingests
normalized .txt files; if the source is a PDF, it must be converted to
text first (e.g. via this utility or an external tool). Use this module
when you need to produce a .txt file from a PDF for later ingestion.

Future considerations: layout-aware extraction, OCR for scanned PDFs,
and other file formats (DOCX, etc.) can be detailed separately.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def pdf_to_txt(
    pdf_path: Path | str,
    output_path: Optional[Path | str] = None,
    encoding: str = "utf-8",
) -> Path:
    """
    Extract text from a PDF and write it to a .txt file.

    Args:
        pdf_path: Path to the PDF file.
        output_path: Where to write the .txt file. If None, uses the same
            path as the PDF with extension changed to .txt.
        encoding: Encoding for the output .txt file.

    Returns:
        Path to the created .txt file.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ImportError: If pypdf is not installed.
    """
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError(
            "PDF conversion requires the pypdf package. Install with: pip install pypdf"
        ) from e

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if output_path is None:
        output_path = pdf_path.with_suffix(".txt")
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(pdf_path)
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        parts.append(text if text else "")

    full_text = "\n\n".join(parts)
    output_path.write_text(full_text, encoding=encoding)
    return output_path
