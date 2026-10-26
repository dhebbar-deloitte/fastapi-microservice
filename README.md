 # Weather, Joke, and Summary API

A FastAPI service that provides weather information, jokes, and concise text summaries powered by Anthropic Claude.

## Endpoints

| Method | Path | Auth required | Description and status codes |
|---|---|---|---|
| GET | `/weather` | No | Returns weather for a city. `200` success, `404` city not found, `502` upstream provider error, `422` city parameter missing. |
| GET | `/joke` | No | Returns a joke. `200` success, `502` upstream provider error. |
| POST | `/summary` | Yes (`X-API-Key`) | Summarizes submitted text. `200` success, `400` text is empty, whitespace-only, or over 5,000 characters, `401` missing or invalid API key, `422` text field missing, `502` Anthropic error. |
| GET | `/health` | No | Health check; returns `200` when the service is running. |

## LLM decisions

- **Provider:** Anthropic (Claude).
- **Model:** `claude-haiku-5-5` is the `ANTHROPIC_MODEL` default. Small and cheap, and plenty for 2 to 3 sentence summaries
- **Summary style:** Summarize the supplied text accurately in two or three sentences. Return only the summary, without an introduction or additional commentary.
- **Maximum input length:** 5,000 characters, to keep cost and latency manageable.
- **`max_tokens`:** 300.

## Setup

1. Clone the repository and enter its directory:

	```sh
	git clone <repository-url>
	cd <repository-directory>
	```

2. Create and activate a virtual environment:

	```sh
	python -m venv venv
	source venv/bin/activate
	```

	On Windows PowerShell, use `venv\Scripts\Activate.ps1` to activate it.

3. Install dependencies:

	```sh
	pip install -r requirements.txt
	```

4. Copy `.env.example` to `.env` and fill in the values:

	```sh
	cp .env.example .env
	```

	- `API_KEY` is the key callers send in the `X-API-Key` header when requesting `/summary`.
	- `ANTHROPIC_API_KEY` is the credential the service sends to Anthropic.
	- `ANTHROPIC_MODEL` optionally overrides the default Claude model.

## Run

Start the server:

```sh
uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000/docs> for interactive API documentation.

## Tests

```sh
python -m pytest
```

All external calls (Anthropic, weather provider, joke provider) are mocked, so the tests need no network access and no real API keys.

## Project structure

```
assignment-1/
├── app/
│   ├── config.py       # Environment variable loading and settings
│   ├── schemas.py      # Pydantic request/response models
│   ├── auth.py         # X-API-Key dependency for protected routes
│   ├── main.py         # FastAPI app creation and router registration
│   └── routes/
│       ├── weather.py  # GET /weather — fetches weather from upstream
│       ├── jokes.py    # GET /joke — fetches a random joke from upstream
│       └── summary.py  # POST /summary — summarizes text via Claude
├── tests/
│   ├── conftest.py     # Sets fake environment variables so tests never need real keys
│   ├── helpers.py      # Reusable test utilities
│   ├── test_weather.py # Tests for /weather
│   ├── test_joke.py    # Tests for /joke
│   └── test_summary.py # Tests for /summary
├── .env.example        # Template listing required environment variables
├── .gitignore          # Excludes .env, venv, __pycache__, and similar
└── requirements.txt    # Python dependencies
```

## Design notes

- Missing secrets stop the app at startup, so auth can't silently turn off.
- Upstream failures become 502, with details logged but never shown to the caller.
- User text and API keys are never logged.
- External calls are mocked in tests.

## Example requests

```sh
curl 'http://127.0.0.1:8000/weather?city=London'
```

```sh
curl 'http://127.0.0.1:8000/joke'
```

Replace `YOUR_API_KEY` with the value of `API_KEY` from `.env`:

```sh
curl -X POST 'http://127.0.0.1:8000/summary' \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: YOUR_API_KEY' \
  -d '{"text":"Paste the text to summarize here."}'
```

```sh
curl 'http://127.0.0.1:8000/health'
```
