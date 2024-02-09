# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any

from pydantic import BaseModel


class StreamingDataTypeEnum(Enum):
    TEXT = "text"
    LLM = "llm"
    APPENDIX = "appendix"
    ACTION = "action"
    SIGNAL = "signal"


class StreamingSignalsEnum(Enum):
    START = "START"
    END = "END"
    TOOL_END = "TOOL_END"
    LLM_END = "LLM_END"


class StreamingData(BaseModel):
    data: str
    data_type: StreamingDataTypeEnum = StreamingDataTypeEnum.TEXT
    metadata: dict[
        str,
        Any,
    ] = {}
