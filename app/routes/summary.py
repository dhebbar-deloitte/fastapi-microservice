from fastapi import HTTPException, Depends, APIRouter
from app.schemas import SummaryRequest, SummaryResponse
from app.auth import verify_api_key
from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, MAX_TEXT_LENGTH

import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


SUMMARY_SYSTEM_PROMPT = (
    "Summarize the user's text in 2 to 3 sentences. "
    "Reply with only the summary."
)

async def generate_summary(text: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": ANTHROPIC_MODEL,
                    "system": SUMMARY_SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": text}],
                    "max_tokens": 300,
                }
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            if isinstance(exc, httpx.HTTPStatusError):
                logger.exception("LLM rejected request")
            else:
                logger.exception("LLM request failed")
            raise HTTPException(status_code=502, detail="LLM request failed")
        data = response.json()
        if not data.get("content"):
            logger.error("LLM returned no content (status %s)", response.status_code)
            raise HTTPException(status_code=502, detail="LLM returned an unexpected response")
        return data["content"][0]["text"].strip()

@router.post("/summary", response_model=SummaryResponse, dependencies=[Depends(verify_api_key)])
async def summary(request: SummaryRequest):
    if request.text.strip() == "":
        raise HTTPException(status_code=400, detail="Text is empty")
    if len(request.text) > MAX_TEXT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Text length exceeds maximum of {MAX_TEXT_LENGTH} characters")
    summary_text = await generate_summary(request.text)
    return {"summary": summary_text}