# KnowFlow AI

## Project Summary

KnowFlow AI is a full-stack RAG knowledge-base platform for searchable business documents. It allows users to upload text-native documents, extract text without OCR, chunk content, create embeddings, store vectors, ask questions, and receive cited AI answers through a FastAPI backend and polished frontend.

## Core Scope Rule

Version 1 does not use OCR. It supports searchable PDFs, DOCX, TXT, and Markdown only. Reject scanned PDFs, images, screenshots, and handwritten files.

## Development Rules

- Build milestone by milestone.
- Do not implement multiple milestones at once.
- Keep code modular and beginner-friendly.
- Keep documentation updated after every milestone.
- Do not commit automatically.
- Show changed files and testing results before asking the user to commit.
- Do not add major features unless approved.

## Architecture Rules

- Separate backend API, document ingestion, extraction, chunking, embeddings, retrieval, citation formatting, metadata storage, frontend UI, and tests.
- Do not put all logic in one file.
- Prefer clear service modules and route files.

## Current Milestone State

- Milestone 0 complete: documentation scaffold.
- Milestone 1 complete: FastAPI backend foundation (health endpoint, CORS, config, logging, pytest).
- Milestone 2 complete: document upload endpoint with file-type validation and local storage.
- Milestone 3 complete: text extraction (PyMuPDF, python-docx, plain text; scanned PDF detection).
- Milestone 4 complete: word-based overlapping text chunking; upload response includes chunk_count.
- Next milestone is Milestone 5: Embeddings Foundation.

## Milestone 5 Scope

- Provider-based embedding architecture (LocalBGEProvider + FakeEmbeddingProvider for tests)
- Default model: BAAI/bge-small-en-v1.5 via sentence-transformers
- Tests use FakeEmbeddingProvider — no model download, fast and deterministic
- Upload response gains embedding_count field
- No vector database yet
- No retrieval yet
- No frontend yet

## Testing Rule

Every milestone that touches code should include tests and test instructions.

## Documentation Rule

Update `PROJECT_STATUS.md` and `CHANGELOG.md` after each milestone.
