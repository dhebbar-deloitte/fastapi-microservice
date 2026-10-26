from fastapi import FastAPI
from app.routes.weather import router as weather_router
from app.routes.jokes import router as jokes_router
from app.routes.summary import router as summary_router
import logging

app = FastAPI(title="WeatherMicroservice")
app.include_router(weather_router)
app.include_router(jokes_router)
app.include_router(summary_router)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)



@app.get("/health")
def health_check():
    return {"status": "healthy"}

