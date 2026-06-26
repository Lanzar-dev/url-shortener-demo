# URL Shortener — Agent Instructions

## Project Overview

Single-file FastAPI URL shortener with base62 encoding, SQLite storage, and a vanilla-JS frontend. All application logic lives in `main.py`. No packages, sub-modules, or new top-level files should be introduced.

## Stack

- Python 3.13+ · FastAPI · Pydantic v2 · SQLite (stdlib `sqlite3`) · Uvicorn
- Testing: pytest + `fastapi.testclient.TestClient` + `httpx`
- Dependency management: `uv` with `pyproject.toml` (no `requirements.txt`)

## Key Commands

```bash
uv sync                                  # install dependencies
uv run uvicorn main:app --reload         # dev server
uv run pytest                            # full test suite
uv run pytest tests/test_main.py::test_name -v  # single test
```

## Architecture

All code lives in `main.py`, structured in four sections (preserved in this order):

1. **Base62 encoder** — `encode(n)` / `decode(s)` pure functions; `decode` raises `ValueError` for invalid chars
2. **Database helpers** — `get_db()` returns a `sqlite3.Connection` (used as context manager); `init_db()` creates the `urls` table; `DB_PATH` is patched in tests via `monkeypatch`
3. **API endpoints** — `POST /shorten`, `GET /{code}` (redirect), `GET /lookup/{code:path}`; all registered **before** the static mount
4. **Static files** — `StaticFiles` mount is always **last**

Helper: `normalize_code(raw_code)` strips a full short URL down to just the code segment; use it in any route that accepts a code parameter.

## Coding Conventions

- `async def` route handlers; request bodies via dedicated `BaseModel` subclasses (e.g. `ShortenRequest`)
- `HTTPException` with a `detail` string on all error paths
- Raw SQL with `?` placeholders only — never interpolate user input
- `conn.row_factory = sqlite3.Row`; access columns by name
- Type hints on all signatures; lowercase generics (`list[str]`, `dict[str, int]`)
- Section separators: `#

## Imports

- Use named imports instead of default imports.
- Group imports: external libraries first, then internal modules, then relative paths.

---------------------------------------------------------------------------`

## Testing Conventions

- All tests in `tests/test_main.py`; fixture `client` is defined there and patches `main.DB_PATH` to a `tmp_path` DB
- Use `monkeypatch.setattr(main, "DB_PATH", ...)` — **not** `mock.patch`
- Naming: `test_<what>_<expected_outcome>`
- Every new endpoint or helper needs a corresponding test
- Pure-function tests (`encode`/`decode`) do not need the `client` fixture

## Security Rules

- Always wrap `decode()` calls in `try/except (ValueError, KeyError)` → raise `HTTPException(404)`
- Use `normalize_code` before decoding any user-supplied code
- Parameterised SQL only (`?` placeholders)

## Common Pitfalls

- **Static mount order**: API routes must be registered before `app.mount("/", StaticFiles(...))` or they'll be shadowed
- **DB_PATH patching**: tests rely on `monkeypatch.setattr(main, "DB_PATH", ...)` at module level; changing `get_db()` to accept a path parameter would break the test fixture
- **`decode` raises on bad input**: always catch both `ValueError` and `KeyError` when calling it from route handlers
