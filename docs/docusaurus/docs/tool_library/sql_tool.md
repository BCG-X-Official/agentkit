# SQL tool

DISCLAIMER: Building Q&A systems of SQL databases requires executing model-generated SQL queries. There are inherent risks in doing this. Make sure that your database connection permissions are always scoped as narrowly as possible for your chain/agent's needs. This will mitigate though not eliminate the risks of building a model-driven system. For more on general security best practices, see [here](https://python.langchain.com/v0.1/docs/security/).

## How it works
The SQL tool currently consists of the following steps:
1) `_alist_sql_tables`: Find the tables relevant to the user's query and filter the database for only those tables
2) `_aquery_with_schemas`: Writes an SQL query with a prompt summarizing the schema of the selected tables and the user question
3) `_avalidate_response`: Validate the response from the executing the SQL query
    a) `_parse_query`: Parse the SQL query from the response and remove extra characters
    b) `run_no_str`: Execute SQL query against configured database, checks if results are returned
    c) LLM validates that the SQL query answers the question the user asked
4) `_aimprove_query`: If the SQL query does not answer the question sufficiently, prompt the LLM to improve it
5) Return the SQL query and the results

To add your own database, you can add your sql script in `scripts`, and modify the sql scripts in the docker-compose for `database` service to bootstrap with your data upon starting the docker.

The SQL tool only returns a limited number of rows of the output of the generated SQL query to the next tool (defined by `nb_example_rows`), to limit the number of tokens used. Take note of this in case there are prompts in downstream tools that interpret the data. To have good results make sure enough of the data is added to the prompt, or change the `sql_tool` to return a more concise result.

While the tool output only contains `nb_example_rows` rows, the SQL tool table appendix in the UI displays the full outputs of the SQL query by executing it dynamically.

## Prompt engineering tips

- Always include examples for important steps that are tailored to your database
- Where you observe frequent errors (in any of the steps), add specific examples of how it should be done correctly, e.g. "In WHERE clauses use substring comparison to account for unknown string formulations (e.g. inhibitor -> LIKE '%inhibitor%')"

`system_context`:
- Mention the role of the LLM: "You are an expert in ... database, your goal is to ..."
- Specify the required output format, e.g. markdown code block
- Specify the SQL dialect (e.g. PostgreSQL, Snowflake)
- For safety, instruct it to not use any DML statements
- Instruct it to only use field and table names from the provided database schemas (to reduce hallucinations)


`prompt_inputs`:
- Always use 'few-shot learning': give an example of a typical user query and a correct SQL query
- In `table_definitions`, give a description of each table and describe what information is exactly in this table. This will give better results in the table selection step
