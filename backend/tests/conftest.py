import pytest
import backend.app.services.embedding_service as embedding_service
import backend.app.services.vector_store_service as vector_store_service
import backend.app.services.llm_service as llm_service
from backend.app.services.embedding_service import FakeEmbeddingProvider
from backend.app.services.vector_store_service import FakeVectorStore
from backend.app.services.llm_service import FakeLLMProvider


@pytest.fixture(autouse=True)
def fake_embedding_provider():
    """Patch the embedding provider for every test.

    Prevents loading the real sentence-transformers model or downloading
    weights. Tests run fast and fully offline.
    """
    original = embedding_service._provider
    embedding_service._provider = FakeEmbeddingProvider()
    yield
    embedding_service._provider = original


@pytest.fixture(autouse=True)
def fake_vector_store_provider():
    """Patch the vector store for every test.

    Prevents any test from connecting to a real Qdrant instance.
    No Docker required to run the test suite.
    """
    original = vector_store_service._vector_store
    vector_store_service._vector_store = FakeVectorStore()
    yield
    vector_store_service._vector_store = original


@pytest.fixture(autouse=True)
def fake_llm_provider():
    """Patch the LLM provider for every test.

    Prevents any test from connecting to a real Ollama instance.
    No Ollama installation required to run the test suite.
    """
    original = llm_service._provider
    llm_service._provider = FakeLLMProvider()
    yield
    llm_service._provider = original
