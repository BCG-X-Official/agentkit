# -*- coding: utf-8 -*-
from typing import Any, List, Literal, Optional, Union

from box import Box
from langchain.schema import AIMessage, HumanMessage
from pydantic.v1 import BaseModel  # TODO: Remove this line when langchain upgrades to pydantic v2

LLMType = Literal[
    "gpt-4",
    "gpt-3.5-turbo",
    "azure-4-32k",
    "azure-3.5",
]


class PromptInput(BaseModel):
    name: str
    content: str


class ToolConfig(BaseModel):
    description: str
    prompt_message: str
    image_description_prompt: Optional[str]
    system_context: str
    prompt_selection: Optional[str]
    system_context_selection: Optional[str]
    prompt_validation: Optional[str]
    system_context_validation: Optional[str]
    prompt_refinement: Optional[str]
    system_context_refinement: Optional[str]
    prompt_inputs: list[PromptInput]
    additional: Optional[Box] = None


class SqlToolConfig(ToolConfig):
    nb_example_rows: int
    validate_empty_results: bool
    validate_with_llm: bool
    always_limit_query: bool


class ToolsLibrary(BaseModel):
    library: dict[
        str,
        ToolConfig,
    ]


class UserSettings(BaseModel):
    data: dict[
        str,
        Any,
    ]
    version: Optional[int] = None


class ToolInputSchema(BaseModel):
    chat_history: List[
        Union[
            HumanMessage,
            AIMessage,
        ]
    ]
    latest_human_message: str

    # Practice configurations
    user_settings: Optional[UserSettings]

    # Tool outputs (intermediate results)
    intermediate_steps: dict[
        str,
        Any,
    ]
