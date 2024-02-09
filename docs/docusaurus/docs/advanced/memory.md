# Memory Management for Tools

## Introduction

Memory management is a crucial aspect of building agents that can provide relevant and context-aware responses to user queries. The memory in this context refers to all context from previous user interactions (chat history) or actions (output from previously executed tools) a tool needs to perform its task optimally. Effective memory management and filtering are vital to ensure that only relevant context is passed into the tool. This reduces the 'noise' of unimportant tokens in the tool's LLM calls, increasing output quality and reducing cost and latency.

**Chat history:** provides the context of the user's previous conversation. This context is essential for the agent to understand the user's current query in the right perspective. For instance, a user's current query might be a follow-up question or a query related to a previous discussion. Without the context provided by the chat history, the agent might not be able to provide a satisfactory response.

**Previous tool output:** provides context of the tools run in intermediate steps of the action plan executed before the current tool. For example, a tool might have retrieved some data that is relevant to the user's current query. By including this data in the memory of the next tool, the agent can provide a correct response.

## Memory manipulation

The memory object is defined by `ToolInputSchema`:
- `chat_history`: This is a list of messages exchanged between the user and the AI, including intermediate tool outputs of previous steps in the conversation. Each message is either a HumanMessage or an AIMessage. The chat history can be passed into a tool prompt, and can be manipulated to only include relevant context, or reduced to limit the number of tokens in the prompt.

- `latest_human_message`: This is the most recent message from the user. It's often the question or command that the tool needs to respond to.

- `user_settings`: This is a `UserSettings` object that contains any user-specific settings or data that might influence the tool's behavior.

- `intermediate_steps`: This is a dictionary that contains the outputs of any previous tools that have been run in the current action plan.

The memory object is created in `SimpleRouterAgent.py`. First, the object is created during each action step and filled with the intermediate steps so far in the action plan:
```
tool_input = ToolInputSchema(
                latest_human_message=kwargs["input"],
                chat_history=[],
                user_settings=UserSettings(**kwargs["user_settings"].dict()) if kwargs["user_settings"] else None,
                intermediate_steps={},
            )
            if len(intermediate_steps) > 0:
                tool_appendix_titles = {
                    tool.name: getattr(
                        tool,
                        "appendix_title",
                        "",
                    )
                    for tool in self.tools
                }
                tool_input.intermediate_steps = {
                    tool_appendix_titles[step[0].tool]: step[1] for step in intermediate_steps
                }
```
Then, the chat history is filled if it exists and if `memory` is one of the action steps:
```
    elif "memory" in next_actions and "chat_history" in kwargs:
        tool_input.chat_history = kwargs["chat_history"]
```
To include chat history in your action step, add `memory` to the step in `agent.yml`, e.g.
```
actions:
      - - memory
        - expert_tool
```

The object will look like
```
{
    "chat_history": [{"content": "user message 1"}, "additional_kwargs": {}, "type": "human", "example": "false"], [{"content": "AI response 1"}, "additional_kwargs": {}, "type": "ai", "example": "false"], ...},
    "latest_human_message": "latest user prompt",
    "user_settings": {"data": {configured user settings}},
    "intermediate_steps": {"tool_name_1": "output", "tool_name_2": "output", ...}
}
```

The memory object is passed to the tools as the `query` argument in the `_arun` function, where it can be used to customize the context for a given tool. For example, we may only want to provide the output of the `sql_tool` and the original user question in a prompt for a different tool. This can be easily done by accessing parts of the memory object:
```
tool_input = ToolInputSchema.parse_raw(query)
question = tool_input.latest_human_message
results = tool_input.intermediate_steps["sql_tool"]
messages = [
    SystemMessage(content=self.system_context.format()),
    HumanMessage(
        content=self.prompt_message.format(
            question=question,
            results=results,
        ))]
```

For most library tools, the below standard query formatting is used (defined in `query_formatting.py`):
```
Chat history: ...
Intermediate tool outputs: ...
Latest user question: ...
```
