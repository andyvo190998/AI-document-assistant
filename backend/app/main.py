from contextlib import asynccontextmanager

from ag_ui_langgraph import (
	LangGraphAgent,
	add_langgraph_fastapi_endpoint
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.document_agent import document_agent
from app.api.documents import router as document_router
from app.core.config import settings
from app.core.pinecone import ensure_pinecone_index

@asynccontextmanager
async def lifespan(_: FastAPI):
	ensure_pinecone_index()
	yield

app = FastAPI(
	title="PDF AI Assistant API",
	version="0.1.0",
	lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router)

@app.get("/health")
async def health() -> dict[str, str]:
	return {"status": "ok"}

add_langgraph_fastapi_endpoint(
	app=app,
	agent=LangGraphAgent(
		name="document_agent",
		description="Answers questions about an uploaded PDF.",
		graph=document_agent
	),
	path="/agent"
)
