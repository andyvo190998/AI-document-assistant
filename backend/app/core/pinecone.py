from functools import lru_cache

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings

EMBEDDING_DIMENSION = 1536

@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
	return OpenAIEmbeddings(
		model=settings.embedding_model,
		api_key=settings.openai_api_key,
	)

@lru_cache
def get_pinecone_client() -> Pinecone:
	return Pinecone(api_key=settings.pinecone_api_key)

def ensure_pinecone_index() -> None:
	client = get_pinecone_client()

	if not client.has_index(settings.pinecone_index_name):
		client.create_index(
			name=settings.pinecone_index_name,
			dimension=EMBEDDING_DIMENSION,
			metric="cosine",
			spec=ServerlessSpec(
				cloud=settings.pinecone_cloud,
				region=settings.pinecone_region
			),
			deletion_protection="disabled"
		)

def get_vector_store(namespace: str) -> PineconeVectorStore:
	client = get_pinecone_client()
	index = client.Index(settings.pinecone_index_name)

	return PineconeVectorStore(
		index=index,
		embedding=get_embeddings(),
		namespace=namespace
	)

def delete_namespace(namespace: str) -> None:
	client = get_pinecone_client()
	index = client.Index(settings.pinecone_index_name)
	index.delete(delete_all=True, namespace=namespace)