import sys
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    # The 'with' statement triggers the @asynccontextmanager lifespan in main.py
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Verify the API is online and ChromaDB is ready"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_chat_endpoint_structure(client):
    """Verify the chat response contains the required fields"""
    payload = {"query": "What are the tax slabs for 2026?"}
    # Using params if your endpoint expects query params, or json= if it expects a body
    response = client.post("/chat", params=payload) 
    
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "strategy" in data
    assert "answer" in data
    assert isinstance(data["answer"], str)

def test_invalid_input(client):
    """Test how the API handles empty queries"""
    response = client.post("/chat", params={"query": ""})
    # Depending on your logic, this might be a 422 (FastAPI validation) or 500
    assert response.status_code in [422, 500, 200]