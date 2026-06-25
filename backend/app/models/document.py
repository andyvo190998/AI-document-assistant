from pydantic import BaseModel, Field


class DocumentSource(BaseModel):
    page: int = Field(ge=1)
    text: str


class UploadDocumentResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    chunk_count: int
    summary: str


class DeleteDocumentResponse(BaseModel):
    document_id: str
    deleted: bool