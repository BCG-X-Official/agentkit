# -*- coding: utf-8 -*-
# type: ignore
from collections.abc import Sequence
from math import ceil
from typing import Any, Generic, TypeVar

from fastapi_pagination import Page, Params
from fastapi_pagination.bases import AbstractPage, AbstractParams
from pydantic import BaseModel

DataType = TypeVar("DataType")
T = TypeVar("T")


class PageBase(
    Page[T],
    Generic[T],
):
    pages: int
    next_page: int | None
    previous_page: int | None


class IResponseBase(
    BaseModel,
    Generic[T],
):
    message: str = ""
    meta: dict = {}
    data: T | None


class IResponsePage(
    AbstractPage[T],
    Generic[T],
):
    """Response page schema."""

    message: str = ""
    meta: dict = {}
    data: PageBase[T]

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> PageBase[T] | None:
        if params.size is not None and total is not None and params.size != 0:
            pages = ceil(total / params.size)
        else:
            pages = 0

        return cls(
            data=PageBase(
                items=items,
                page=params.page,
                size=params.size,
                total=total,
                pages=pages,
                next_page=params.page + 1 if params.page < pages else None,
                previous_page=params.page - 1 if params.page > 1 else None,
            )
        )


class IGetResponseBase(
    IResponseBase[DataType],
    Generic[DataType],
):
    message: str = "Data got correctly"


def create_response(
    data: DataType | None,
    message: str | None = "",
    meta: dict | Any | None = None,
) -> DataType:
    meta = {} if meta is None else meta
    if isinstance(
        data,
        IResponsePage,
    ):
        data.message = "Data paginated correctly" if not message else message
        data.meta = meta
        return data
    return {
        "data": data,
        "message": message,
        "meta": meta,
    }
