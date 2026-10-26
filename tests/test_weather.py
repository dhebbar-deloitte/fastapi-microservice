import httpx
from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import FakeResponse

client = TestClient(app)

def test_weather_success(monkeypatch):
    async def mock_get(self, url, **kwargs):
        if "geocoding" in url:
            return FakeResponse({"results": [{"name": "London", "latitude": 51.5, "longitude": -0.12}]})
        return FakeResponse({"current": {"temperature_2m": 15.2, "relative_humidity_2m": 70, "weather_code": 3}})
    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/weather", params={"city": "London"})
    assert response.status_code == 200
    assert response.json() == {
        "city": "London",
        "temperature": 15.2,
        "condition": "Overcast",
        "humidity": 70,
    }

def test_weather_city_not_found(monkeypatch):
    async def mock_get(self, url, **kwargs):
        if "geocoding" in url:
            return FakeResponse({"results": []})
        return FakeResponse({"current": {"temperature_2m": 15.2, "relative_humidity_2m": 70, "weather_code": 3}})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/weather", params={"city": "Unknown City"})
    assert response.status_code == 404
    assert response.json() == {"detail": "City not found"}

def test_weather_geocoding_failure(monkeypatch):
    async def mock_get(self, url, **kwargs):
        if "geocoding" in url:
            raise httpx.ConnectError("boom")
        return FakeResponse({"current": {"temperature_2m": 15.2, "relative_humidity_2m": 70, "weather_code": 3}})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/weather", params={"city": "London"})
    assert response.status_code == 502

def test_weather_forecast_failure(monkeypatch):
    async def mock_get(self, url, **kwargs):
        if "geocoding" in url:
            return FakeResponse({"results": [{"name": "London", "latitude": 51.5, "longitude": -0.12}]})
        raise httpx.ConnectError("boom")

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/weather", params={"city": "London"})
    assert response.status_code == 502

def test_weather_unknown_code(monkeypatch):
    async def mock_get(self, url, **kwargs):
        if "geocoding" in url:
            return FakeResponse({"results": [{"name": "London", "latitude": 51.5, "longitude": -0.12}]})
        return FakeResponse({"current": {"temperature_2m": 15.2, "relative_humidity_2m": 70, "weather_code": 999}})

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)
    response = client.get("/weather", params={"city": "London"})
    assert response.status_code == 200
    assert response.json() == {
        "city": "London",
        "temperature": 15.2,
        "condition": "Unknown",
        "humidity": 70,
    }
    
def test_weather_missing_city():
    response = client.get("/weather")
    assert response.status_code == 422