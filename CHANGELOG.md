# Changelog

All notable changes to this project will be documented in this file.

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
