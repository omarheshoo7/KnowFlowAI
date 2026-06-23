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
- Milestone 5 complete: provider-based embeddings (BAAI/bge-small-en-v1.5, 384-dim); FakeEmbeddingProvider for tests.
- Milestone 6 complete: Qdrant vector database foundation; QdrantVectorStore + FakeVectorStore; stored_vector_count in upload response.
- Next milestone is Milestone 7: Semantic Retrieval.

## Milestone 7 Scope

- POST /api/search endpoint: embed query → Qdrant top-K → return scored chunks
- SearchRequest / SearchResult / SearchResponse Pydantic schemas
- VectorStore ABC gains search(query_embedding, top_k) → List[ScoredChunk]
- QdrantVectorStore.search() uses client.search(); FakeVectorStore.search() returns stored entries
- FakeVectorStore and FakeEmbeddingProvider used in all tests — no Docker, no model download
- No LLM answer generation yet
- No frontend yet

## Testing Rule

Every milestone that touches code should include tests and test instructions.

## Documentation Rule

Update `PROJECT_STATUS.md` and `CHANGELOG.md` after each milestone.
