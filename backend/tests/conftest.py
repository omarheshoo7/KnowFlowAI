import pytest
import backend.app.services.embedding_service as embedding_service
import backend.app.services.vector_store_service as vector_store_service
from backend.app.services.embedding_service import FakeEmbeddingProvider
from backend.app.services.vector_store_service import FakeVectorStore


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
