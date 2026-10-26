from fastapi.testclient import TestClient
import httpx
from app.config import MAX_TEXT_LENGTH, API_KEY
from app.main import app

client = TestClient(app)
AUTH_HEADERS = {"x-api-key": API_KEY}


def test_uses_test_config():
    assert API_KEY == "test-key"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_summary_no_api_key():
    response = client.post("/summary", json={"text": "hello"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API token"}

def test_summary_wrong_api_key():
    response = client.post("/summary", json={"text": "hello"}, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API token"}

def test_summary_empty_text():
    response = client.post("/summary", json={"text": ""}, headers=AUTH_HEADERS)
    assert response.status_code == 400
    assert response.json() == {"detail": "Text is empty"}

def test_summary_whitespace_text():
    response = client.post("/summary", json={"text": " "}, headers=AUTH_HEADERS)
    assert response.status_code == 400
    assert response.json() == {"detail": "Text is empty"}

def test_summary_text_too_long():
    response = client.post("/summary", json={"text": "a" * (MAX_TEXT_LENGTH + 1)}, headers=AUTH_HEADERS)
    assert response.status_code == 400
    assert response.json() == {"detail": f"Text length exceeds maximum of {MAX_TEXT_LENGTH} characters"}

def test_summary_missing_text_field():
    response = client.post("/summary", json={}, headers=AUTH_HEADERS)
    assert response.status_code == 422

def test_summary_success(monkeypatch):
    async def mock_post(self, url, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
            def json(self):
                return {"content": [{"type": "text", "text": "A short summary."}]}
            def raise_for_status(self):
                pass
        return MockResponse()
            
    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post("/summary", json={"text": "hello"}, headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json() == {"summary": "A short summary."}

def test_summary_llm_network_failure(monkeypatch):
    async def mock_post(self, url, **kwargs):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)
    response = client.post("/summary", json={"text": "hello"}, headers=AUTH_HEADERS)
    assert response.status_code == 502