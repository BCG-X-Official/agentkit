## Configuring Different LLMs with AgentKit

While the default implementation of AgentKit uses GPT-4, it is fairly straightforward to configure a different LLM provider, e.g. Anthropic. 

Follow these steps to change the LLM: 

* Add a Langchain LLM to `llm.py`: You can add any LLM here as long as it's supported by a Langchain chat model. For example: 
```python
case "claude-3-opus":
    return ChatAnthropic(
        temperature=0,
        model_name="claude-3-opus-20240229",
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        streaming=True,
    )
```
You will need to set `streaming=True` and ensure that the given chat model supports asynchronous streaming. 

* Add an API key (or other environment variables needed to make an LLM call) to your `.env`. You should read through the Langchain chat model documentation to determine what other inputs you might need. 

* Go to `schemas/tool_schema.py` and update the list of acceptable LLM inputs by changing the `LLMTypeObject`

* Finally, update the LLM being used in `config/agent.yml`, setting it to match the name which you set in `llm.py`. 

This should be all, but you should note that not all Langchain versions will support asynchronous streaming for all LLMs, even if they offer a chat model wrapper. For example, in the Langchain 0.1.x series, Google's gemini models don't support asynchronous streaming and hence do not integrate well with AgentKit's off-the-shelf frontend. Getting this to work will require a bugfix on Langchain's part in a future version (which has been implemented in Lanchain 0.2+), or a lower-level change to the AgentKit code. 

