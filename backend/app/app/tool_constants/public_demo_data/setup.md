# Setup
If this is your first time setting up AgentX, please use the recommended installation method ([development setup modes](docs/setup_development.md) if hot-reload is required). We will run the backend app as well as the frontend app inside a Docker container.

### Prerequisites
- Docker: https://www.docker.com/get-started

### Installation steps

1. Clone the repository containing the source code for the backend and frontend apps.

2. Copy the `.env.example` file in the root directory of the repository and change the name to `.env`.
   - Change the OPENAI_API_KEY and OPENAI_ORGANIZATION to your own (n.b. OPENAI_ORGANIZATION should be your OpenAI 'Organization ID', not 'Organization name'):
      ```sh
      OPENAI_API_KEY=<your_openai_api_key>
      OPENAI_ORGANIZATION=<your_openai_organization>
      ```
3. Copy the `frontend/.env.example` file in the frontend directory and change the name to `.env`.

4. In the terminal, navigate to the root directory of the cloned repository. Build and start the Docker containers using the `docker-compose.yml` configuration file:
   ```
   docker-compose -f docker-compose.yml up -d
   ```

5. Wait for the containers to build and start. This may take a few minutes depending on your system. Once the containers are up and running, you can access the apps in your browser:
   - Frontend app (Next.js): [http://localhost](http://localhost/)
   - Backend app (FastAPI): http://localhost/api/v1

6. You have successfully installed and run the apps using Docker and the Caddy reverse proxy!

## (Optional) Langchain tracing (Langsmith)

See https://docs.smith.langchain.com/ on how to set up LangSmith. Once you have set up LangSmith and the .env variables, you will be able to see the AgentX traces in LangSmith.

## (Optional) Pre-commit

We are using pre-commit to automatically run some hygiene checks. Install this by running `make install-pre-commit`

There is also a dockerized service that can be run using `docker-compose run pre-commit`

To link this from a local python installation, run:
```sh
pip install pre-commit
cp pre-commit/.pre-commit-config.yaml .
pre-commit install
```
