# Entertainer and Expert tools

The entertainer and expert tools are simple tools: they only execute a single LLM call. However, we have a couple of different uses for these tools.

## Entertainer tool

The entertainer tool is typically used to ...entertain the user with some initial streamed output while long chains are running and executing complex queries that take time to generate output. The tool typically uses a cheap, fast LLM call, and is added as a subitem in the first action step, such that output is generated immediately after the user submits their prompt.

To clarify to the user that this output is a preliminary output, and should not be considered in the final output, a UI distinction is built in that is triggered if the text starts with "Thought: " (see `LLMResponse.tsx`). Therefore, ensure that the prompt for the entertainer tool instructs the LLM to start its answer with "Thought: ". Note: this UI trigger can also be used when using a ReAct agent instead of a constrained agent, to distinguish the 'thoughts' of the agent with the final answer.

## Expert tool

The expert tool is typically used to provide expert output, such as drawing conclusions from data, generating complex documents, or answering user questions.

Typically, best practice is to structure the prompt clearly and provide a clear goal:
```
system_context: |-
      You are an expert in [topic]. Your goal is to [].

      You must format your answer as follows:
      - Answer in beautiful Markdown
      - ...

      You MUST adhere to the following guidelines:
      - Answer using only the provided information
      - ...
```

## Clarify tool

The clarify tool can be used to attempt to catch unclear or unhelpful / offensive prompts, and return an ask to the user to clarify / change their prompt. Ensure the action plan description has a clear description of when to use this tool, e.g. "Ask the user to clarify the input question".
