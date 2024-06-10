# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain.base_language import BaseLanguageModel

from app.schemas.agent_schema import AgentConfig
from app.services.chat_agent.tools.library.sql_tool.sql_tool import SQLTool
from tests.fake.sql_db import FakeDBInfo, FakeSQLDatabase, FakeTable


@pytest.fixture(autouse=True)
def mock_llm_call(llm: BaseLanguageModel):  # pylint: disable=redefined-outer-name
    with patch("app.services.chat_agent.tools.library.sql_tool.sql_tool.get_llm", return_value=llm):
        yield


@pytest.fixture(autouse=True)
def patch_check_init():  # pylint: disable=redefined-outer-name
    def dummy(*args, **kwargs):
        pass

    with patch("app.services.chat_agent.tools.library.sql_tool.sql_tool.SQLTool.check_init", new=dummy):
        yield


@pytest.fixture(autouse=True)
def sql_tool_db():
    db_info = FakeDBInfo(tables=[FakeTable(name="fake_table", structure="test_structure")])
    fake_db = FakeSQLDatabase(db_info=db_info)
    with patch("app.services.chat_agent.tools.library.sql_tool.sql_tool.sql_tool_db", new=fake_db):
        yield


@pytest.fixture
def sql_tool(agent_config: AgentConfig) -> SQLTool:
    return SQLTool.from_config(
        config=agent_config.tools_library.library["sql_tool"],
        common_config=agent_config.common,
    )


@pytest.mark.asyncio
async def test_list_tables(sql_tool: SQLTool):
    response = await sql_tool._alist_sql_tables(query="This is a test query.")
    assert response == ["0"]


@pytest.mark.asyncio
async def test_sql_query_generation(sql_tool: SQLTool):
    table_schemas, response = await sql_tool._aquery_with_schemas(
        query="This is a test query.", filtered_tables=["fake_table"]
    )
    assert table_schemas == "DB.TABLE name: fake_table, Table structure: test_structure"
    assert response == "0"


@pytest.mark.asyncio
async def test_sql_query_generation_no_tables(sql_tool: SQLTool):
    table_schemas, response = await sql_tool._aquery_with_schemas(query="This is a test query.", filtered_tables=[])
    assert table_schemas == ""
    assert response == "0"


@pytest.mark.asyncio
async def test_sql_tool_run(sql_tool: SQLTool, tool_input: str):
    with (
        patch(
            "app.services.chat_agent.tools.library.sql_tool.sql_tool.SQLTool._alist_sql_tables",
            return_value=["fake_table"],
        ),
        patch("app.services.chat_agent.tools.library.sql_tool.sql_tool.SQLTool._parse_query", return_value="query"),
        patch("app.services.chat_agent.tools.library.sql_tool.sql_tool.is_sql_query_safe", return_value=True),
    ):
        response = await sql_tool._arun(tool_input)
    assert response == "0"
