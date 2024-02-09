# -*- coding: utf-8 -*-
import logging
from typing import List

import tiktoken

logger = logging.getLogger(__name__)


def get_token_length(string: str, model: str = "gpt-4") -> int:
    """Get the token length of a string for a given model."""
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(string)
    return len(encoded)


def get_conversation_id(tags: List) -> str:
    for tag in tags:
        if "conversation_id" in tag:
            return tag.split("=")[1]
    raise ValueError("No conversation_id found in tags.")
