from fastapi import Header
from app.config import API_KEY
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != API_KEY:
        logger.warning("Rejected request: invalid or missing API key")
        raise HTTPException(status_code=401, detail="Invalid or missing API token")

