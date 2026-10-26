import httpx
import logging
from fastapi import HTTPException, APIRouter
from app.schemas import JokeResponse

router = APIRouter()
logger = logging.getLogger(__name__)
ERROR_FETCHING_JOKE = "Error fetching joke"

@router.get("/joke", response_model=JokeResponse)
async def joke():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://v2.jokeapi.dev/joke/Any?type=single")
            response.raise_for_status()
        except httpx.HTTPError:
            logger.exception(ERROR_FETCHING_JOKE)
            raise HTTPException(status_code=502, detail=ERROR_FETCHING_JOKE)
        
        
        data = response.json()
        if "joke" not in data:
            logger.error("Joke API returned unexpected response: %s", response.text)
            raise HTTPException(status_code=502, detail=ERROR_FETCHING_JOKE)
        return {"joke": data["joke"], "category": data["category"]}