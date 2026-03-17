import io
import pdfplumber
import re


def extract_text_from_pdf(source) -> str:
    """
    Extract text from a PDF file.

    Args:
        source: Can be a file path (str), bytes, or a file-like object.

    Returns:
        Extracted and cleaned text string.
    """
    text_parts = []

    # Convert bytes to file-like object
    if isinstance(source, bytes):
        source = io.BytesIO(source)

    try:
        with pdfplumber.open(source) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

                # Fallback: try extracting from tables for complex layouts
                if not page_text:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                cells = [
                                    cell.strip() for cell in row if cell
                                ]
                                if cells:
                                    text_parts.append(" ".join(cells))
    except Exception as e:
        print(f"[PDF Extractor] Error reading PDF: {e}")
        return ""

    raw_text = "\n".join(text_parts)
    return _clean_text(raw_text)


def _clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Collapse multiple whitespace/newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    # Remove leading/trailing whitespace per line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return text.strip()
