# -*- coding: utf-8 -*-
from typing import Any

from fastapi import FastAPI

from app.schemas.streaming_schema import StreamingData, StreamingDataTypeEnum, StreamingSignalsEnum


class FastAPIWithInternalModels(FastAPI):
    """
    FastAPI subclass that adds internal models (which are not already exposed via API
    return types) to the OpenAPI schema.

    This allows sharing the same models between the backend and the frontend via
    `openapi-typescript-codegen`.
    """

    def openapi(self) -> dict[str, Any]:
        openapi_schema = super().openapi()

        enums = [StreamingSignalsEnum, StreamingDataTypeEnum]
        models = [StreamingData]

        for model in models:
            model_schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
            model_name = model.__name__
            openapi_schema["components"]["schemas"][model_name] = model_schema

        for enum in enums:
            enum_schema = {
                "type": "string",
                "enum": [e.value for e in enum],
                "description": "Description of your enum",
            }
            openapi_schema["components"]["schemas"][enum.__name__] = enum_schema

        return openapi_schema
