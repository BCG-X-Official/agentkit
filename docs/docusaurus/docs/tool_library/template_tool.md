# Template tool
Below is an example of a template tool to configure for your use case.

```
from typing import Optional, List, Tuple
from app.db.session import sql_tool_db
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.db.session import sql_tool_db
from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool


class ReadMeTool(ExtendedBaseTool):
    # define the name of your tool, matching the name in the config
    name = "readme_tool"
    appendix_title = "readme Appendix"

    @classmethod
    def from_config(cls, config: ToolConfig, common_config: AgentAndToolsConfig, **kwargs):
        llm = kwargs.get("llm", get_llm(common_config.llm))
        fast_llm = kwargs.get("fast_llm", get_llm(common_config.fast_llm))
        fast_llm_token_limit = kwargs.get("fast_llm_token_limit", common_config.fast_llm_token_limit)

        # add all custom prompts from your config, below are the standard ones
        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
        )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""

        raise NotImplementedError("ReadMeTool does not support sync")

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            # if you want to stream the action signal to the frontend (appears in 'Steps')
            if run_manager is not None:
                await run_manager.on_text(
                    "readme_action",
                    data_type=StreamingDataTypeEnum.ACTION,
                    tool=self.name,
                    step=1,
                )

            # implement your custom tool here
            def func_that_does_something(query):
                return query

            response = func_that_does_something(query)

            # if the tool is only a LLM call, you can use the following code
            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(content=self.prompt_message.format(question=query)),
            ]
            response = await self._agenerate_response(messages, discard_fast_llm=True, run_manager=run_manager)

            # if you want to stream the response to an Appendix
            if run_manager is not None:
                # appendix 1
                await run_manager.on_text(
                    response,
                    data_type=StreamingDataTypeEnum.APPENDIX,
                    tool=self.name,
                    step=1,
                    title=self.appendix_title,
                )
                # appendix 2 (appears below appendix 1)
                await run_manager.on_text(
                    response,
                    data_type=StreamingDataTypeEnum.APPENDIX,
                    tool=self.name,
                    step=2,
                    title=self.appendix_title,
                )
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e
```
