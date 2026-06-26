from contextlib import asynccontextmanager

from ag_ui.core.types import RunAgentInput
from ag_ui.encoder import EventEncoder
from ag_ui_langgraph import LangGraphAgent
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agents.document_agent import document_agent, extract_document_id_from_context
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

agent = LangGraphAgent(
	name="document_agent",
	description="Answers questions about an uploaded PDF.",
	graph=document_agent
)


@app.post("/agent")
async def agent_endpoint(input_data: RunAgentInput, request: Request):
	accept_header = request.headers.get("accept")
	encoder = EventEncoder(accept=accept_header)
	request_agent = agent.clone()

	state = input_data.state if isinstance(input_data.state, dict) else {}
	document_id = extract_document_id_from_context(input_data.context or [])
	if document_id:
		state = {
			**state,
			"active_document_id": document_id,
		}

	request_input = input_data.model_copy(update={"state": state})

	async def event_generator():
		async for event in request_agent.run(request_input):
			yield encoder.encode(event)

	return StreamingResponse(
		event_generator(),
		media_type=encoder.get_content_type()
	)


@app.get("/agent/health")
def agent_health():
	return {
		"status": "ok",
		"agent": {
			"name": agent.name,
		}
	}
