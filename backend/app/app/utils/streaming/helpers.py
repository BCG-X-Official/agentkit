# -*- coding: utf-8 -*-
import logging
from typing import Any, AsyncGenerator, Awaitable

from app.schemas.streaming_schema import StreamingData
from app.utils.exceptions.common_exceptions import AgentCancelledException
from app.utils.streaming.callbacks.stream import AsyncIteratorCallbackHandler

logger = logging.getLogger(__name__)


class StreamHandlerNoNewline(logging.StreamHandler):
    """Stream handler that does not add a newline."""

    def emit(
        self,
        record: logging.LogRecord,
    ) -> None:
        msg = self.format(record)
        self.stream.write(msg)
        self.flush()


def setup_stream_logger() -> logging.Logger:
    """Setup a logger for the stream."""
    logger_ = logging.getLogger("stream_logger")
    logger_.setLevel(logging.INFO)

    # Add custom stream handler to the logger
    handler = StreamHandlerNoNewline()
    handler.setFormatter(logging.Formatter("%(message)s"))  # Remove the default formatting

    logger_.addHandler(handler)
    logger_.propagate = False  # Prevent duplicate log messages

    return logger_


stream_logger = setup_stream_logger()


async def event_generator(
    acallback: AsyncIteratorCallbackHandler,
) -> AsyncGenerator[StreamingData, Any]:
    """Generate events from the callback handler."""
    ait = acallback.aiter()

    logger.info("Streaming response...")
    async for response in ait:
        stream_logger.debug(response)
        yield response
    stream_logger.info("\n")


async def handle_exceptions(
    awaitable: Awaitable[Any],
    stream_handler: AsyncIteratorCallbackHandler,
) -> None:
    """Handle exceptions from awaitables."""
    try:
        return await awaitable
    except TimeoutError as e:
        logger.exception(repr(e))
        await stream_handler.on_llm_error(error=Exception("OpenAI API timed out. Please try again."))
    except AgentCancelledException as e:
        logger.exception(repr(e))
        await stream_handler.on_llm_error(error=e)
    except Exception as e:
        logger.exception(e)
        await stream_handler.on_llm_error(error=e)
