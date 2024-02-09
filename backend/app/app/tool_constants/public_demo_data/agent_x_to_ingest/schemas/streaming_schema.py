# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any

from pydantic import BaseModel


class StreamingDataTypeEnum(Enum):
    text = "text"
    llm = "llm"
    appendix = "appendix"
    action = "action"
    signal = "signal"


class StreamingData(BaseModel):
    data: str
    data_type: StreamingDataTypeEnum = StreamingDataTypeEnum.text
    metadata: dict[str, Any] = {}
