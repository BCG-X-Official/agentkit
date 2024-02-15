# Optional Features

In addition to the core functionality, AgentKit supports optional security and tracking features out of the box.

## Tracing & evaluation with local LangSmith

To use a self-hosted langchain in docker, ensure the docker containers are running and `LANGCHAIN_TRACING_V2` is set to `true` and `LANGCHAIN_ENDPOINT` to `"http://langchain-backend:1984"` (see below).
Note that `LANGCHAIN_API_KEY` must be set, but will not be used in self-hosted context.

Stored runs and feedback can be accessed at [http://localhost:9091](http://localhost:9091)

```
#############################################
# Langsmith variables
#############################################
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="http://langchain-backend:1984"
LANGCHAIN_API_KEY="not-used" # must be set to real key if using hosted - key must be set for self-hosted
LANGCHAIN_PROJECT="default"
```

Ensure the docker containers for langsmith are running:
```
langchain-playground:
    image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-playground@sha256:f61ce9762babcb4a51af3e5b0cc628453ac7087237c5fc8694834de49b56d16e

  langchain-frontend:
    image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-frontend@sha256:e0ab157b2b9cb7f75743d45237f0d8ede75a3811d913f234585484255afe5b5a
    ports:
      - 9091:80
    expose:
      - 9091
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://langchain-backend:1984
    depends_on:
      - langchain-backend
      - langchain-playground
    volumes:
      - ./conf/nginx.conf:/etc/nginx/default.conf:ro

  langchain-backend:
    image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-backend@sha256:1196c12308b450548195c10927d469963c7d8e62db0e67f8204c83adb91f9031
    environment:
      - PORT=1984
      - LANGCHAIN_ENV=local_docker
      - LOG_LEVEL=warning
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - 1984:1984
    depends_on:
      - langchain-db

  langchain-db:
    image: postgres:14.1
    command:
      [
        "postgres",
        "-c",
        "log_min_messages=WARNING",
        "-c",
        "client_min_messages=WARNING"
      ]
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=postgres
    volumes:
      - langchain-db-data:/var/lib/postgresql/data
    ports:
      - 5433:5432

  langchain-redis:
    image: redis:7
    ports:
      - 63791:6379
    volumes:
      - langchain-redis-data:/data

  langchain-queue:
    image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-backend@sha256:1196c12308b450548195c10927d469963c7d8e62db0e67f8204c83adb91f9031
    environment:
      - LANGCHAIN_ENV=local_docker
      - LOG_LEVEL=warning
    entrypoint: "rq worker --with-scheduler -u redis://langchain-redis:6379 --serializer lc_database.queue.serializer.ORJSONSerializer --worker-class lc_database.queue.worker.Worker --connection-class lc_database.queue.connection.RedisRetry --job-class lc_database.queue.job.AsyncJob"
    depends_on:
      - langchain-redis

  langchain-hub:
    image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainhub-backend@sha256:73b4c2c3e7cd81729e766bb4eece2b28883bebf7c710567a21d1a6c114abff5a
    environment:
      - PORT=1985
      - LANGCHAIN_ENV=local_docker
      - LOG_LEVEL=warning
    ports:
      - 1985:1985
    depends_on:
      - langchain-db
      - langchain-redis
```


## Tracing & evaluation with hosted Langsmith

To use hosted Langsmith, set `LANGCHAIN_ENDPOINT` to `"https://api.langchain.plus"` and fill `LANGCHAIN_API_KEY`:

1. Create an API Key by navigating to the [settings page](https://smith.langchain.com/settings).
2. Configure runtime environment - replace `<your-api-key>` with the API key generated in step 1

```
#############################################
# Langsmith variables
#############################################
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.langchain.plus"
LANGCHAIN_API_KEY="<your-api-key>"
LANGCHAIN_PROJECT="default"
```

## User chat feedback integration

> Note: LLM Run tracing must be enabled for this feature.

To enable feedback from the tool frontend, set `NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK` in the /frontend/.env file is set to `true`,

A pop-up will appear after each message giving the user the ability to rate the message quantitatively (thumbs up/down) and qualitatively (comment). This functionality can be useful e.g. for a PoC user testing session for your application. It can be further customised by adjusting the `FeedbackView` typescript file.

<img src="/docs/img/feedback_feature.png" alt="Feedback popup" width="500" />

Frontend implementation: [frontend/src/components/ConversationView/MessageView/FeedbackView/index.tsx](frontend/src/components/ConversationView/MessageView/FeedbackView/index.tsx)
Backend route: [backend/app/app/api/v1/endpoints/statistics.py](backend/app/app/api/v1/endpoints/statistics.py)


### Retrieving Feedback results:
1. Via the UI:
   Feedback is collected in Langsmith as for LLM runs - Navigate to http://localhost:9091 (https://smith.langchain.com/ if using hosted) and select the project.
2. Via python API: by following example scripts at https://docs.smith.langchain.com/cookbook/exploratory-data-analysis/exporting-llm-runs-and-feedback
3. Via DB: by connecting to the DB directly in `public.runs` / `public.feedback` at `jdbc:postgresql://localhost:5433/postgres`


## User authentication

User authentication can be done through NextAuth. Set `NEXT_PUBLIC_USE_AUTH` to `true` and fill the 'NEXTAUTH_SECRET' variable in `frontend/.env` with the generated secret key. A secret key can be generated using:
```
openssl rand -base64 32
```
For more information, check the [NextAuth documentation](https://next-auth.js.org/configuration/options#secret).
Additionally, if you want to enable GitHub authentication, the `GITHUB_ID` and `GITHUB_SECRET` in `frontend/.env` should be filled with the corresponding values from your GitHub app credentials.

<img src="/docs/img/auth_feature.png" alt="Feedback" width="500" />

## User settings
The user can configure custom settings in the UI in the 'Settings' modal, providing an option for the user to configure settings which can affect the prompts. The configured setting can be accessed in the `query` object:
```
tool_input = ToolInputSchema.parse_raw(query)
settings = tool_input.user_settings
```
These settings can then be used in any of the tools, e.g. as input to prompts.

<img src="/docs/img/settings_feature.png" alt="Settings" width="500" />
