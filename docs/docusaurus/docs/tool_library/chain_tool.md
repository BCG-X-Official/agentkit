# Chain Tool

## How it works

This tool provides a demonstration of injecting external chains into a single tool that's called by the meta agent.

It uses an example of a nested meta agent chain and gives an example of how to execute, passing callbacks correctly,
using a second meta-agent using the constructor in `app.services.chat_agent.meta_agent.create_meta_agent`.

```python
response = await chain.acall(
    dict(**chain_inputs),
    callbacks=run_manager.get_child() if run_manager else None
)
```

It notes how to force output from something other than a tool run to the frontend.

```python
await run_manager.on_text(main_response, data_type=StreamingDataTypeEnum.llm)
```
