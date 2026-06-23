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

## Planned vector schema (per point in Qdrant)

| Field | Type | Description |
|---|---|---|
| `id` | uuid | Unique vector ID |
| `document_id` | string | Source document identifier |
| `chunk_index` | int | Position of this chunk in the document |
| `text` | string | Chunk text (stored as payload for retrieval) |
| `filename` | string | Original uploaded filename |
| `file_type` | string | pdf / docx / txt / md |

## Indexing configuration

- Collection metric: **Cosine**
- Vector size: **384** (BAAI/bge-small-en-v1.5)
- Index type: HNSW (Qdrant default)

## Query plan (Milestone 7)

- Embed query text with the same `LocalBGEProvider`
- Run top-K cosine search against the Qdrant collection
- Return matching chunks with payload (text + document metadata)
- Support metadata pre-filtering (e.g., by filename or file_type)
