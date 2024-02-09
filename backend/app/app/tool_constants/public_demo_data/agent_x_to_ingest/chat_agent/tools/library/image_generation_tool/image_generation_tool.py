# -*- coding: utf-8 -*-
import logging
import os
from typing import Optional

import openai
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.text_splitter import TokenTextSplitter

from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class ImageGenerationTool(ExtendedBaseTool):
    """Image Generation Tool."""

    name = "image_generation_tool"
    appendix_title = "Image Appendix"

    image_generation_prompt_template: PromptTemplate

    @classmethod
    def from_config(cls, config: ToolConfig, **kwargs):
        """Create an image generation tool from a config."""
        llm = kwargs.get("llm", get_llm(config.default_llm))
        fast_llm = kwargs.get("fast_llm", get_llm(config.default_fast_llm))

        description_prompt = config.image_description_prompt.format(**{e.name: e.content for e in config.prompt_inputs})

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
            image_generation_prompt_template=PromptTemplate(template=description_prompt, input_variables=["text"]),
        )

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            logger.info("Generating the image")
            tool_input = ToolInputSchema.parse_raw(query)
            tool_outputs = [f"{k}: {v}" for k, v in tool_input.intermediate_steps.items()]
            text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)
            texts = [text for tool_output in tool_outputs for text in text_splitter.split_text(tool_output)]
            docs = [Document(page_content=t) for t in texts]
            chain = load_summarize_chain(
                self.llm,
                chain_type="map_reduce",
                map_prompt=self.image_generation_prompt_template,
                combine_prompt=self.image_generation_prompt_template,
            )
            image_description = await chain.arun(docs)
            image_url = self.generate_image(str(image_description))

            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(content=self.prompt_message.format(description=image_description)),
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
    def generate_image(description):
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            response = openai.Image.create(prompt=description, n=1, size="1024x1024")
            image_url = str(response["data"][0]["url"])
            return image_url
        except Exception:
            return "ERROR: could not generate the image based on the description: " + description
