# KnowFlow AI — Architecture Overview

This document outlines the high-level architecture for KnowFlow AI.

Core Subsystems

- Document Ingestion Service
  - Handles file uploads, validation, metadata extraction, and storage.
  - Stores raw files in object storage (S3-compatible) and metadata in a relational DB.

- Text Extraction
  - Extracts text from PDFs (text layer), DOCX, and plain text files.
  - Produces cleaned, normalized text and document-level metadata.

- Chunking and Embeddings Worker
  - Splits text into chunks (configurable size + overlap).
  - Calls embedding model (OpenAI, Anthropic, or local) to create vectors.
  - Persists vectors and metadata to a vector database.

- Vector Database & Retrieval
  - Milvus, Weaviate, Pinecone, or self-hosted FAISS as options.
  - Supports metadata filters, ANN indexing, and configurable distance metric.

- FastAPI Backend
  - Ingestion endpoints, document library endpoints, search/QA endpoints.
  - Orchestrates retrieval, prompt construction, LLM queries, and citation assembly.

- RAG/QA Pipeline
  - Retrieve top-K chunks, optional reranking, and prompt engineering for LLM.
  - Return answers with inline/annotated citations and source references.

- Web Frontend (future)
  - Document library, upload UI, search/QA interface, admin pages.

Data Flow
1. User uploads document → Ingestion Service stores raw file and metadata.
2. Extraction worker extracts text → Chunking worker splits and creates embeddings.
3. Vectors stored in Vector DB → Backend performs retrieval for queries.
4. RAG pipeline assembles context and calls LLM → Answer returned with citations.

Security & Compliance
- Authentication + RBAC for document access
- Data encryption at rest and in transit
- Audit logs for ingestion and queries

Scalability
- Workers autoscaled via queue/backpressure (e.g., Redis, RabbitMQ)
- Vector DB scaled independently; consider sharding or multi-index strategies

Observability
- Tracing for ingestion → extraction → embedding flows
- Metrics: ingestion latency, embedding throughput, query latency, vector DB load
