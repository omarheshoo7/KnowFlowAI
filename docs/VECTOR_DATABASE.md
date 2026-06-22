# Vector Database

Options
- Managed: Pinecone, Weaviate Cloud
- Self-hosted: Weaviate, Milvus, Milvus + FAISS, or local FAISS

Vector schema (per vector)
- `id` (uuid)
- `document_id`
- `chunk_index`
- `text` (optional, short preview)
- `metadata` (json: filename, page, section, uploaded_by, tags)
- `embedding` (vector)

Indexing and configuration
- Metric: cosine or dot-product depending on embedding model.
- Dimensionality: depends on embedding provider (e.g., 1536 for OpenAI Ada/embedding-3-small)
- Sharding/replication: plan for scale (use managed DB if unsure)

Queries
- Support top_k, score threshold, and metadata filtering.
- Consider pre-filtering by date, document type, or tags.
