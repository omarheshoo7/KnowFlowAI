from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    file_type: str
    status: str
    message: str
    extraction_status: str
    text_length: int
    text_preview: str
