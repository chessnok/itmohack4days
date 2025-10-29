from typing import (
    Any,
    Dict,
)

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langchain_core.messages import (
    convert_to_openai_messages,
)
from langchain_openai import ChatOpenAI
from openai import OpenAI

from app.core.config import settings


def _get_model_kwargs() -> Dict[str, Any]:
    """Get environment-specific model kwargs.

    Returns:
        Dict[str, Any]: Additional model arguments based on environment
    """
    model_kwargs = {"top_p": 0.95, "presence_penalty": 0.1, "frequency_penalty": 0.1}

    return model_kwargs

langfuse_cli=Langfuse(public_key=settings.LANGFUSE_PUBLIC_KEY, secret_key=settings.LANGFUSE_SECRET_KEY)

handler = CallbackHandler()

llm_client = OpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    project=settings.FOLDER_LLM,
)
LLM = ChatOpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    client=llm_client,
    model=settings.LLM_MODEL,
    callbacks=[handler],
    temperature=settings.DEFAULT_LLM_TEMPERATURE,
    max_tokens=settings.MAX_TOKENS,
    **_get_model_kwargs(),
)
