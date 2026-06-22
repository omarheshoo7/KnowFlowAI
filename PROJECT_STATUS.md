# Project Status — KnowFlow AI

Milestone: 3 (Text Extraction)

Summary
- Status: Complete.
- Deliverables: Text extraction service for all supported file types, integrated into the upload endpoint.

What was built
- `backend/app/services/text_extraction_service.py` — Extraction for PDF (PyMuPDF), DOCX (python-docx), TXT, MD.
- `backend/app/schemas/document.py` — Extended with extraction_status, text_length, text_preview fields.
- `backend/app/api/routes/documents.py` — Upload route now calls extraction after save.
- `backend/tests/test_text_extraction.py` — 13 new tests (unit + integration) for all file types.
- Added `pymupdf` and `python-docx` to requirements.txt.

Extraction behaviour
- Searchable PDF, DOCX, TXT, MD → extraction_status: "success"
- Scanned/blank PDF → extraction_status: "failed" with clear OCR message
- text_preview capped at 300 characters

Open items
- Decide primary vector DB for v1 (options: Pinecone, Weaviate, FAISS).
- Choose embedding provider (OpenAI or open-source alternative).

Next milestone
- Milestone 4: Text chunking — split extracted text into overlapping chunks for embedding.
