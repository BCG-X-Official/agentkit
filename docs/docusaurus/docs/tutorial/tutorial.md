# Tutorial: AgentKit Codebase Helper



Let's run through a full example of how you can rapidly build a high quality Agent application using AgentKit.

We're going to build an Agent which can guide us through a GitHub repository, with access to two sorts of information:

1. **Codebase documentation**: All documentation in the codebase, including setup instructions, overall architecture, and feature-specific docs.
2. **GitHub reposistory commit history**: Commit log from the GitHub repository. We want this data to be in tabular form.

Developers can use this Agent to familiarize themselves with the contents of the repository, ask questions, and track contributions (e.g. "What were the latest commits from Joe to the frontend?"). The agent will use semantic similarity to retrieve information from
the documentation and generate a SQL query to retrieve information from the GitHub repository information.


In this example, we'll use data from the AgentKit repository itself (meta!), but you can do this for any repository.

All it takes is 3 steps:

## Step 1: Ingest data
The first thing we'll do is download all AgentKit docs as PDF. We can also do this in native Markdown format, but it's quicker to use PDFs because AgentKit has off-the-shelf PDF ingestion and retrieval.
Next, we need a directory to store the PDFs in, for which we can use `backend/app/app/tool_constants/pdf_data` (and we can delete the music-related default PDFs already there). We can also specify any other location
for the PDFs, as long as we correctly point the `PDF_TOOL_DATA_PATH` parameter in `.env` to it.

We now want to a CSV file of GitHub commit history into the PostgreSQL DB to use with the SQL tool. The tables include columns such as commit hash, commit date, commit user, and file changed. First, add this data to `tool_constants/`.

We'll go to `scripts/db_sql_tool/` and create a SQL script to load the data, calling it `load_commits.sql`.
```sql
-- Create table
CREATE TABLE COMMITS (
    commit_hash TEXT,
    commit_timestamp TIMESTAMP,
    commit_user TEXT,
    commit_message TEXT,
    file_changed TEXT
);

-- Copy CSV
COPY COMMITS (commit_hash, commit_timestamp, commit_user, commit_message, file_changed)
FROM '/docker-entrypoint-initdb.d/commit_history.csv'
WITH CSV HEADER;
```

Notice that the CSV path is referenced as `/docker-entrypoint-initdb.d/commit_history.csv`. This is because we need to map
local paths to paths within the Docker container running the `db_sql_tool` service. This includes the paths of the data and the SQL script to load it.

