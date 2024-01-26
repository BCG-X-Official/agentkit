# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import openai
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.query_formatting import standard_query_format
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class ImageGenerationTool(ExtendedBaseTool):
    """Image Generation Tool."""

    name = "image_generation_tool"
    appendix_title = "Image Appendix"

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> ImageGenerationTool:
        """Generate an image based on the input from the user."""
        llm = kwargs.get(
            "llm",
            get_llm(common_config.llm),
        )
        fast_llm = kwargs.get(
            "fast_llm",
            get_llm(common_config.fast_llm),
        )
        fast_llm_token_limit = kwargs.get(
            "fast_llm_token_limit",
            common_config.fast_llm_token_limit,
        )

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
        )

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError("Tool does not support sync")

    async def _arun(
        self,
        *args: Any,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        """Use the tool asynchronously."""
        query = kwargs.get(
            "query",
            args[0],
        )

        # Use standard query formatting
        query = standard_query_format(ToolInputSchema.parse_raw(query))

        try:
            logger.info("Generating the image")
            image_url = self.generate_image(str(query))
            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(content=self.prompt_message.format(description=query)),
            ]
            response = await self._agenerate_response(
                messages,
                discard_fast_llm=True,
                run_manager=run_manager,
            )

            image_url_link = "```ImageURL" + image_url + "```"

            if run_manager is not None:
                await run_manager.on_text(
                    image_url_link,
                    data_type=StreamingDataTypeEnum.APPENDIX,
                    tool=self.name,
                    step=1,
                    title=self.appendix_title,
                )
            return response

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return repr(e)
            raise e

    @staticmethod
    def generate_image(
        description: str,
    ) -> str:
        """Generate an image based on the description."""
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.images.generate(
                prompt=description,
                n=1,
                size="1024x1024",
            )
            image_url = str(response.data[0].url)
            return image_url
        except Exception:
            return "ERROR: could not generate the image based on the description: " + description
