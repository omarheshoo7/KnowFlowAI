# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - Milestone 4 — Text Chunking
- Added `chunking_service` with word-based overlapping chunk splitting.
- Default: chunk_size_words=500, chunk_overlap_words=100 (step=400).
- Each chunk carries chunk_index, text, word_count, character_count.
- Extended `DocumentUploadResponse` schema with `chunk_count`.
- Upload route calls chunking after successful extraction; chunk_count=0 on failure.
- Upload success message updated to include "chunked".
- Added 18 new tests (unit + integration); 47 total, all passing.
- Updated CLAUDE.md milestone state.

## [0.4.0] - Milestone 3 — Text Extraction
- Added `text_extraction_service` supporting PDF (PyMuPDF/fitz), DOCX (python-docx), TXT, and Markdown.
- Scanned/image-based PDFs are detected and return a clear rejection message instead of empty text.
- Extended `DocumentUploadResponse` schema with `extraction_status`, `text_length`, and `text_preview`.
- Upload endpoint now extracts text immediately after saving the file.
- `text_preview` is capped at 300 characters.
- Added `pymupdf==1.24.5` and `python-docx==1.1.2` to requirements.txt.
- Added 13 new tests (unit + integration); 29 total, all passing.
- Updated CLAUDE.md milestone state.

## [0.3.0] - Milestone 2 — Document Upload and File Validation
- Added `POST /api/documents/upload` endpoint.
- Added extension validation — accepts .pdf, .docx, .txt, .md; rejects all others with HTTP 400.
- Added `StorageService` that saves uploads to `backend/storage/uploads/` with UUID-based filenames.
- Added `DocumentUploadResponse` Pydantic schema.
- Added `python-multipart` dependency for multipart file uploads.
- Added `.gitignore` rule to exclude uploaded files but track the uploads folder.
- Added 13 pytest tests covering all success and rejection cases (16 total, all passing).

## [0.2.0] - Milestone 1 — Backend Foundation
- Created FastAPI backend scaffold under `backend/`.
- Added `GET /api/health` endpoint returning status, service name, and version.
- Added CORS middleware with configurable allowed origins.
- Added Pydantic settings loaded from environment variables.
- Added basic stdout logging setup.
- Added `requirements.txt`, `requirements-dev.txt`, and `.env.example`.
- Added pytest test suite covering the health endpoint.

## [0.1.0] - Milestone 0 — Documentation scaffold
- Created project documentation and planning structure.
- Added PRD, architecture, RAG pipeline, ingestion, vector DB, and testing strategy docs.
