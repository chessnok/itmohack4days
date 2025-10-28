"""This file contains the graph utilities for the application."""
from typing import Union, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import trim_messages as _trim_messages, BaseMessage
from transformers import AutoTokenizer

from app.core.config import settings
from app.schemas import Message


def dump_messages(messages: list[Message]) -> list[dict]:
    """Dump the messages to a list of dictionaries.

    Args:
        messages (list[Message]): The messages to dump.

    Returns:
        list[dict]: The dumped messages.
    """
    return [message.model_dump() for message in messages]


def prepare_messages(messages: list[Message], llm: BaseChatModel, system_prompt: str) -> list[Message]:
    """Prepare the messages for the LLM.

    Args:
        messages (list[Message]): The messages to prepare.
        llm (BaseChatModel): The LLM to use.
        system_prompt (str): The system prompt to use.

    Returns:
        list[Message]: The prepared messages.
    """
    trimmed_messages = _trim_messages(
        dump_messages(messages),
        strategy="last",
        token_counter=count_tokens,
        max_tokens=settings.MAX_TOKENS,
        start_on="human",
        include_system=False,
        allow_partial=False,
    )
    return [Message(role="system", content=system_prompt)] + trimmed_messages
MODEL_ID = "yandex/YandexGPT-5-Lite-8B-pretrain"

def _load_tokenizer():
    # сначала пробуем fast, если не вышло — fall back на slow
    try:
        return AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    except Exception:
        return AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, use_fast=False)

def _to_text(messages: Union[str, List[BaseMessage]], tokenizer) -> str:
    if isinstance(messages, str):
        return messages
    # Попробуем chat template, если модель его поддерживает
    try:
        chat = [{"role": getattr(m, "type", "user"), "content": m.content} for m in messages]
        return tokenizer.apply_chat_template(
            chat, tokenize=False, add_generation_prompt=False
        )
    except Exception:
        # Фолбэк: просто склеим реплики
        return "\n".join(f"{getattr(m, 'type', 'user')}: {m.content}" for m in messages)

def count_tokens(messages: Union[str, List[BaseMessage]]) -> int:
    tokenizer = _load_tokenizer()
    text = _to_text(messages, tokenizer)
    # Надёжный подсчёт без спец-токенов
    return len(tokenizer.encode(text, add_special_tokens=False))