from fastapi import APIRouter, File, UploadFile, status

from app.core.pinecone import delete_namespace
from app.models.document import (
	DeleteDocumentResponse,
	UploadDocumentResponse
)
from app.services.document_service import document_service

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post(
	"/upload",
	response_model=UploadDocumentResponse,
	status_code=status.HTTP_201_CREATED,
)
async def upload_document(
	file: UploadFile = File(...),
) -> UploadDocumentResponse:
	result = await document_service.upload_and_index(file)
	return UploadDocumentResponse(**result)

@router.delete(
	"/{document_id}",
	response_model=DeleteDocumentResponse
)
async def delete_document(
	document_id: str,
) -> DeleteDocumentResponse:
	delete_namespace(document_id)
	return DeleteDocumentResponse(
		document_id=document_id,
		deleted=True
	)