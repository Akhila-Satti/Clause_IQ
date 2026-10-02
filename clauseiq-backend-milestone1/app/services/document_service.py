from pathlib import Path

import fitz
from docx import Document as DocxDocument


ALLOWED_TYPES = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "txt",
}


def extract_pdf(path: Path) -> str:
    doc = fitz.open(path)
    try:
        return "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()


def extract_docx(path: Path) -> str:
    doc = DocxDocument(path)
    return "\n".join(
        paragraph.text.strip()
        for paragraph in doc.paragraphs
        if paragraph.text.strip()
    )


def extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_text(path: Path, extension: str) -> str:
    if extension == ".pdf":
        return extract_pdf(path)
    if extension == ".docx":
        return extract_docx(path)
    if extension == ".txt":
        return extract_txt(path)
    raise ValueError(f"Unsupported file type: {extension}")
