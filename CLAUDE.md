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
- Milestone 8 complete: RAG answer generation with citations; POST /api/chat; LLMProvider ABC; OllamaLLMProvider; FakeLLMProvider; rag_service; 115 tests passing.
- Milestone 9 complete: SaaS frontend dashboard; Next.js 14 + TypeScript + Tailwind CSS; Upload, Chat, Search panels; ApiStatus; clean build.
- Next milestone is Milestone 10: Deployment & Portfolio Polish.

## Milestone 9 Scope (complete)

- Next.js 14 App Router, TypeScript, Tailwind CSS — no paid APIs, no OCR
- frontend/ directory: app/, components/, lib/, types/
- UploadPanel: drag-and-drop upload, full response display (chunk_count, embedding_count, stored_vector_count, text_preview)
- ChatPanel: question input, top-k selector, AI answer with inline citations and sources list
- SearchPanel: semantic search, scored results with similarity progress bar
- ApiStatus: backend health indicator in header (online/offline + version)
- NEXT_PUBLIC_API_BASE_URL environment variable; .env.local.example provided
- npm run build passes clean (zero TypeScript and ESLint errors)

## Testing Rule

Every milestone that touches code should include tests and test instructions.

## Documentation Rule

Update `PROJECT_STATUS.md` and `CHANGELOG.md` after each milestone.
