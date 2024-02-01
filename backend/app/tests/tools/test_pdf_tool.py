# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain.base_language import BaseLanguageModel
from langchain.schema import Document

from app.schemas.agent_schema import AgentConfig
from app.services.chat_agent.tools.library.pdf_tool.pdf_tool import PDFTool
from tests.fake.pdf_pipeline import FakePDFExtractionPipeline
from tests.fake.vector_db import FakeVectorDB


@pytest.fixture(autouse=True)
def mock_llm_call(llm: BaseLanguageModel):  # pylint: disable=redefined-outer-name
    with patch("app.services.chat_agent.tools.library.pdf_tool.pdf_tool.get_llm", return_value=llm):
        yield


@pytest.fixture
def pdf_pipeline():
    db = FakeVectorDB.from_documents(docs=[Document(page_content="This is a test document.")])
    pdf_pipeline = FakePDFExtractionPipeline(vector_db=db)
    return pdf_pipeline


@pytest.fixture(autouse=True)
def fake_get_pdf_pipeline(pdf_pipeline: FakePDFExtractionPipeline):  # pylint: disable=redefined-outer-name
    with patch("app.services.chat_agent.tools.library.pdf_tool.pdf_tool.get_pdf_pipeline", return_value=pdf_pipeline):
        yield


@pytest.fixture()
def pdf_tool(agent_config: AgentConfig) -> PDFTool:
    pdf_tool = PDFTool.from_config(
        config=agent_config.tools_library.library["pdf_tool"],
        common_config=agent_config.common,
    )

    return pdf_tool


@pytest.mark.skip(reason="This test will require changing the source code.")
@pytest.mark.asyncio
async def test_doc_retrieval(pdf_tool: PDFTool):
    # Assuming hypothetical `_aretrieve_docs()` method which only fetches docs.
    docs = await pdf_tool._aretrieve_docs(query="This is a test query.")
    assert docs == "This is a test document."


@pytest.mark.asyncio
async def test_qa_with_docs(pdf_tool: PDFTool):
    response = await pdf_tool._aqa_pdf_chunks(query="This is a test query.", docs="This is a test document.")
    assert response == "0"


@pytest.mark.asyncio
async def test_qa_without_docs(pdf_tool: PDFTool):
    response = await pdf_tool._aqa_pdf_chunks(query="This is a test query.", docs=None)
    assert response == "0"


@pytest.mark.asyncio
async def test_pdf_tool_run(pdf_tool: PDFTool, tool_input: str):
    response = await pdf_tool._arun(tool_input)
    assert response == "0"
