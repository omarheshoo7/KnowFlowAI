import io
import pytest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
import backend.app.services.storage_service as storage_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def use_tmp_upload_dir(tmp_path):
    """Redirect all uploads to a pytest temp directory so no files land in the project."""
    with patch.object(storage_service, "UPLOAD_DIR", tmp_path):
        yield


def _upload(filename: str, content: bytes = b"dummy content", content_type: str = "application/octet-stream"):
    return client.post(
        "/api/documents/upload",
        files={"file": (filename, io.BytesIO(content), content_type)},
    )


# --- Success cases ---

def test_upload_pdf_returns_200():
    response = _upload("report.pdf", content_type="application/pdf")
    assert response.status_code == 200


def test_upload_pdf_response_shape():
    """Checks all expected fields are present. Dummy bytes are not valid PDF so extraction fails."""
    response = _upload("report.pdf", content_type="application/pdf")
    data = response.json()
    assert data["filename"] == "report.pdf"
    assert data["file_type"] == "pdf"
    assert data["status"] == "uploaded"
    assert "message" in data
    assert data["extraction_status"] in ("success", "failed")
    assert isinstance(data["text_length"], int)
    assert isinstance(data["text_preview"], str)


def test_upload_txt_returns_200():
    response = _upload("notes.txt", content_type="text/plain")
    assert response.status_code == 200


def test_upload_txt_response():
    """Dummy text content is valid plain text — extraction always succeeds for TXT."""
    response = _upload("notes.txt", content_type="text/plain")
    data = response.json()
    assert data["file_type"] == "txt"
    assert data["status"] == "uploaded"
    assert data["extraction_status"] == "success"
    assert data["text_length"] > 0


def test_upload_docx_returns_200():
    response = _upload(
        "contract.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert response.status_code == 200


def test_upload_docx_response():
    """Checks schema shape; dummy bytes are not valid DOCX so extraction fails."""
    response = _upload(
        "contract.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    data = response.json()
    assert data["file_type"] == "docx"
    assert data["status"] == "uploaded"
    assert "extraction_status" in data
    assert isinstance(data["text_length"], int)


def test_upload_md_returns_200():
    response = _upload("README.md", content_type="text/markdown")
    assert response.status_code == 200


def test_upload_md_response():
    """Dummy text content is valid markdown — extraction always succeeds for MD."""
    response = _upload("README.md", content_type="text/markdown")
    data = response.json()
    assert data["file_type"] == "md"
    assert data["status"] == "uploaded"
    assert data["extraction_status"] == "success"
    assert data["text_length"] > 0


# --- Rejection cases ---

def test_upload_png_rejected():
    response = _upload("photo.png", content_type="image/png")
    assert response.status_code == 400


def test_upload_jpg_rejected():
    response = _upload("photo.jpg", content_type="image/jpeg")
    assert response.status_code == 400


def test_upload_jpeg_rejected():
    response = _upload("scan.jpeg", content_type="image/jpeg")
    assert response.status_code == 400


def test_upload_unsupported_extension_rejected():
    response = _upload("data.csv", content_type="text/csv")
    assert response.status_code == 400


def test_rejection_error_message_mentions_file_type():
    response = _upload("photo.png", content_type="image/png")
    data = response.json()
    assert "detail" in data
    assert ".png" in data["detail"]
