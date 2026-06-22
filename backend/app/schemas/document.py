from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    file_type: str
    status: str
    message: str
