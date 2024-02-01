# Visualizer tool

## How it works

The visualizer tool can generate visualizations dynamically using [Recharts](https://recharts.org/en-US/). As input, the tool takes a number of rows of data (from the output of the `sql_tool`) and the user prompt to generate Recharts code that can then be rendered in an appendix. The appendix builds the visualization in Recharts using the full data from the executed SQL query as input.

As a best practice, it helps to include clear examples of visualizations in the prompt custom to your use case. These can be added in `prompt_inputs` for `visualizer_tool` in `tools.yml`.

<img src="/docs/img/img_visualizer_tool.png" alt="Viz" width="400"/>
