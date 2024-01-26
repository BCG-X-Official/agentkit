# -*- coding: utf-8 -*-
import logging
import os
from typing import Optional

import openai
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class ImageGenerationWithInputTool(ExtendedBaseTool):
    """Image Generation With Input Tool."""

    name = "image_gen_with_input_tool"
    appendix_title = "Image Appendix"

    @classmethod
    def from_config(cls, config: ToolConfig, **kwargs):
        """Create an image generation with input tool from a config."""
        llm = kwargs.get("llm", get_llm(config.default_llm))
        fast_llm = kwargs.get("fast_llm", get_llm(config.default_fast_llm))

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
        )

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            logger.info("Generating the image")
            image_url = self.generate_image(str(query))
            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(content=self.prompt_message.format(description=query)),
            ]
            response = await self._agenerate_response(messages, force_gpt4=True, run_manager=run_manager)

            image_url_link = "```ImageURL" + image_url + "```"

            if run_manager is not None:
                await run_manager.on_text(
                    image_url_link,
                    data_type=StreamingDataTypeEnum.appendix,
                    tool=self.name,
                    step=1,
                    title=self.appendix_title,
                )
            return response

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    @staticmethod
    def generate_image(description: str) -> str:
        """Generate an image based on the description."""
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.Image.create(prompt=description, n=1, size="1024x1024")
            image_url = str(response["data"][0]["url"])
            return image_url
        except:
            return "ERROR: could not generate the image based on the description: " + description
