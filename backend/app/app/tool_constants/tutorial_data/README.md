<img src="static/AgentKit_logo_color.png" alt="AgentKit logo" style="width:500px;"/>

# AgentKit: rapidly build Agent apps
AgentKit is a LangChain-based toolkit developed by BCG X to build Agent apps. Key advantages of the AgentKit framework include:
- 🚀 **Quickly build high quality Agent apps**: Build a strong demo in a few hours using a modular, easy to configure tech stack based on FastAPI/Nextjs and a library of useful GenAI tools
- 💻 **Flexible, reactive UI/UX designed for Agents**: React/Nextjs chat-based UI that is easy to configure, with features such as streaming, rendering of tables/visualizations/code, status of Agent actions and more
- 🛡️ **Focus on reliability**: Easy to configure routing architecture gives control of possible paths Agent can take, increasing reliability and making it suited for real-life use cases

[Placeholder for demo video]

## Quickstart
For a quick setup of AgentKit, use the steps below, where both the backend app and frontend app are run inside a Docker container. More elaborate setup instructions can be found at [setup.md](docs/setup.md).

### Prerequisites
- Docker: https://www.docker.com/get-started

### Installation steps
1. Clone the repository containing the source code for the backend and frontend apps.

2. Copy the `frontend/.env.example` file in the frontend directory and change the name to `.env`. Also, copy the `.env.example` file in the root directory of the repository and change the name to `.env`.
   - Change the OPENAI_API_KEY and OPENAI_ORGANIZATION to your own (n.b. OPENAI_ORGANIZATION should be your OpenAI 'Organization ID')

3. In the terminal, navigate to the root directory of the cloned repository. Build and start the Docker containers with the following command:
   ```
   docker-compose -f docker-compose.yml up -d
   ```
   Wait for the containers to build and start, which may take a few minutes depending on your system. Once the containers are up and running, you can access the apps in your browser at [http://localhost](http://localhost/).

## Chinook music database demo
- Ensure you are on the `develop` branch
- Follow the installation instructions above and run the app
- Try the prompt "When was AC/DC founded?" to see AgentKit in action!

## Set up your own app
- Configure your Agent and Tools [link](docs/configure_agent_and_tools.md)
- (Optional) Adjust the UI to your use case [link](docs/configure_ui.md)
- (Optional) Set up evaluation with LangSmith [link](docs/evaluation.md)

## Documentation
- [Installation instructions for running frontend or entire app outside Docker](docs/setup_development.md)
- [Key concepts](docs/key_concepts.md)
- [Agent configuration](docs/configure_agent.md)
- [UI configuration](docs/configure_ui.md)
- [Optional features](docs/optional_features.md)
- [Tool library](docs/tool_library.md)

## How it works

### Reliability
AgentKit attempts to solve the reliability issue of agents such as ReAct agents by constraining the potential routes the agent can take to a pre-configured sets of routes, or **Action Plans**. Since for many use cases the potential routes the agent can take are known, we can use our human domain expertise to steer the agent in the right direction, and reduce it going into unexpected directions or rabbit holes. This is achieved by combining a **Meta Agent** with **Action Plans**: A set of tools which are executed linearily and in parallel, similar to a Chain. The Meta Agent takes in the user prompt and outputs the most suited Action Plan to generate an answer. Note: implementing multiple Meta Agents is possible, generating a tree of possible routes.

### User experience
To optimize user experience, the intermediary output of every step in the Action Plan can be shown to the user. For example, consider an Action Plan consisting of 2 toolsets: `[[sql_tool, pdf_tool], [generate_summary_tool, visualize_tool]]`. In the first action step, information from a SQL database and a vector database with embedded PDFs are retrieved in parallel. The retrieved data and most relevant PDF are streamed to the UI as soon as the first action step finishes. In the second action step, the output from step 1 is passed to a tool that generates a text summary and a tool that creates a JSX visualization from the data, which is streamed to the UI to create the final answer.

For a high level overview of the routing flow and connection the UI, please see below diagram:
<img src="static/AgentKit_flow_diagram.png" alt="AgentKit framework" style="width:500px;"/>

## Additional optional features

- **Feedback integration**: allow users to give feedback on generated answers by showing a pop up after each message with quantitative (thumbs up/down) and qualitative (comment) feedback

[placeholder for picture of feedback feature]

- **User settings**: Allow users to specify default settings in the app that can be used to customize prompts for the user

[placeholder for picture of settings feature]

- **User authentication**: Enable NextAuth on your app to authenticate users with Github or with email/password

[placeholder for picture of authentication feature]

See [optional feature documentation](docs/optional_features.md) for more detailed info.

## Contributors

[Placeholder for contributor list]
Please read `CONTRIBUTING.md` for more details on how to contribute.
