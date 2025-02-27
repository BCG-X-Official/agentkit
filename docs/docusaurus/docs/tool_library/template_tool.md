# Template tool

Here is how you can extend Agentkit Tools with your own custom tool. 

## Option 1: Use an existing tools

AgentKit already provide a set of existing Tool implementations. 
If your need it to simply adjust the prompts and options of an existing tools without changing the logic, you can do so by adjusting the `tools.yaml` configuration file.

For example, for a poem generator tool, you might want to adjust the prompts and options of the `BaseLLM` tool.

```yaml
library:
  poem_generator:
    class_name: "app.services.chat_agent.tools.library.basellm_tool.basellm_tool:BaseLLM" # reference the LLMTool, is nice starting point
    description: "Generate a poem based on a given input."
    prompt_message: "Generate a poem based on the following input: {question}"
    system_context: "You are a poem generator. You will generate a poem based on the input."
```

Then just use the tool in your action plan as you would with any other tool.


```yaml
tools: # 
  - poem_generator
action_plans: 
  '0':
    name: ''
    description: Answer the user's request
    actions: # each sublist is 1 action step, i.e. add tools as subitems if you want to execute in parallel
      - - poem_generator
```

You can pick your implementation from the following list:

* **BaseLLM**

  class_name: `app.services.chat_agent.tools.library.basellm_tool.basellm_tool:BaseLLM`

  Implements the ability to use a LLM model to generate text based on configured prompts

* **SQLTool**

  class_name: `app.services.chat_agent.tools.library.sql_tool.sql_tool:SQLTool`

  Implements SQL database interactions and queries.

* **JsxVisualizerTool**

  class_name: `app.services.chat_agent.tools.library.visualizer_tool.visualizer_tool:JsxVisualizerTool`

  Enables the visualization of JSX components.

* **SummarizerTool**

  class_name: `app.services.chat_agent.tools.library.summarizer_tool.summarizer_tool:SummarizerTool`

  Provides functionality for summarizing text content.

* **PDFTool**

  class_name: `app.services.chat_agent.tools.library.pdf_tool.pdf_tool:PDFTool`

  Perform a RAG operation on textual documents.

* **ImageGenerationTool**

  class_name: `app.services.chat_agent.tools.library.image_generation_tool.image_generation_tool:ImageGenerationTool`

  Supports the generation of images based on specified prompt.


## Option2: Create a new tool

If you need to create a new tool, you can do so by creating a new class that extends the `ExtendedBaseTool` class. 
You don't *have to* nest your tool inside the `app.services.chat_agent.tools` package, the only requirement is that the class is importable by the backend of AgentKit (i.e. it is in the python path).

Assuming you have you code in a folder called `my_tools` and the file is called `echo.py` and the `__init__.py` file along with it.

The minimal requirements for a tool are a class that extends `ExtendedBaseTool` and implements the `_arun` methods.

```python 
# my_tools/echo.py
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

class EchoTool(ExtendedBaseTool):
    # define the name of your tool, matching the name in the config [TODO: remove this constraint.] 
    name = "echo_tool"

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        # very simple tool that just Echoes the input back. See bellow for more complex example
        return query 
```

Then reference your class in the `tools.yaml` configuration file :

```yaml
library:
  echo_tool: 
    class_name: "my_tools.echo:EchoTool" # package_name:class_name
    description: "A dummy tool for testing"
    prompt_message: "This is a dummy tool. You will see this message: {question}"
    system_context: "You are using the dummy tool."
```

The final step is to make sure agent kit can load your package. 


### For docker users

The docker that runs the backend agent is actually "Guaranted" to have the `/code` folder in the python path. So you can just volume mount your folder in the `/code` folder and it will be importable. 

```yaml

# somewhere in the docker-compose-xxxx.yml you are using
services:
  fastapi_server:
    ... # some options about the server
    volumes:
      ... # probeably existing mounts
      - ./mytools:/code/my_tools # Here, add this at the bottom of the list
```

Finally you need to down & up (restart might not be enough for a such a change) the docker container with `docker compose -f <your compose file>  down` and `docker compose -f <your compose file> up -d`.



### For "on my machine" developpers

You might already run the back end with hand like with `uvicorn app.main:app` and the current folder is usually considered as part of the python path. 

If not, then trouble shoot by listing the python path with `python -c "import sys; print(sys.path)"` and make sure your package is in one of the listed folders.

Adjust the PYTHONPATH environment variable with
* Linux `export PYTHONPATH=$PYTHONPATH:/path/to/your/folder`
* Windows `set PYTHONPATH=%PYTHONPATH%;C:\path\to\your\folder`

If still not, just consider using docker. 



### Example of a more complex tool

The following tool is a more complex example of a tool that uses a LLM model to generate extra messages and return them as an appendix DataType. 


```python
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
