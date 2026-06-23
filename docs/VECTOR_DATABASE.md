# Vector Database

## Decision (Milestone 6)

**Chosen:** Qdrant (self-hosted, local Docker for development)

Qdrant is selected over Pinecone/Weaviate because it is:
- Free and fully local for development
- Production-ready as a managed cloud service
- Simple Python client (`qdrant-client`)
- Supports cosine similarity out of the box

## Embedding model (implemented — Milestone 5)

- Model: `BAAI/bge-small-en-v1.5` via sentence-transformers
- Dimensionality: **384**
- Provider class: `LocalBGEProvider` in `backend/app/services/embedding_service.py`

## Implemented vector schema (per Qdrant point — Milestone 6)

| Field | Type | Location | Description |
|---|---|---|---|
| `id` | uuid string | PointStruct.id | Unique vector ID (generated per chunk) |
| vector | `List[float]` (384-dim) | PointStruct.vector | BGE-small-en-v1.5 embedding |
| `document_id` | string | payload | UUID hex generated per upload |
| `original_filename` | string | payload | User-supplied filename |
| `stored_filename` | string | payload | UUID-based on-disk filename |
| `file_type` | string | payload | pdf / docx / txt / md |
| `chunk_index` | int | payload | Position of chunk in the document |
| `chunk_text` | string | payload | Full chunk text (used for retrieval) |
| `word_count` | int | payload | Words in this chunk |
| `character_count` | int | payload | Characters in this chunk |

## Indexing configuration

- Collection name: `knowflow_documents` (configurable via `QDRANT_COLLECTION_NAME`)
- Collection metric: **Cosine**
- Vector size: **384** (BAAI/bge-small-en-v1.5)
- Index type: HNSW (Qdrant default)
- Collection is auto-created on first upload if it does not exist

## Running Qdrant locally

```bash
docker run -p 6333:6333 qdrant/qdrant
```

The REST API is available at `http://localhost:6333`. The dashboard is at `http://localhost:6333/dashboard`.

Tests do **not** require Docker — they use `FakeVectorStore` (in-memory).

## Query plan (Milestone 7)

- Embed query text with the same `LocalBGEProvider`
- Run top-K cosine search against the Qdrant collection
- Return matching chunks with payload (chunk_text + document metadata)
- Support metadata pre-filtering (e.g., by original_filename or file_type)
