from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "KnowFlow AI Backend"
    version: str = "0.1.0"
    environment: str = "development"
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Embeddings
    embedding_provider: str = "local"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_batch_size: int = 32

    # Qdrant vector database
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "knowflow_documents"
    vector_size: int = 384
    vector_distance: str = "Cosine"

    # LLM (answer generation)
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "llama3.2:3b"
    llm_timeout_seconds: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
