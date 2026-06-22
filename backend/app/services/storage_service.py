import uuid
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "storage" / "uploads"


def validate_extension(filename: str) -> str:
    """Return the lowercased extension or raise 400 if not allowed."""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )
    return suffix


async def save_upload(file: UploadFile) -> Path:
    """Validate, then write the file to the uploads directory. Returns saved path."""
    extension = validate_extension(file.filename)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{extension}"
    dest = UPLOAD_DIR / safe_name

    contents = await file.read()
    dest.write_bytes(contents)

    logger.info("Saved upload: %s -> %s", file.filename, dest.name)
    return dest
