# Evaluation

Evaluating an AgentKit app can be done on multiple levels:
- Routing layer: Evaluate the meta agent's accuracy of choosing the right action plan based on the user query
- Tool layer: Evaluate individual tools
- Output layer: Evaluate the final output quality

<img src="../static/evaluation_layers.png" alt="AgentKit evaluation layers" style="width:500px;"/>

See `experimental/evaluation_example.ipynb` for an example of evaluating an AgentKit app in a notebook.

AgentKit natively integrates with LangSmith, which is a useful tool for tracing and tracking the performance of your app. https://docs.smith.langchain.com/
