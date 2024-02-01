# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.base_uuid_model import BaseUUIDModel
from app.utils import UUID_


class Account(
    BaseUUIDModel,
    SQLModel,
    table=True,
):
    """Account model."""

    id: UUID_ = Field(
        default=None,
        sa_column_kwargs={"primary_key": True},
    )
    userId: str = Field(default=None)
    type: str = Field(default=None)
    provider: str = Field(default=None)
    providerAccountId: str = Field(default=None)
    refresh_token: str = Field(
        default=None,
        nullable=True,
    )
    access_token: str = Field(
        default=None,
        nullable=True,
    )
    expires_at: int = Field(
        default=None,
        nullable=True,
    )
    token_type: str = Field(
        default=None,
        nullable=True,
    )
    scope: str = Field(
        default=None,
        nullable=True,
    )
    id_token: str = Field(
        default=None,
        nullable=True,
    )
    session_state: str = Field(
        default=None,
        nullable=True,
    )
    user: "User" = Relationship(back_populates="accounts")

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "providerAccountId",
        ),
    )


class Session(
    BaseUUIDModel,
    SQLModel,
    table=True,
):
    id: UUID_ = Field(
        default=None,
        sa_column_kwargs={"primary_key": True},
    )
    sessionToken: str = Field(
        default=None,
        unique=True,
    )
    userId: str = Field(default=None)
    expires: datetime = Field(default=None)
    user: "User" = Relationship(back_populates="sessions")


class User(
    BaseUUIDModel,
    SQLModel,
    table=True,
):
    """User model."""

    id: UUID_ = Field(
        default=None,
        sa_column_kwargs={"primary_key": True},
    )
    name: str = Field(
        default=None,
        nullable=True,
    )
    email: str = Field(
        default=None,
        unique=True,
        nullable=True,
    )
    emailVerified: datetime = Field(
        default=None,
        nullable=True,
    )
    image: str = Field(
        default=None,
        nullable=True,
    )
    credits: int = Field(default=3)
    location: str = Field(
        default=None,
        nullable=True,
    )
    accounts: List[Account] = Relationship(back_populates="user")
    sessions: List[Session] = Relationship(back_populates="user")


class VerificationToken(
    BaseUUIDModel,
    SQLModel,
    table=True,
):
    """Verification token model."""

    identifier: str = Field(default=None)
    token: str = Field(
        default=None,
        unique=True,
    )
    expires: datetime = Field(default=None)

    __table_args__ = (
        UniqueConstraint(
            "identifier",
            "token",
        ),
    )
