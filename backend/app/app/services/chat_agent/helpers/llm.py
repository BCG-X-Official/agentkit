# -*- coding: utf-8 -*-
# mypy: disable-error-code="call-arg"
# TODO: Change langchain param names to match the new langchain version

import logging
from typing import Optional

import tiktoken
from langchain.base_language import BaseLanguageModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.core.config import settings
from app.schemas.tool_schema import LLMType

logger = logging.getLogger(__name__)


def get_token_length(
    string: str,
    model: str = "gpt-4",
) -> int:
    """Get the token length of a string."""
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(string)
    return len(encoded)


def get_llm(
    llm: LLMType,
    api_key: Optional[str] = settings.OPENAI_API_KEY,
) -> BaseLanguageModel:
    """Get the LLM instance for the given LLM type."""
    match llm:
        case "azure-3.5":
            if settings.OPENAI_API_BASE is None:
                raise ValueError("OPENAI_API_BASE must be set to use Azure LLM")
            return AzureChatOpenAI(
                openai_api_base=settings.OPENAI_API_BASE,
                openai_api_version="2023-03-15-preview",
                deployment_name="rnd-gpt-35-turbo",
                openai_api_key=api_key if api_key is not None else settings.OPENAI_API_KEY,
                openai_api_type="azure",
                streaming=True,
            )
        case "gpt-3.5-turbo":
            return ChatOpenAI(
                temperature=0,
                model_name="gpt-3.5-turbo",
                openai_organization=settings.OPENAI_ORGANIZATION,
                openai_api_key=api_key if api_key is not None else settings.OPENAI_API_KEY,
                streaming=True,
            )
        case "gpt-4":
            return ChatOpenAI(
                temperature=0,
                model_name="gpt-4",
                openai_organization=settings.OPENAI_ORGANIZATION,
                openai_api_key=api_key if api_key is not None else settings.OPENAI_API_KEY,
                streaming=True,
            )
        # If an exact match is not confirmed, this last case will be used if provided
        case _:
            logger.warning(f"LLM {llm} not found, using default LLM")
            return ChatOpenAI(
                temperature=0,
                model_name="gpt-4",
                openai_organization=settings.OPENAI_ORGANIZATION,
                openai_api_key=settings.OPENAI_API_KEY,
                streaming=True,
            )
