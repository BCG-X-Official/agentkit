# -*- coding: utf-8 -*-
from langchain.schema import HumanMessage

from app.schemas.tool_schema import ToolInputSchema


def standard_query_format(tool_input: ToolInputSchema) -> str:
    if "entertainer_tool" in tool_input.intermediate_steps:
        del tool_input.intermediate_steps["entertainer_tool"]
    for message in tool_input.chat_history:
        if isinstance(message.content, str):
            message.content = "\n".join(
                [line for line in message.content.split("\n") if not line.startswith(("action:", "signal:"))]
            )
        else:
            raise Exception("Message content is not a string.")
    query = (
        (
            "\nChat history: \n"
            + "\n".join(
                [
                    f"Human: {message.content}" if isinstance(message, HumanMessage) else f"AI: {message.content}"
                    for message in tool_input.chat_history
                ]
            )
            if tool_input.chat_history
            else ""
        )
        + (
            "\nIntermediate tool outputs: "
            + "\n".join([f"{key}: {value}" for key, value in tool_input.intermediate_steps.items()])
            if tool_input.intermediate_steps
            else ""
        )
        + "Latest user question: "
        + tool_input.latest_human_message
    )
    return query
