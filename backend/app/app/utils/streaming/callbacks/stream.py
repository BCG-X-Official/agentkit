# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Literal, Optional, Union, cast
from uuid import UUID

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.globals import get_llm_cache
from langchain.schema import AgentFinish, LLMResult
from langchain.schema.messages import BaseMessage

from app.schemas.streaming_schema import StreamingData, StreamingDataTypeEnum, StreamingSignalsEnum
from app.utils.fastapi_globals import g


# pylint: disable=too-many-ancestors
class AsyncIteratorCallbackHandler(AsyncCallbackHandler):
    """
    Callback handler that returns an async iterator.

    This handler queues streaming data from various callbacks and allows for
    asynchronous iteration over received data.
    """

    queue: asyncio.Queue[StreamingData]
    done: asyncio.Event
    run_id_cached: dict[str, bool] = {}

    @property
    def always_verbose(
        self,
    ) -> bool:
        return True

    @property
    def llm_cache_enabled(self) -> bool:
        """Determine if LLM caching is enabled."""
        llm_cache = get_llm_cache()
        return llm_cache is not None

    def __init__(
        self,
    ) -> None:
        """
        queue (asyncio.Queue): A queue to hold streaming data until the agent is done.

        done (asyncio.Event): An event that signals the completion of data streaming.
        """
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
        query_context = g.query_context or {}
        self.queue.put_nowait(
            StreamingData(
                data=StreamingSignalsEnum.START.value,
                data_type=StreamingDataTypeEnum.SIGNAL,
                metadata={**query_context},
            )
        )

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        if self.llm_cache_enabled:
            self.run_id_cached[str(kwargs.get("run_id"))] = True

    async def on_llm_new_token(
        self,
        token: str,
        **kwargs: Any,
    ) -> None:
        """
        Callback for when a new token is generated.

        The token along with metadata is immediately queued for streaming
        """
        if self.llm_cache_enabled and self.run_id_cached[str(kwargs.get("run_id"))]:
            self.run_id_cached[str(kwargs.get("run_id"))] = False

        query_context = g.query_context or {}
        self.queue.put_nowait(
            StreamingData(
                data=token,
                data_type=StreamingDataTypeEnum.LLM,
                metadata={**kwargs, **query_context},
            )
        )

    async def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> None:
        """
        Callback to signal the end of language model streaming.

        An 'llm_end' signal is queued along with metadata.
        """
        query_context = g.query_context or {}
        if self.llm_cache_enabled and self.run_id_cached[str(kwargs.get("run_id"))]:
            for generation in response.generations:
                for token in generation:
                    self.queue.put_nowait(
                        StreamingData(
                            data=token.text,
                            data_type=StreamingDataTypeEnum.LLM,
                            metadata={**kwargs, **query_context},
                        )
                    )
            del self.run_id_cached[str(kwargs.get("run_id"))]

        self.queue.put_nowait(
            StreamingData(
                data=StreamingSignalsEnum.LLM_END.value,
                data_type=StreamingDataTypeEnum.SIGNAL,
                metadata={**kwargs, **query_context},
            )
        )

    async def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: Optional[UUID] = None,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Callback for when an error occurs during streaming.

        The error is queued for streaming and done flag is set to signal completion.
        """
        self.queue.put_nowait(
            StreamingData(
                data=repr(error),
                data_type=StreamingDataTypeEnum.LLM,
                metadata={**kwargs, **(g.query_context or {})},
            )
        )
        await asyncio.sleep(1)
        self.done.set()

    async def on_tool_start(
        self,
        serialized: Dict[
            str,
            Any,
        ],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Run when tool starts running."""
        kwargs["tool"] = serialized["name"]
        kwargs["step"] = 0
        kwargs["time"] = datetime.now()
        self.queue.put_nowait(
            StreamingData(
                data=serialized["name"],
                data_type=StreamingDataTypeEnum.ACTION,
                metadata={**kwargs, **(g.query_context or {})},
            )
        )

    async def on_tool_end(
        self,
        output: str,
        **kwargs: Any,
    ) -> None:
        """Run when tool ends running."""
        kwargs["tool"] = kwargs["name"]
        self.queue.put_nowait(
            StreamingData(
                data=StreamingSignalsEnum.TOOL_END.value,
                data_type=StreamingDataTypeEnum.SIGNAL,
                metadata={**kwargs, **(g.query_context or {})},
            )
        )

    async def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when tool errors."""
        kwargs["step"] = 1
        kwargs |= {
            "run_id": run_id,
            "parent_run_id": parent_run_id,
            "tags": tags,
            "error": repr(error),
        }
        self.queue.put_nowait(
            StreamingData(
                data="error",
                data_type=StreamingDataTypeEnum.ACTION,
                metadata={**kwargs, **(g.query_context or {})},
            )
        )

    async def on_text(
        self,
        text: str,
        **kwargs: Any,
    ) -> None:
        """Run on arbitrary text."""
        data_type = kwargs.get(
            "data_type",
            None,
        )
        if data_type is not None:
            if data_type == StreamingDataTypeEnum.ACTION:
                text = text.upper()
            self.queue.put_nowait(
                StreamingData(
                    data=text,
                    data_type=data_type,
                    metadata={**kwargs, **(g.query_context or {})},
                )
            )

    async def on_agent_finish(
        self,
        finish: AgentFinish,
        **kwargs: Any,
    ) -> None:
        """Run on agent end."""
        self.queue.put_nowait(
            StreamingData(
                data=StreamingSignalsEnum.END.value,
                data_type=StreamingDataTypeEnum.SIGNAL,
                metadata={**kwargs, **(g.query_context or {})},
            )
        )
        await asyncio.sleep(0.1)
        self.done.set()

    async def aiter(
        self,
    ) -> AsyncIterator[StreamingData]:
        """Allow streams to be stopped (e.g. on errors or cancelation) via done flag."""
        while not self.queue.empty() or not self.done.is_set():
            # Wait for the next token in the queue,
            # but stop waiting if the done event is set
            (
                done,
                other,
            ) = await asyncio.wait(
                [
                    # NOTE: If you add other tasks here, update the code below,
                    # which assumes each set has exactly one task each
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the other task
            while len(other) > 0:
                other.pop().cancel()

            while len(done) > 0:
                # Extract the value of the first completed task
                token_or_done = cast(
                    Union[
                        StreamingData,
                        Literal[True],
                    ],
                    done.pop().result(),
                )

                # If the extracted value is the boolean True, the done event was set
                if token_or_done is True:
                    break

                # Otherwise, the extracted value is a token, which we yield
                yield token_or_done

    async def on_chat_model_start(
        self,
        serialized: Dict[
            str,
            Any,
        ],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[
            Dict[
                str,
                Any,
            ]
        ] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when a chat model starts running."""
        raise NotImplementedError("AsyncIteratorCallbackHandler does not implement on_chat_model_start")
