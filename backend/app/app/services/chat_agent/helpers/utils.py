# -*- coding: utf-8 -*-
import logging
from typing import List, Union

import tiktoken

logger = logging.getLogger(__name__)


def get_token_length(string: str, model="gpt-4") -> int:
    """Get the token length of a string for a given model."""
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(string)
    return len(encoded)


def get_conversation_id(tags: List) -> Union[str, None]:
    for tag in tags:
        if "conversation_id" in tag:
            return tag.split("=")[1]
    return None
