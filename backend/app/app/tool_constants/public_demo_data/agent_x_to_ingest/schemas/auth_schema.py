# -*- coding: utf-8 -*-
from datetime import datetime

from pydantic import BaseModel

from .user_schema import UserSchema


class AccountSchema(BaseModel):
    id: str
    userId: str
    type: str
    provider: str
    providerAccountId: str
    refresh_token: str | None = None
    access_token: str | None = None
    expires_at: int | None = None
    token_type: str | None = None
    scope: str | None = None
    id_token: str | None = None
    session_state: str | None = None

    user: UserSchema = None

    class Config:
        orm_mode = True


class SessionSchema(BaseModel):
    id: str
    sessionToken: str
    userId: str
    expires: datetime

    user: UserSchema = None

    class Config:
        orm_mode = True


class VerificationTokenSchema(BaseModel):
    identifier: str
    token: str
    expires: datetime

    class Config:
        orm_mode = True
