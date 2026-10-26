from fastapi import APIRouter, HTTPException
import httpx
import logging
from app.schemas import WeatherResponse
logger = logging.getLogger(__name__)

router = APIRouter()
ERROR_FETCHING_WEATHER = "Error fetching weather data"
ERROR_FETCHING_FORECAST = "Error fetching forecast data"
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}

@router.get("/weather", response_model=WeatherResponse)
async def weather(city: str):
    async with httpx.AsyncClient() as client:
        try:
            geo_response = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1})
            geo_response.raise_for_status()
            
        except httpx.HTTPError:
            logger.exception("Error fetching weather data")
            raise HTTPException(status_code=502, detail=ERROR_FETCHING_WEATHER)
        
        geo_data = geo_response.json()
        if "results" not in geo_data or len(geo_data["results"]) == 0:
            raise HTTPException(status_code=404, detail="City not found")
        city_data = geo_data["results"][0]

        try:
            forecast_response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": city_data["latitude"],
                    "longitude": city_data["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,weather_code",
                }
            )
            forecast_response.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Error fetching forecast data")
            raise HTTPException(status_code=502, detail=ERROR_FETCHING_FORECAST)
        current = forecast_response.json()["current"]
        return {
            "city": city_data["name"],
            "temperature": current["temperature_2m"],
            "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
            "humidity": current["relative_humidity_2m"],
        }