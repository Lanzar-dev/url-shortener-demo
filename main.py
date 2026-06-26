import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import unquote, urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Base62 encoder
# ---------------------------------------------------------------------------

BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(n: int) -> str:
    """Encode a positive integer as a base62 string."""
    if n == 0:
        return BASE62[0]
    chars: list[str] = []
    while n:
        chars.append(BASE62[n % 62])
        n //= 62
    return "".join(reversed(chars))


def decode(s: str) -> int:
    """Decode a base62 string back to an integer."""
    n = 0
    for ch in s:
        n = n * 62 + BASE62.index(ch)
    return n


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

DB_PATH = Path("urls.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                original TEXT NOT NULL
            )
            """
        )
        conn.commit()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)


# ---------------------------------------------------------------------------
# API endpoints  (must be registered BEFORE StaticFiles mount)
# ---------------------------------------------------------------------------


class ShortenRequest(BaseModel):
    url: str


def normalize_code(raw_code: str) -> str:
    """Accept either a short code or full short URL and return just the code."""
    code = unquote(raw_code.strip())

    parsed = urlparse(code)
    if parsed.scheme and parsed.netloc:
        code = parsed.path.rsplit("/", 1)[-1]
    elif "/" in code:
        code = code.rsplit("/", 1)[-1]

    code = code.strip()
    if not code:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return code


def get_original_url_by_code(code: str) -> str:
    """Resolve a short code to its original URL or raise 404."""
    normalized_code = normalize_code(code)

    try:
        row_id = decode(normalized_code)
    except (ValueError, KeyError):
        raise HTTPException(status_code=404, detail="Short URL not found")

    with get_db() as conn:
        row = conn.execute(
            "SELECT original FROM urls WHERE id = ?", (row_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return row["original"]


@app.post("/shorten")
async def shorten(body: ShortenRequest, request: Request):
    """Insert the original URL and return a base62 short code."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO urls (original) VALUES (?)", (body.url,)
        )
        conn.commit()
        row_id: int = cursor.lastrowid  # type: ignore[assignment]

    code = encode(row_id)
    base = str(request.base_url).rstrip("/")
    return {"short_code": code, "short_url": f"{base}/{code}"}


@app.get("/{code}")
async def redirect(code: str):
    """Decode the short code and redirect to the original URL."""
    original_url = get_original_url_by_code(code)
    return RedirectResponse(url=original_url, status_code=307)


@app.get("/lookup/{code:path}")
async def lookup(code: str):
    """Return the original URL as JSON for a short code."""
    original_url = get_original_url_by_code(code)
    return {"url": original_url}


# ---------------------------------------------------------------------------
# Static files  (mounted last so API routes take priority)
# ---------------------------------------------------------------------------

app.mount("/", StaticFiles(directory="static", html=True), name="static")
