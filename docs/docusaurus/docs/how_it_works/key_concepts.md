# Key concepts

## Reliability
AgentKit attempts to solve the reliability issue of agents such as ReAct agents by constraining the potential routes the agent can take to a pre-configured sets of routes, or **Action Plans**. Since for many use cases the potential routes the agent can take are known, we can use our human domain expertise to steer the agent in the right direction, and reduce it going into unexpected directions or rabbit holes. This is achieved by combining a **Meta Agent** with **Action Plans**: A set of tools which are executed linearily and in parallel, similar to a Chain. The Meta Agent takes in the user prompt and outputs the most suited Action Plan to generate an answer. Note: implementing multiple Meta Agents is possible, generating a tree of possible routes.

## Transparency
To optimize user experience and transparency, the intermediary output of every step in the Action Plan can be shown to the user. For example, consider an Action Plan consisting of 2 toolsets: `[[sql_tool, pdf_tool], [generate_summary_tool, visualize_tool]]`. In the first action step, information from a SQL database and a vector database with embedded PDFs are retrieved in parallel. The retrieved data and most relevant PDF are streamed to the UI as soon as the first action step finishes. In the second action step, the output from step 1 is passed to a tool that generates a text summary and a tool that creates a JSX visualization from the data, which is streamed to the UI to create the final answer.

## Flow Diagram
For a high level overview of the routing flow and connection the UI, please see below diagram:
<img src="/docs/img/agentkit_flow_diagram.png" alt="AgentKit framework" width="1000"/>

## Terminology

- **Actions**: One of the steps to obtain an answer to the user's query, corresponding to executing a Tool(chain). An action has its own action-renderer for visualization in the frontend.

- **Action Step**: A pre-configured set of actions, e.g. sql_tool and pdf_tool. An action step can consist of multiple actions which are executed in parallel to achieve a certain outcome (e.g. retrieve information).

- **Action Plan**: A set of action steps which are executed linearily to achieve a certain outcome. For example, consider an action plan consisting of 2 toolsets: [[tool_1, tool_2], [tool_3, tool_4]]. In the first action step, tool_1 and tool_2 are executed in parallel and generate output. In the second action step, this output is passed to tool_3 and tool_4, which are executed in parallel, and the final output is passed to the frontend.

- **LLM Outputs**: Text output of an LLM from a Tool that is streamed to the frontend (e.g. output from explainer tool). In the output section, there is a preliminary LLM output (currently only from entertainer tool) and a final LLM output (final answer of agent).

- **Appendices**: Additional objects that are added below the final LLM output, such as visualizations, tables etc.

- **Signals**: Signals sent from backend of output status. E.g. 'Action ended', 'LLM Output final'.
