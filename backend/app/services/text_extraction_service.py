import re
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

PREVIEW_LENGTH = 300

SCANNED_PDF_MESSAGE = (
    "This document appears to be scanned or image-based. "
    "KnowFlow AI v1 supports searchable documents only. "
    "OCR/document intelligence support may be added in a future version."
)


@dataclass
class ExtractionResult:
    text: str
    extraction_status: str  # "success" | "failed"
    message: str
    text_length: int
    text_preview: str


def extract(file_path: Path) -> ExtractionResult:
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf(file_path)
        elif suffix == ".docx":
            return _extract_docx(file_path)
        elif suffix in {".txt", ".md"}:
            return _extract_plaintext(file_path)
        else:
            return _failed(f"Unsupported file type '{suffix}' for extraction.")
    except Exception as exc:
        logger.warning("Unexpected extraction error for %s: %s", file_path.name, exc)
        return _failed(f"Text extraction failed unexpectedly: {exc}")


def _extract_pdf(path: Path) -> ExtractionResult:
    import fitz  # PyMuPDF

    try:
        doc = fitz.open(str(path))
        pages_text = [page.get_text() for page in doc]
        doc.close()
    except Exception as exc:
        logger.warning("Could not open PDF %s: %s", path.name, exc)
        return _failed(f"Could not open PDF: {exc}")

    text = _normalize("".join(pages_text))
    if not text:
        return ExtractionResult(
            text="",
            extraction_status="failed",
            message=SCANNED_PDF_MESSAGE,
            text_length=0,
            text_preview="",
        )
    return _success(text)


def _extract_docx(path: Path) -> ExtractionResult:
    from docx import Document

    try:
        doc = Document(str(path))
        text = "\n".join(para.text for para in doc.paragraphs)
    except Exception as exc:
        logger.warning("Could not read DOCX %s: %s", path.name, exc)
        return _failed(f"Could not read DOCX: {exc}")

    text = _normalize(text)
    if not text:
        return _failed("Document was uploaded but appears to be empty.")
    return _success(text)


def _extract_plaintext(path: Path) -> ExtractionResult:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        logger.warning("Could not read file %s: %s", path.name, exc)
        return _failed(f"Could not read file: {exc}")

    text = _normalize(text)
    if not text:
        return _failed("Document was uploaded but appears to be empty.")
    return _success(text)


def _normalize(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _success(text: str) -> ExtractionResult:
    return ExtractionResult(
        text=text,
        extraction_status="success",
        message="Document uploaded and text extracted successfully",
        text_length=len(text),
        text_preview=text[:PREVIEW_LENGTH],
    )


def _failed(message: str) -> ExtractionResult:
    return ExtractionResult(
        text="",
        extraction_status="failed",
        message=message,
        text_length=0,
        text_preview="",
    )
