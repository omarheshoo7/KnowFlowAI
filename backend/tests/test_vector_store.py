import io
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services import vector_store_service
from backend.app.services.vector_store_service import FakeVectorStore, ChunkPoint
from backend.app.services.chunking_service import Chunk
import backend.app.services.storage_service as storage_service

client = TestClient(app)

FAKE_EMBEDDING = [0.1] * 384


# ---------------------------------------------------------------------------
# Unit tests — FakeVectorStore directly (no patching needed here)
# ---------------------------------------------------------------------------

def test_fake_store_returns_correct_count():
    store = FakeVectorStore()
    points = [
        ChunkPoint(chunk_index=0, text="first", word_count=1, character_count=5, embedding=FAKE_EMBEDDING),
        ChunkPoint(chunk_index=1, text="second", word_count=1, character_count=6, embedding=FAKE_EMBEDDING),
    ]
    result = store.store("doc1", "file.txt", "abc.txt", "txt", points)
    assert result == 2


def test_fake_store_accumulates_points():
    store = FakeVectorStore()
    points = [
        ChunkPoint(chunk_index=i, text=f"chunk {i}", word_count=2, character_count=7, embedding=FAKE_EMBEDDING)
        for i in range(4)
    ]
    store.store("doc1", "file.txt", "abc.txt", "txt", points)
    assert len(store.stored_points) == 4


def test_fake_store_empty_input_returns_zero():
    store = FakeVectorStore()
    result = store.store("doc1", "file.txt", "abc.txt", "txt", [])
    assert result == 0
    assert len(store.stored_points) == 0


def test_fake_store_records_metadata():
    store = FakeVectorStore()
    store.store("doc-abc", "report.pdf", "uuid123.pdf", "pdf", [])
    assert store.stored_metadata[0]["document_id"] == "doc-abc"
    assert store.stored_metadata[0]["original_filename"] == "report.pdf"
    assert store.stored_metadata[0]["file_type"] == "pdf"


# ---------------------------------------------------------------------------
# Unit tests — store_chunks() public function
# (conftest.py FakeVectorStore fixture is autouse — no Docker needed)
# ---------------------------------------------------------------------------

def test_store_chunks_empty_inputs_return_zero():
    result = vector_store_service.store_chunks(
        document_id="doc1",
        original_filename="file.txt",
        stored_filename="abc.txt",
        file_type="txt",
        chunks=[],
        embeddings=[],
    )
    assert result == 0


def test_store_chunks_returns_count_equal_to_input():
    chunks = [
        Chunk(chunk_index=0, text="hello world", word_count=2, character_count=11),
        Chunk(chunk_index=1, text="second chunk", word_count=2, character_count=12),
        Chunk(chunk_index=2, text="third chunk", word_count=2, character_count=11),
    ]
    embeddings = [FAKE_EMBEDDING for _ in chunks]
    result = vector_store_service.store_chunks(
        document_id="doc1",
        original_filename="notes.txt",
        stored_filename="uuid.txt",
        file_type="txt",
        chunks=chunks,
        embeddings=embeddings,
    )
    assert result == 3


def test_store_chunks_points_reach_fake_store():
    chunks = [Chunk(chunk_index=i, text=f"chunk {i}", word_count=2, character_count=7) for i in range(5)]
    embeddings = [FAKE_EMBEDDING for _ in chunks]
    vector_store_service.store_chunks(
        document_id="doc1",
        original_filename="doc.txt",
        stored_filename="abc.txt",
        file_type="txt",
        chunks=chunks,
        embeddings=embeddings,
    )
    fake = vector_store_service._vector_store
    assert len(fake.stored_points) == 5


def test_store_chunks_empty_chunks_skips_store():
    vector_store_service.store_chunks(
        document_id="doc1",
        original_filename="doc.txt",
        stored_filename="abc.txt",
        file_type="txt",
        chunks=[],
        embeddings=[FAKE_EMBEDDING],
    )
    fake = vector_store_service._vector_store
    assert len(fake.stored_points) == 0


# ---------------------------------------------------------------------------
# Integration tests — POST /api/documents/upload includes stored_vector_count
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def use_tmp_upload_dir(tmp_path):
    with patch.object(storage_service, "UPLOAD_DIR", tmp_path):
        yield


def _upload_bytes(filename: str, content: bytes, content_type: str):
    return client.post(
        "/api/documents/upload",
        files={"file": (filename, io.BytesIO(content), content_type)},
    )


def test_upload_response_has_stored_vector_count_field():
    content = ("word " * 100).encode("utf-8")
    response = _upload_bytes("doc.txt", content, "text/plain")
    data = response.json()
    assert response.status_code == 200
    assert "stored_vector_count" in data
    assert isinstance(data["stored_vector_count"], int)


def test_txt_upload_stored_count_equals_chunk_count():
    content = (" ".join([f"word{i}" for i in range(600)])).encode("utf-8")
    response = _upload_bytes("notes.txt", content, "text/plain")
    data = response.json()
    assert data["extraction_status"] == "success"
    assert data["stored_vector_count"] == data["chunk_count"]
    assert data["stored_vector_count"] > 0


def test_scanned_pdf_returns_stored_vector_count_zero():
    import fitz
    import io as _io
    doc = fitz.open()
    doc.new_page()
    buf = _io.BytesIO()
    doc.save(buf)
    doc.close()
    response = _upload_bytes("scan.pdf", buf.getvalue(), "application/pdf")
    data = response.json()
    assert response.status_code == 200
    assert data["extraction_status"] == "failed"
    assert data["stored_vector_count"] == 0


def test_upload_success_message_mentions_stored():
    content = ("word " * 100).encode("utf-8")
    response = _upload_bytes("doc.txt", content, "text/plain")
    data = response.json()
    assert "stored" in data["message"].lower()


def test_md_upload_stored_count_is_positive():
    content = ("# Title\n\n" + "word " * 200).encode("utf-8")
    response = _upload_bytes("doc.md", content, "text/markdown")
    data = response.json()
    assert response.status_code == 200
    assert data["stored_vector_count"] >= 1