So, one additional step is to go to
`docker-compose.yml` (or whichever `docker-compose` file you're using) and add these mappings to the `db_sql_tool` service.
This is what it looks like:
```yaml
  db_sql_tool:
    image: postgres:11
    restart: always
    container_name: db_sql_tool
    volumes:
      - ./db_docker:/var/lib/postgresql
      - ./scripts/db_sql_tool/load_commits.sql:/docker-entrypoint-initdb.d/load_commits.sql
      - ./backend/app/app/tool_constants/public_demo_data/commit_history.csv:/docker-entrypoint-initdb.d/commit_history.csv
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=sqltool
    ports:
      - "5632:5432"
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres" ]
      interval: 10s
      timeout: 15s
      retries: 5
```


## Step 2: Configure tools

Recall that we want two functionalities: RAG over codebase documentation, and SQL query generation to search commit history. AgentKit provides off-the-shelf tools for both of these things.

For RAG, we want to use a combination of `pdf_tool` and `expert_tool`, where `pdf_tool` retrieves documents and `expert_tool` makes an LLM call to generate an answer. The goal, then, is to run them sequentially: `pdf_tool` first and then `expert_tool` after with access to the retrieved docs.
No change needs to be made to `pdf_tool`, we need to add a few lines of code to the `_arun` method of `expert_tool` and write some prompts.
```python
from app.schemas.tool_schema import ToolConfig

class ExpertTool(ExtendedBaseTool):

    # Other code omitted ...

     async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
            """Use the tool asynchronously."""
            try:
                tool_input = ToolInputSchema.parse_raw(query)
                user_question = tool_input.latest_human_message

                docs =  tool_input.intermediate_steps["PDF Tool"]

                messages = [
                    SystemMessage(content=self.system_context),
                    HumanMessage(content=self.prompt_message.format(question=user_question, retrieved_docs=docs))
                ]
                response = await self._agenerate_response(messages, discard_fast_llm=True, run_manager=run_manager)

                logger.info(f"Expert Tool response - {response}")

                return response

            except Exception as e:
                if run_manager is not None:
                    await run_manager.on_tool_error(e, tool=self.name)
                    return repr(e)
                else:
                    raise e
```
The code above parses the input provided to the `expert_tool` and fetches the docs retrieved by `pdf_tool`. It then formats these
docs into the prompt for the `expert_tool`, which needs to be set in `tools.yml`:

```yaml
expert_tool:
    default_llm: "gpt-4"
    default_fast_llm: "gpt-3.5-turbo-1106"
    description: >-
      Tool to answer the user question based on the documents retrieved by the pdf_tool. It analyzes the documents to provide reliable, helpful answers to specific technical queries related to the codebase, such as setup procedures or tool additions.
      {examples}
    prompt_message: |-
      Answer the user's question based on the documents retrieved.
      User question:
      <<<
      {{question}}
      >>>
      Retrieved documents:
      <<<
      {{retrieved_docs}}
      >>>
      Concise Answer:
    system_context: |-
      You are an expert in software engineering and communicating technical ideas. Your goal is to answer the user question solely based on the given documents.
    prompt_inputs:
      - name: examples
        content: |-
          Example Input: "What are the steps to set up the development environment?"
          Example Output: "You can set up your development environment locally or on Docker. To set up on Docker follow these steps: ..."
    max_token_length: 8000
```

To recap, here's what's happening: `pdf_tool` retrieves docs from codebase documentation, the `expert_tool` is tasked
with synthesizing an answer using these docs and an LLM call, and we write prompts for the `expert_tool` to which we add these docs.

Luckily, we don't need to change any code in `sql_tool` for data retrieval from the commit history. We do, however, need to add prompts to tell the tool the structure of our data:

```yaml
sql_tool:
    description: >-
      SQL tool to query structured table containing commit history of the Github repository of AgentKit, an LLM powered agent.
      Input is a question about the data in natural language, output is a string that contains an SQL query in markdown format, the number of rows the query returns and the first 3 rows.
      {examples}
    prompt_message: |-
      Given the database schema:
      ---
      {{table_schemas}}
      ---
      And the following notes about the tables:
      ---
      {table_notes}
      ---
      Please answer the following user questions with an SQL query:
      {{question}}
      ---
      Current conversation history:
      {{chat_history}}
    system_context: |-
      You are an expert on the GitHub repository of AgentKit, an LLM-powered agent. Your main task is to use
      SQL queries to retrieve information from structured tables containing commit history of the repository.
      During answering, the following principles MUST be followed:
      1. Set the language to the markdown code block for each code block. For example, \```sql SELECT * FROM public.Artist``` is SQL.
      2. Use the postgreSQL dialect, i.e. only functions that are supported
      3. DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
      4. In WHERE clauses use substring comparison to account for unknown string formulations (e.g. commit -> LIKE '%commit%')
      6. Make sure the final SQL query starts with '```sql' and ends with '```'
      7. Only use field and table names from the provided database schemas
      8. Ensure to include the schema name before the table, for example, \```sql SELECT * FROM public.COMMITS``` is correct but \```sql SELECT * FROM COMMITS``` is INCORRECT
      9. When asked to give time aggregated data (e.g. monthly), provide the time unit as an integer. For example, months should be 1-12, where you can the EXTRACT statement
      10. Always keep in mind that each `commit_hash` can correspond to multiple rows public.COMMITS; when counting commits, only count DISTINCT values of `commit_hash`
      11. When asked to summarize a user's contributions to the codebase, look at their 20 most recent commits.
    prompt_inputs:
      - name: examples
        content: |-
          Example Input: \"List all users who have made commits to the AgentKit repository"
          Example Output: \"`sql SELECT DISTINCT commit_user FROM public.COMMITS;`, total rows from SQL query: 8, first 3 rows: Ilyass El Mansouri, Gustaf Halvardsson, Casper Lindberg\"
      - name: table_definitions
        content: |-
          public.db_table | description
          public.COMMITS | Table with all commits made to the AgentKit repository; columns include commit user, commit message, commit timestamp, and file change. Each (commit, file changed) is a single row
      - name: table_notes
        content: |-
          Table name:
          public.COMMITS
          Table description:
          Table with all commits made to the AgentKit repository.
          Columns include commit user, commit message, commit timestamp, and file change.

    prompt_selection: |-
      Given the following tables:
      ---
      {table_definitions}
      ---
      Please reply only with a comma separated list of the db and the table names.
      Select the tables that can be most useful for answering to the question:
      {{question}}
    system_context_selection: |-
      You are a software engineering expert on the AgentKit codebase, an LLM-powered assistant. You have access to a
      PostgreSQL database which has tables consisting of the commit history of the AgentKit GitHub repository.

      Your task is to define which tables are useful to answer the question of the user.
      Please follow the instructions to answer the questions:
      1. Only reply with a comma separated list of db and table names. For example, "public.COMMITS"
      2. Only answer with valid table names from the list
      3. Always format the table names to include the database schema, for example "public.COMMITS", NOT "COMMITS"
      3. Reply with the least amount of tables necessary for the question
    prompt_validation: |-
      Given the following SQL query:
      {{query}}
      and the following results executing the query with a LIMIT 5:
      {{result}}
      Does the query answer the following question:
      {{question}}
      You must reply in the following format:
      Valid: [yes/no]
      Reason: [your reason for the validation]
    system_context_validation: |-
      You are a software engineering expert on the AgentKit codebase, an LLM-powered assistant. You have access to a
      PostgreSQL database which has tables consisting of data from the AgentKit GitHub repository, including commits,
      issues, and pull requests.
      You should validate that the constructed SQL query is answering the question of the user.
      You must reply in the following format:
      Valid: [yes/no]
      Reason: [your reason for the validation]
    prompt_refinement: |-
      Given the database schema:
      ---
      {{table_schemas}}
      ---
      Given your previous answer and the complaint from the user, please improve the SQL query to answer the question of the user.
      If the SQL query does not contain the database schema before a table, correct it. For example "SELECT * FROM COMMITS" should be corrected to "SELECT * FROM public.COMMITS".
      User question: {{question}}
      Previous answer: {{previous_answer}}
      Complaints: {{complaints}}
    nb_example_rows: 3
    validate_empty_results: False
    validate_with_llm: False
    always_limit_query: False
    max_rows_in_output: 30
```
The configs give the tool information about the commits table, allowing it to write an informed query.




## Step 3: Write action plans

The last step is to write action plans to use our tools. Recall that we want the Agent to be able to do two tasks:

1. Retrieve relevant docs from codebase documentation and use them to answer the user's question
2. Generate and execute a SQL query to retrieve data from the commit history

This suggests using two action plans in `agent.yml`:
```yaml
action_plans:
  '0':
    name: ''
    description: Use this plan to answer technical questions about AgentKit - related to setup, code, codebase navigation, or other technical questions.
    actions:
      - - pdf_tool
      - - expert_tool

  '1':
    name: ''
    description: |-
      Use this plan to fetch Github-related information from the repository of AgentKit, such as commits, issues, pull requests.
    actions:
      - - sql_tool
```

## Conclusion

In three simple steps, we have set up a high quality Agent which can provide informed guidance on a codebase. See the results below!

Fetching docs:
![Docs retrieval image](img/tutorial1.png)

Querying commits:
![Commits querying image](img/tutorial2.png)
