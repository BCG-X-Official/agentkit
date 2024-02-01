# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.api.deps import get_jwt
from app.api.v1.endpoints.chat import get_meta_agent_with_api_key
from app.deps.agent_deps import set_global_tool_context
from app.main import app
from app.schemas.agent_schema import AgentConfig
from app.schemas.tool_schema import ToolInputSchema
from app.services.chat_agent.meta_agent import create_meta_agent
from app.utils import uuid7
from app.utils.config_loader import get_agent_config
from app.utils.fastapi_globals import g
from tests.fake.chat_model import FakeMessagesListChatModel


def pytest_configure():
    run_id = str(uuid7())
    g.tool_context = {}
    g.query_context = {
        "run_id": run_id,
    }


@pytest.fixture(autouse=True)
def mock_redis_client_sync():
    with patch(
        "app.services.chat_agent.helpers.run_helper.get_redis_client", new_callable=AsyncMock
    ) as mock_helpers_redis_client:
        mock_helpers_redis_client.get.return_value = "mocked_redis_get_value"
        mock_helpers_redis_client.set.return_value = True

        yield


@pytest.fixture
def messages() -> list:
    return [
        SystemMessage(content="You are a test user."),
        HumanMessage(content="Hello, I am a test user."),
    ]


@pytest.fixture
def llm() -> BaseLanguageModel:
    fake_llm = FakeMessagesListChatModel(responses=[HumanMessage(content=f"{i}") for i in range(100)])
    return fake_llm


@pytest.fixture(autouse=True)
def mock_llm_call(llm: BaseLanguageModel):  # pylint: disable=redefined-outer-name
    with patch("app.services.chat_agent.tools.library.basellm_tool.basellm_tool.get_llm", return_value=llm):
        yield


@pytest.fixture
def tool_input() -> str:
    return ToolInputSchema(
        chat_history=[
            HumanMessage(content="This is a test memory"),
            AIMessage(content="This is the AI message response"),
        ],
        latest_human_message="This is a test message. ",
        intermediate_steps={},
    ).json()


@pytest.fixture
def agent_config() -> AgentConfig:
    return get_agent_config()


@pytest.fixture
def meta_agent(llm: BaseLanguageModel) -> AgentExecutor:  # pylint: disable=redefined-outer-name
    agent_config = get_agent_config()
    return create_meta_agent(
        agent_config=agent_config, get_llm_hook=lambda type, key: llm  # pylint: disable=unused-argument
    )


@pytest.fixture
def test_client(meta_agent: AgentExecutor) -> TestClient:  # pylint: disable=redefined-outer-name
    FastAPICache.init(None, enable=False)

    app.dependency_overrides[set_global_tool_context] = lambda: None
    app.dependency_overrides[get_jwt] = lambda: {}
    app.dependency_overrides[get_meta_agent_with_api_key] = lambda: meta_agent

    return TestClient(app)


@pytest.fixture
def run_manager() -> AsyncCallbackManagerForToolRun:
    return MagicMock(spec=AsyncCallbackManagerForToolRun)
