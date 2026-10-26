from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL") or "claude-haiku-5-5"

if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")

MAX_TEXT_LENGTH = 5000