from dataclasses import dataclass

from app.core.pinecone import get_vector_store

@dataclass(frozen=True)
class RetriedChunk:
	page: int
	text: str
	score: float

class RetrievalService:
	@staticmethod
	def search(
			document_id: str,
			query: str,
			limit: int = 6,
	) -> list[RetriedChunk]:
		if not document_id.startswith("document-"):
			raise ValueError("Invalid document ID.")

		vector_store = get_vector_store(namespace=document_id)

		result = vector_store.similarity_search_with_score(
			query=query,
			k=limit
		)

		return [
			RetriedChunk(
				page=int(document.metadata.get("page", 0)),
				text=document.page_content,
				score=float(score)
			)
			for document, score in result
		]


retrieval_service = RetrievalService()