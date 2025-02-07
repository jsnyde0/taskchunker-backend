from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_hello_endpoint():
    """Test the hello endpoint returns the expected response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, TaskChunker!"}


@pytest.mark.asyncio
@pytest.mark.llm
async def test_chat_endpoint():
    """Test the chat endpoint with a mocked LLM response."""
    with patch("src.main.get_llm_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Test response"

        response = client.post("/api/v1/chat", json={"message": "Test message"})
        print(f"Actual response: {response.json()}")  # Debug print
        assert response.status_code == 200
        assert mock_llm.called  # Verify our mock was actually called
        assert response.json() == {"response": "Test response"}


@pytest.mark.asyncio
@pytest.mark.llm
async def test_chat_endpoint_content():
    """Test that the chat endpoint returns expected content."""
    with patch("src.main.get_llm_response", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Brussels is the capital of Belgium"

        response = client.post(
            "/api/v1/chat", json={"message": "What is the capital of Belgium?"}
        )
        assert response.status_code == 200
        assert mock_llm.called  # Verify our mock was actually called
        assert "Brussels" in response.json()["response"]
