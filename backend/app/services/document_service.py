import os
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.core.config import settings
from app.core.pinecone import get_vector_store
from app.services.model_factory import create_chat_model


# Ingestion service
class DocumentService:
    allowed_content_types = {
        "application/pdf",
        "application/x-pdf",
    }

    def __init__(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1_000,
            chunk_overlap=200,
            add_start_index=True,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def upload_and_index(self, file: UploadFile) -> dict:
        self._validate_file(file)

        document_id = f"document-{uuid4()}"
        temporary_path: str | None = None

        try:
            temporary_path = await self._save_temporarily(file)
            pages = self._extract_pages(
                temporary_path=temporary_path,
                document_id=document_id,
                filename=file.filename or "document.pdf",
            )

            if not pages:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        "No extractable text was found. "
                        "The PDF may be scanned and require OCR."
                    ),
                )

            chunks = self.splitter.split_documents(pages)

            for index, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = index
                chunk.metadata["document_id"] = document_id

            vector_store = get_vector_store(namespace=document_id)
            vector_ids = [
                f"{document_id}-chunk-{index}"
                for index in range(len(chunks))
            ]

            vector_store.add_documents(
                documents=chunks,
                ids=vector_ids,
            )

            summary = await self._generate_summary(pages)

            return {
                "document_id": document_id,
                "filename": file.filename or "document.pdf",
                "page_count": len(pages),
                "chunk_count": len(chunks),
                "summary": summary,
            }
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)

            await file.close()

    def _validate_file(self, file: UploadFile) -> None:
        filename = file.filename or ""

        if Path(filename).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are supported.",
            )

        if file.content_type not in self.allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="The uploaded file does not have a PDF content type.",
            )

    async def _save_temporarily(self, file: UploadFile) -> str:
        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        total_bytes = 0

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temporary_file:
            while chunk := await file.read(1024 * 1024):
                total_bytes += len(chunk)

                if total_bytes > max_bytes:
                    temporary_path = temporary_file.name
                    temporary_file.close()
                    os.unlink(temporary_path)

                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            "The PDF exceeds the "
                            f"{settings.max_upload_size_mb} MB limit."
                        ),
                    )

                temporary_file.write(chunk)

            return temporary_file.name

    def _extract_pages(
        self,
        temporary_path: str,
        document_id: str,
        filename: str,
    ) -> list[Document]:
        try:
            reader = PdfReader(temporary_path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The PDF is invalid, encrypted, or corrupted.",
            ) from exc

        pages: list[Document] = []

        for zero_based_page, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            normalized_text = " ".join(text.split())

            if not normalized_text:
                continue

            pages.append(
                Document(
                    page_content=normalized_text,
                    metadata={
                        "document_id": document_id,
                        "filename": filename,
                        "page": zero_based_page + 1,
                    },
                )
            )

        return pages

    async def _generate_summary(
        self,
        pages: list[Document],
    ) -> str:
        model = create_chat_model()

        # Limit the initial MVP summary input to avoid putting a very
        # large document into one model request.
        summary_input = "\n\n".join(
            f"[Page {page.metadata['page']}]\n{page.page_content}"
            for page in pages
        )[:80_000]

        response = await model.ainvoke(
            [
                {
                    "role": "system",
                    "content": (
                        "You summarize uploaded documents accurately. "
                        "Use only information from the provided document. "
                        "Produce a concise overview, key points, and the "
                        "document's main conclusion. Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": summary_input,
                },
            ]
        )

        return str(response.content)


document_service = DocumentService()