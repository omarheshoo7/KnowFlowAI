# Text Extraction

v1: No OCR — rely on files with embedded/selectable text.

Extraction sources
- PDF text layer: use `pdfminer.six` or `pikepdf` + `pdfplumber` for page-level extraction.
- DOCX: use `python-docx` or `docx2txt`.
- TXT: direct read and normalize encoding.

Cleaning
- Normalize whitespace, fix broken line breaks, remove headers/footers heuristically.
- Keep page/paragraph boundaries for citation anchors.

Edge cases
- Scanned PDFs (images-only): mark for manual processing and surface to users.
- Mixed content (images + text): extract text where available and flag pages with low text density.
