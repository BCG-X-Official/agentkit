# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from app.schemas.common_schema import QueryBase

LangchainMessage = Union[AIMessage, HumanMessage, SystemMessage]


class ICreatorRole(str, Enum):
    system = "system"
    user = "user"
    agent = "agent"


class IChatMessage(QueryBase):
    role: ICreatorRole
    content: str

    def to_langchain(self) -> LangchainMessage | None:
        match self.role:
            case ICreatorRole.system:
                return SystemMessage(content=self.content)
            case ICreatorRole.user:
                return HumanMessage(content=self.content)
            case ICreatorRole.agent:
                return AIMessage(content=self.content)
            case _:
                return None


class UserSettings(BaseModel):
    data: dict[str, Any]
    version: Optional[str] = None


class IChatQuery(QueryBase):
    messages: list[IChatMessage]
    api_key: str
    conversation_id: UUID
    new_message_id: UUID
    user_email: str
    settings: Optional[UserSettings] = None


class IFeedback(QueryBase):
    conversation_id: UUID
    message_id: UUID
    user: str
    score: int
    comment: str
    key: str
    settings: Optional[UserSettings] = None
    previous_id: Optional[str] = None
