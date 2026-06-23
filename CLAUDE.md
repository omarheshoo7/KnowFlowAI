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
- Milestone 7 complete: semantic retrieval; POST /api/search; ScoredChunk; VectorStore.search(); 93 tests passing.
- Next milestone is Milestone 8: RAG Answer Generation with Citations.

## Milestone 8 Scope

- POST /api/chat: retrieve chunks → build context → call LLM → return grounded answer with citations
- LLM provider architecture: OllamaLLMProvider (default) + FakeLLMProvider (tests)
- llm_service.py: LLMProvider ABC, OllamaLLMProvider, FakeLLMProvider, generate_answer()
- rag_service.py: orchestrates embed → search → format → generate → extract citations
- ChatRequest / CitationSource / ChatResponse Pydantic schemas
- conftest.py patched with FakeLLMProvider — no Ollama required for tests
- No frontend yet; no user accounts; no chat history

## Testing Rule

Every milestone that touches code should include tests and test instructions.

## Documentation Rule

Update `PROJECT_STATUS.md` and `CHANGELOG.md` after each milestone.
