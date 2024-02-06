WIP: tbd if needed

## Key concepts

- **Actions**: One of the steps to obtain an answer to the user's query, corresponding to executing a Tool(chain). An action has its own action-renderer for visualization in the frontend.
- **Action Step**: A pre-configured set of actions, e.g. sql_tool and pdf_tool. An action step can consist of multiple actions which are executed in parallel to achieve a certain outcome (e.g. retrieve information).
- **Action Plan**: A set of action steps which are executed linearily to achieve a certain outcome. For example, consider an action plan consisting of 2 toolsets: [[tool_1, tool_2], [tool_3, tool_4]]. In the first action step, tool_1 and tool_2 are executed in parallel and generate output. In the second action step, this output is passed to tool_3 and tool_4, which are executed in parallel, and the final output is passed to the frontend.
- **LLM Outputs**: Text output of an LLM from a Tool that is streamed to the frontend (e.g. output from explainer tool). In the output section, there is a preliminary LLM output (currently only from entertainer tool) and a final LLM output (final answer of agent).
- **Appendices**: Additional objects that are added below the final LLM output, such as visualizations, tables etc.
- **Signals**: Signals sent from backend of output status. E.g. 'Action ended', 'LLM Output final'.

<img src="../static/AgentKit_flow_diagram.png" alt="AgentKit framework" style="width:500px;"/>
