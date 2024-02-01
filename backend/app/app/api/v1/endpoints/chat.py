# -*- coding: utf-8 -*-
import asyncio
import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain.agents import AgentExecutor

from app.api.deps import get_jwt
from app.core.config import settings
from app.deps import agent_deps
from app.schemas.message_schema import IChatQuery
from app.services.chat_agent.helpers.run_helper import is_running, stop_run
from app.services.chat_agent.meta_agent import get_conv_token_buffer_memory
from app.utils.streaming.callbacks.stream import AsyncIteratorCallbackHandler
from app.utils.streaming.helpers import event_generator, handle_exceptions
from app.utils.streaming.StreamingJsonListResponse import StreamingJsonListResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def get_meta_agent_with_api_key(
    chat: IChatQuery,
) -> AgentExecutor:
    """
    Returns a MetaAgent instance with the API key specified in the chat query.

    Args:
        chat (IChatQuery): The chat query containing the API key.

    Returns:
        MetaAgent: The MetaAgent instance with the specified API key.
    """
    return agent_deps.get_meta_agent(chat.api_key)


@router.get("/run/{run_id}/status", response_model=bool)
async def run_status(
    run_id: str,
) -> bool:
    return await is_running(run_id)


@router.get("/run/{run_id}/cancel", response_model=bool)
async def run_cancel(
    run_id: str,
) -> bool:
    await stop_run(run_id)
    return True


@router.post("/agent", dependencies=[Depends(agent_deps.set_global_tool_context)])
async def agent_chat(
    chat: IChatQuery,
    jwt: Annotated[dict, Depends(get_jwt)],
    meta_agent: AgentExecutor = Depends(get_meta_agent_with_api_key),
) -> StreamingResponse:
    """
    This function handles the chat interaction with an agent. It converts the chat
    messages to the Langchain format, creates a memory of the conversation, and sets up
    a stream handler. It then creates an asyncio task to handle the conversation with
    the agent and returns a streaming response of the conversation.

    Args:
        chat (IChatQuery): The chat query containing the messages and other details.
        jwt (Annotated[dict, Depends(get_jwt)]): The JWT token from the request.
        meta_agent (AgentExecutor, optional): The MetaAgent instance. Defaults to the one returned by get_
        meta_agent_with_api_key.

    Returns:
        StreamingResponse: The streaming response of the conversation.
    """
    logger.info(f"User JWT from request: {jwt}")

    api_key = chat.api_key
    if api_key is None or api_key == "":
        api_key = settings.OPENAI_API_KEY

    chat_messages = [m.to_langchain() for m in chat.messages]
    memory = get_conv_token_buffer_memory(
        chat_messages[:-1],  # type: ignore
        api_key,
    )
    stream_handler = AsyncIteratorCallbackHandler()
    chat_content = chat_messages[-1].content if chat_messages[-1] is not None else ""
    asyncio.create_task(
        handle_exceptions(
            meta_agent.arun(
                input=chat_content,
                chat_history=memory.load_memory_variables({})["chat_history"],
                callbacks=[stream_handler],
                user_settings=chat.settings,
                tags=[
                    "agent_chat",
                    f"user_email={chat.user_email}",
                    f"conversation_id={chat.conversation_id}",
                    f"message_id={chat.new_message_id}",
                    f"timestamp={datetime.now()}",
                    f"version={chat.settings.version if chat.settings is not None else 'N/A'}",
                ],
            ),
            stream_handler,
        )
    )

    return StreamingJsonListResponse(
        event_generator(stream_handler),
        media_type="text/plain",
    )
