# Evaluation

Evaluating an AgentKit app can be done on multiple levels:
- Routing layer: Evaluate the meta agent's accuracy of choosing the right action plan based on the user query
- Tool layer: Evaluate individual tools
- Output layer: Evaluate the final output quality

<img src="/docs/img/evaluation_layers.png" alt="AgentKit evaluation layers" width="500" />

AgentKit natively integrates with LangSmith, which is a useful tool for tracing and tracking the performance of your app. https://docs.smith.langchain.com/

See [Optional Features](docs/advanced/optional_features.md) for instructions to set up LangSmith.
