# PDF tool
## How it works

The standard PDF tool uses PGVector for indexing (https://github.com/pgvector/pgvector) and saves the embeddings in PostgresQL. However, any preferred index can be used easily if it is supported by Langchain. We use 'PyMuPDF' as the standard PDF parser, but any of the options in `LOADER_DICT` can be used.

Note: This tool can easily be extended other documents as well, e.g. PPT, Word, by adding specific parsers for those document types.

The general process is

1) Create an index and fill with embedded documents (on app startup, or can be persisted), see `vector_db_pdf_ingestion.py`. Some choices can be made:
 - The index as mentioned (PGVector in this template)
 - Embedding model (OpenAI in this template)
 - How the documents are split into chunks (TokenTextSplitter with chunk size 2000 and overlap 200 tokens in this template)

2) When the PDF tool is run, the k most relevant document chunks are returned (4 in this template)

3) These document chunks are entered in a LLM prompt along with the user question and the result is returned to the user
