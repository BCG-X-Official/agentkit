# -*- coding: utf-8 -*-
import json
import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.schemas.message_schema import IChatMessage, IChatQuery, ICreatorRole
from app.schemas.streaming_schema import StreamingData, StreamingDataTypeEnum, StreamingSignalsEnum
from app.utils import uuid7


@pytest.fixture
def chat_query() -> dict[str, Any]:
    return {
        "messages": [
            {
                "role": "user",
                "content": "Hello, I am a test user.",
            }
        ],
        "api_key": None,
        "conversation_id": str(uuid7()),
        "new_message_id": str(uuid7()),
        "user_email": "",
        "settings": None,
    }


@pytest.mark.asyncio
async def test_chat(test_client: TestClient, chat_query: dict[str, Any]):  # pylint: disable=redefined-outer-name
    response = test_client.post("api/v1/chat/agent", json=chat_query)
    assert response is not None
    assert response.status_code == 200

    start_time = time.time()
    timeout = 10  # Timeout in seconds

    received_end = False
    response_data = []
    while not received_end:
        # Read the streaming response
        for line in response.iter_lines():
            if line:
                response_data.append(line)

        # Perform assertions on the response data
        assert len(response_data) > 0
        assert json.loads(response_data[0])["data_type"] == StreamingDataTypeEnum.SIGNAL.value
        assert json.loads(response_data[0])["data"] == StreamingSignalsEnum.START.value
        assert "run_id" in json.loads(response_data[0])["metadata"]

        if len(response_data) > 1:
            assert json.loads(response_data[1])["data_type"] == StreamingDataTypeEnum.ACTION.value
            assert json.loads(response_data[1])["data"] == "clarify_tool"
            assert "run_id" in json.loads(response_data[1])["metadata"]

        if len(response_data) > 2:
            assert json.loads(response_data[2])["data_type"] == StreamingDataTypeEnum.SIGNAL.value
            assert json.loads(response_data[2])["data"] == StreamingSignalsEnum.LLM_END.value
            assert "run_id" in json.loads(response_data[2])["metadata"]

        if len(response_data) > 3:
            assert json.loads(response_data[3])["data_type"] == StreamingDataTypeEnum.SIGNAL.value
            assert json.loads(response_data[3])["data"] == StreamingSignalsEnum.TOOL_END.value
            assert "run_id" in json.loads(response_data[3])["metadata"]

        if len(response_data) > 4:
            assert json.loads(response_data[4])["data_type"] == StreamingDataTypeEnum.SIGNAL.value
            assert json.loads(response_data[4])["data"] == StreamingSignalsEnum.END.value
            assert "run_id" in json.loads(response_data[4])["metadata"]

        if time.time() - start_time > timeout:
            assert False, f"Timeout reached after {len(response_data)} messages."

        # Check if the end of the stream has been reached
        last_line = json.loads(response_data[len(response_data) - 1])["data"]
        if last_line == StreamingSignalsEnum.END.value:
            received_end = True

        time.sleep(0.1)  # Wait a bit before reading the next line

    assert len(response_data) == 5
