from fastapi import APIRouter, UploadFile, File
from backend.app.schemas.document import DocumentUploadResponse
from backend.app.services import storage_service, text_extraction_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    saved_path = await storage_service.save_upload(file)
    result = text_extraction_service.extract(saved_path)
    return DocumentUploadResponse(
        filename=file.filename,
        file_type=saved_path.suffix.lstrip("."),
        status="uploaded",
        message=result.message,
        extraction_status=result.extraction_status,
        text_length=result.text_length,
        text_preview=result.text_preview,
    )
