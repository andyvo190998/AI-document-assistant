from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings

def create_chat_model(provider: str = "openai") -> BaseChatModel:
    if provider == "ollama":
        return ChatOllama(
            model="llama3.2",
            temperature=0,
        )

    return ChatOpenAI(
        model=settings.chat_model,
        temperature=0,
        api_key=settings.openai_api_key,
        streaming=True,
    )