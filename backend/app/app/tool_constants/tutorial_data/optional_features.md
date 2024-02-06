# Optional Features

In addition to the core functionality, AgentKit supports optional security and tracking features out of the box.

## LLM Run Tracing

To use a self-hosted langchain in docker, set `LANGCHAIN_TRACING_V2` to `true` and `LANGCHAIN_ENDPOINT` to `"http://langchain-backend:1984"`, e.g.
Note that `LANGCHAIN_API_KEY` must be set, but will not be used in self-hosted context.

You will access stored runs / feedback at [http://localhost:9091](http://localhost:9091)

```
#############################################
# Langsmith variables
#############################################
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="http://langchain-backend:1984"
LANGCHAIN_API_KEY="not-used" # must be set to real key if using hosted - key must be set for self-hosted
LANGCHAIN_PROJECT="default"
```

### Hosted Langsmith

To use hosted Langsmith, set `LANGCHAIN_ENDPOINT` to `"https://api.langchain.plus"` and fill `LANGCHAIN_API_KEY`:

1. Create an API Key by navigating to the [settings page](https://smith.langchain.com/settings).
3. Configure runtime environment - replace "<your-api-key>" with the API key generated in step 1

```
#############################################
# Langsmith variables
#############################################
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT="https://api.langchain.plus"
LANGCHAIN_API_KEY="<your-api-key>"
LANGCHAIN_PROJECT="default"
```

## Feedback integration

> Note: LLM Run tracing must be enabled for this feature.

To enable feedback from the tool frontend, set `NEXT_PUBLIC_ENABLE_MESSAGE_FEEDBACK` in the /frontend/.env file is set to `true`,

A pop-up will appear after each message giving the user the ability to rate the message quantitatively (thumbs up/down) and qualitatively (comment). This functionality can be useful e.g. for a PoC user testing session for your application. It could be further customised by adjusting the `FeedbackView` typescript file.


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
