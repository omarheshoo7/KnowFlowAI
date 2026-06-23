import pytest
import backend.app.services.embedding_service as embedding_service
from backend.app.services.embedding_service import FakeEmbeddingProvider


@pytest.fixture(autouse=True)
def fake_embedding_provider():
    """Patch the embedding provider for every test.

    This prevents any test from loading the real sentence-transformers model
    or downloading weights from the internet. Tests run fast and offline.
    """
    original = embedding_service._provider
    embedding_service._provider = FakeEmbeddingProvider()
    yield
    embedding_service._provider = original
