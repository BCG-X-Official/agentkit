# -*- coding: utf-8 -*-
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_root(test_client: TestClient):
    response = test_client.get("/")
    assert response is not None
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI backend"}
