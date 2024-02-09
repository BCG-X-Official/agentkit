# -*- coding: utf-8 -*-
import tiktoken


def get_token_length(string: str, model: str = "gpt-4") -> int:
    """Get the token length of a string."""
    enc = tiktoken.encoding_for_model(model)
    encoded = enc.encode(string)
    return len(encoded)


def truncate_to_token_length(string: str, max_length: int, model: str = "gpt-4") -> str:
    print("****")
    print("FUNCTION RUN STARTED")
    print(f"TYPE: {type(string)}")
    enc = tiktoken.encoding_for_model(model)
    print("ENCODING OBJECT SUCCESSFUL")
    truncated = enc.encode(string)[:max_length]
    print("FULL ENCODING + TRUNCATION SUCCESSFUL")
    print(type(truncated))
    return enc.decode(truncated)
