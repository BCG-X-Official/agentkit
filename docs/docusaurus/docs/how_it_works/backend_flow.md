# AgentKit Backend Flow

The general backend flow is mainly constructed through the following four Python files, each serving a specific purpose.

## chat.py

This is the main backend entry point of AgentKit. It exposes a FastAPI endpoint at `/agent` which accepts POST requests.
The request body should contain a chat query, which is processed by the `agent_chat` function. This function creates a
conversation with an agent and returns an `StreamingJsonListResponse` object.

## meta_agent.py

This file contains functions for creating and managing a meta agent. A meta agent is an instance of the `AgentExecutor`
class, which is responsible for executing AgentKit's logic.
- The `create_meta_agent` function creates a meta agent from a given configuration.
- The `get_conv_token_buffer_memory` function retrieves the chat history and stores it in a
`ConversationTokenBufferMemory` object.

## SimpleRouterAgent.py

This file contains the `SimpleRouterAgent` class. This class is
responsible for managing AgentKit's actions based on the input it receives.
- The `aplan` function decides what actions the agent should take based on the input and the intermediate steps taken so far.
- The `create_prompt` function creates a prompt for the agent.
- The `from_llm_and_tools` function constructs an agent from a language model and a set of tools.

## get_tools.py

This file contains the `get_tools` function, which retrieves a list of tools from a list of tool names. Each tool class
is responsible for a specific functionality of AgentKit.

## Flow

1. A POST request is sent to the `/agent` endpoint with a chat query in the request body.
2. The `agent_chat` function in `chat.py` is called. This function retrieves the meta agent associated with the API key
specified in the chat query.
3. The `agent_chat` function creates a conversation with the agent, handles exceptions, and returns a streaming response.
4. The meta agent, which is an instance of the `AgentExecutor` class, executes AgentKit's logic. This logic is
determined by the `SimpleRouterAgent` class in `SimpleRouterAgent.py`.
5. The `SimpleRouterAgent` class decides what actions the agent should take based on the input it receives and the
intermediate steps taken so far.
6. The `get_tools` function in `get_tools.py` is called to retrieve the tools needed by the agent. These tools are used
to perform various tasks, such as generating images, summarizing text, executing SQL queries, etc.
7. The conversation continues until the agent decides to stop, at which point the `agent_chat` function returns a
`StreamingJsonListResponse` object containing the conversation history.
