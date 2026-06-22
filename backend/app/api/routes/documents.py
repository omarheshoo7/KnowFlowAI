from fastapi import APIRouter, UploadFile, File
from backend.app.schemas.document import DocumentUploadResponse
from backend.app.services import storage_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    saved_path = await storage_service.save_upload(file)
    extension = saved_path.suffix.lstrip(".")
    return DocumentUploadResponse(
        filename=file.filename,
        file_type=extension,
        status="uploaded",
        message="Document uploaded successfully",
    )
