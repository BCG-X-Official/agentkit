---
sidebar_position: 1
---

# Introduction
AgentKit is a LangChain / FastAPI / Next.js14 toolkit developed by BCG X to build Agents. Developers can use AgentKit to rapidly build high quality Agent applications that can scale into production-grade apps.

Key advantages of AgentKit include:
- 🚀 **Quickly build high quality Agent apps**: Modular, easy to configure tech stack and a library of useful GenAI tools allows developers to build a strong Agent app in hours
- 💻 **Flexible, reactive UI/UX designed for Agents**: React/Nextjs chat-based UI that is easy to configure, with features such as streaming, rendering of tables/visualizations/code, status of Agent actions and more
- 🛡️ **Focus on reliability**: Easy to configure routing architecture gives control of possible paths Agent can take, increasing reliability and making it suited for real-life use cases

As an example, try the AgentKit codebase helper [demo](https://agentkit.infra.x.bcg.com/)
<!-- TODO: add video -->


## Chinook music database demo
For a quick start to test some of the functionality, you can use the dummy Chinook example:
- If docker containers are running, run `docker-compose down --volumes`
- Follow the [installation instructions](docs/setup/setup.md) and swap `docker-compose.yml` with `docker-compose-demo.yml` to run the app
- Try the prompt "How many artists and songs are there in the database?" to see AgentKit in action!

## New users: Customize your agent app in 15 minutes
- [Configure your Agent and Tools](docs/configuration/configure_agent_and_tools.md)
- [Adjust the UI to your use case](docs/configuration/configure_ui.md)
- Ask the [AgentKit codebase helper](https://agentkit.infra.x.bcg.com/) if you need help!

## Advanced users: Prepare your app for production
- [Tech stack and code structure](docs/advanced/overview_codebase.md)
- [Set up evaluation with LangSmith](docs/advanced/evaluation.md)
- [Run linting and tests for the application](docs/advanced/linting_and_tests.md)
- [Set up and run acceptance tests with cypress](docs/advanced/aat_guidelines.md)
- [Add additional features, such as auth, feedback and user settings](docs/advanced/optional_features.md)
- [Deploy your app] TODO: deployment documentation link
