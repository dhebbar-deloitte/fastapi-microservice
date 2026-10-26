from pydantic import BaseModel

class JokeResponse(BaseModel):
    joke: str
    category: str

class WeatherResponse(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int

class SummaryRequest(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str