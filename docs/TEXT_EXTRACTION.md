# Text Extraction

v1: No OCR — only files with an embedded/selectable text layer are supported.

## Implementation (Milestone 3)

| File type | Library | Notes |
|---|---|---|
| `.pdf` | PyMuPDF (`fitz`) | Page-level text via `page.get_text()` |
| `.docx` | `python-docx` | Paragraph-level join |
| `.txt` | built-in | `Path.read_text(encoding="utf-8")` |
| `.md` | built-in | Same as TXT |

## Extraction flow

1. File is saved to `backend/storage/uploads/` by `storage_service`.
2. `text_extraction_service.extract(path)` is called immediately after save.
3. Returns an `ExtractionResult` dataclass with:
   - `text` — full extracted string
   - `extraction_status` — `"success"` or `"failed"`
   - `message` — human-readable outcome
   - `text_length` — character count
   - `text_preview` — first 300 characters

## Scanned / image-based PDFs

If PyMuPDF extracts zero text from a PDF, the document is assumed to be scanned or image-only.
Response:

```json
{
  "extraction_status": "failed",
  "message": "This document appears to be scanned or image-based. KnowFlow AI v1 supports searchable documents only. OCR/document intelligence support may be added in a future version.",
  "text_length": 0,
  "text_preview": ""
}
```

## Whitespace normalisation

Three or more consecutive newlines are collapsed to two (`\n\n`). Leading/trailing whitespace is stripped.

## Edge cases

- Corrupted DOCX or PDF → caught, logged, `extraction_status: "failed"` returned.
- Empty document (valid format, no content) → `extraction_status: "failed"` with "appears to be empty" message.
- Mixed content PDFs (images + text) → text is extracted where available; no image content is processed.
