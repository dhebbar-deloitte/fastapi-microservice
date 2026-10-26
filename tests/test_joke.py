import httpx
from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import FakeResponse

client = TestClient(app)

def test_joke_success(monkeypatch):
    async def mock_get(self, url, **kwargs):
        return FakeResponse({"joke": "Why did the chicken...", "category": "Misc"})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/joke")
    assert response.status_code == 200
    assert response.json() == {"joke": "Why did the chicken...", "category": "Misc"}

def test_joke_upstream_failure(monkeypatch):
    async def mock_get(self, url, **kwargs):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/joke")
    assert response.status_code == 502
    

def test_joke_missing_joke_key(monkeypatch):
    async def mock_get(self, url, **kwargs):
        return FakeResponse({"category": "Misc"})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/joke")
    assert response.status_code == 502
    