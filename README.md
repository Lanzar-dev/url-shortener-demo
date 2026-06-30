# URL Shortener Demo

A simple URL shortener built with FastAPI, SQLite, and a vanilla HTML/CSS/JS frontend, with a single-file Python backend.

## Features

- Shorten long URLs into Base62 short codes
- Redirect short code URLs to original URLs
- Lookup original URL from either:
  - a short code
  - a full short URL
- Base62 output table in the UI:
  - Original URL on the left
  - Base62 code on the right
- Persistent table history via browser localStorage
- One-click Clear History button
- Light/Dark theme toggle with preference persistence

## Tech Stack

- Python 3.13+
- FastAPI
- SQLite (`sqlite3` from stdlib)
- Uvicorn
- Pytest + TestClient + httpx
- Dependency manager: `uv`
- Code formatter: `ruff`

## Project Layout

- `main.py`: API app, DB helpers, Base62 helpers
- `static/index.html`: frontend UI and client logic
- `tests/test_main.py`: test suite
- `pyproject.toml`: dependencies and project metadata
- `.github/hooks/format-prettier.sh`: post-tool ruff formatter hook script
- `.github/hooks/post-tool-prettier.json`: agent hook configuration

## Installation

```bash
uv sync
```

## Run the App

```bash
uv run uvicorn main:app --reload
```

Open: `http://127.0.0.1:8000`

## Run Tests

```bash
uv run pytest
```

Run a single test:

```bash
uv run pytest tests/test_main.py::test_shorten_returns_short_code_and_url -v
```

## Code Formatting

[`ruff`](https://docs.astral.sh/ruff/) is used to format Python files. It is installed as a dev dependency and runs automatically via a post-tool agent hook after every file edit.

To format manually:

```bash
uv run ruff format .
```

## API Reference

### `POST /shorten`

Create a short URL.

Request body:

```json
{
  "url": "https://example.com/page"
}
```

Response:

```json
{
  "short_code": "1",
  "short_url": "http://127.0.0.1:8000/1"
}
```

### `GET /{code}`

Redirect to original URL.

- Success: `307 Temporary Redirect`
- Not found/invalid code: `404` with detail `"Short URL not found"`

### `GET /lookup/{code:path}`

Lookup original URL for a short code or short URL input.

Response:

```json
{
  "url": "https://example.com/page"
}
```

Not found/invalid code response:

```json
{
  "detail": "Short URL not found"
}
```

## Frontend Usage

1. Enter a URL and submit to shorten.
2. Use Lookup with either:
   - short code (for example `1`)
   - full short URL (for example `http://127.0.0.1:8000/1`)
3. Review outputs in the table:
   - `Original URL`
   - `Base62 Code`
4. Refresh the page to confirm history persistence.
5. Click `Clear History` to reset stored table data.
