# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from pydantic import BaseModel


# Define schemas
class UserSchema(BaseModel):
    id: str
    name: str | None = None
    email: str | None = None
    emailVerified: datetime | None = None
    image: str | None = None
    credits: int = 3
    location: str | None = None

    accounts: list[Any] = []
    sessions: list[Any] = []

    class Config:
        from_attributes = True
