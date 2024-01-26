# -*- coding: utf-8 -*-
import logging
from itertools import groupby
from operator import itemgetter
from typing import Dict, List, Tuple, TypeVar

import tiktoken

logger = logging.getLogger(__name__)


def get_token_length(string: str, model="gpt-4") -> int:
    """Get the token length of a string for a given model."""
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(string)
    return len(encoded)
