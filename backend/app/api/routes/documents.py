from fastapi import APIRouter, UploadFile, File
from backend.app.schemas.document import DocumentUploadResponse
from backend.app.services import storage_service, text_extraction_service, chunking_service

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    saved_path = await storage_service.save_upload(file)
    extraction = text_extraction_service.extract(saved_path)

    if extraction.extraction_status == "success":
        chunks = chunking_service.chunk_text(extraction.text)
        message = "Document uploaded, text extracted, and chunked successfully"
    else:
        chunks = []
        message = extraction.message

    return DocumentUploadResponse(
        filename=file.filename,
        file_type=saved_path.suffix.lstrip("."),
        status="uploaded",
        message=message,
        extraction_status=extraction.extraction_status,
        text_length=extraction.text_length,
        text_preview=extraction.text_preview,
        chunk_count=len(chunks),
    )
