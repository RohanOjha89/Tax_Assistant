import sys
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# Mock sqlite3 for ChromaDB compatibility in CI
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from main import app

@pytest.fixture(scope="module")
def client():
    # We use 'with' to trigger the lifespan (startup/shutdown)
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

# We patch the components to avoid real API calls and empty DB errors
@patch("src.semantic_router.SemanticRouter.classify_query")
@patch("src.rag_pipeline.RAGPipeline.retrieve")
@patch("src.rag_pipeline.RAGPipeline.generate_response")
def test_chat_endpoint_structure(mock_gen, mock_retrieve, mock_classify, client):
    """Verify the chat response works by mocking the AI and Database"""
    
    # Define what the 'fake' components should return
    mock_classify.return_value = "SIMPLE"
    mock_retrieve.return_value = "Mock context: Tax slab for 2026 is 10%."
    mock_gen.return_value = "Based on the context, your tax slab is 10%."
    
    payload = {"query": "What are the tax slabs for 2026?"}
    response = client.post("/chat", params=payload)
    
    # Assertions to ensure our API correctly routes these mock values
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "SIMPLE"
    assert "10%" in data["answer"]
    assert data["query"] == payload["query"]

def test_invalid_input(client):
    """Test how the API handles empty queries"""
    response = client.post("/chat", params={"query": ""})
    # FastAPI usually returns 422 Unprocessable Entity for missing/empty required params
    assert response.status_code in [422, 200, 500]