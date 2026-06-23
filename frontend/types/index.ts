export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface UploadResponse {
  filename: string;
  file_type: string;
  status: string;
  message: string;
  extraction_status: string;
  text_length: number;
  text_preview: string;
  chunk_count: number;
  embedding_count: number;
  stored_vector_count: number;
}

export interface SearchResult {
  document_id: string;
  original_filename: string;
  file_type: string;
  chunk_index: number;
  chunk_text: string;
  score: number;
  word_count: number;
  character_count: number;
}

export interface SearchResponse {
  query: string;
  top_k: number;
  results: SearchResult[];
}

export interface CitationSource {
  source_id: string;
  document_id: string;
  original_filename: string;
  file_type: string;
  chunk_index: number;
  score: number;
  chunk_text_preview: string;
}

export interface ChatResponse {
  question: string;
  answer: string;
  citations: string[];
  sources: CitationSource[];
  retrieval_count: number;
}
