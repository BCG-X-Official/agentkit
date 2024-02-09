# Configure your agent and tools

## Steps to complete
- Configure your agent in `agent.yml`, [see agent section for more detailed instructions](#agent-configuration)
- Add your own tools in `services/chat_agent/tools/YOURAPP` and configure them in `tools.yml`, [see tools section for more detailed instructions](#tools-configuration)


## Agent configuration

The agent and action plans can be configured in `agent.yml`.

### LLMs

`default_llm` & `default_fast_llm`: Set the name of the LLMs you want to use. In `llm.py` you can add your own model (any model compatible with LangChain e.g. Google, Anthropic, or open source like Llama2).

We currently have 2 ways to choose if `default_llm` or `default_fast_llm` is used.
- If you set `discard_fast_llm=True` to True in the LLM call in a tool, `default_llm` will always be used
- [TO BE CHANGED] Otherwise, `default_fast_llm` will be used for prompts < 2500 tokens (configurable in ExtendedBaseTool.py currently, needs to be cleaned up to add as a key setting) and `default_llm` for >=2500 tokens

### Tools and Action Plans
Add all the tools in use in `tools`. Ensure the names match the tool names in `tools.py` and your custom tools.

Configure the Action Plans available for the Meta Agent to choose from in `action_plans`. Give each Action Plan a clear `description` of what the use case is, this will improve the reliability and accuracy of the Meta Agent. Add all the tools in `actions`. Each sublist is 1 action step, so add tools as subitems if you want to execute them in parallel.

### Meta agent prompts

It is very important to have a clear system prompt in `system_context` for the Meta Agent so that it chooses the right Action Plans (`prompt_message` typically can typically be kept the same). Always include a role for the agent ("You are an expert in ...") and a clear goal ("Your goal is to select the right action plan.."). Include some principles to ensure the agent has the right behaviour for the use case, e.g. only run an optimization when the agent is very sure the user wants this, as it takes a lot of time. If there are common failure modes in the agent's routing choices, add a principle or add an example of good behaviour to solve it.

## Tools configuration

### Using a library tool
Check out the library of commonly used tools in `services/chat_agent/tools/library`. Using these tools is simple; ensure the tool is in the `tools` list in `agent.yml` and configure the prompts in `tools.yml`. Detailed documentation on the library tools can be found in `docs/library_tool_docs`.

### Add a tool

1) Add your own tool folder to `services/chat_agent/tools` with a new file `yourtool.py`
2) Implement your tool. See `template_tool.py` for a template tool, or look at the other library tools for inspiration
3) In `tools.py`, add the tool in `all_tool_classes` and import it
4) Add the tool in `tools` in `agent.yml` and add the tool to the applicable action plans
5) Add your tool and configure the tool and prompts in `tools.yml`

Optional:
Customize the Actions for the tool in the UI, see [the UI documentation](configure_ui.md).
