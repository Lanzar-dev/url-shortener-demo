---
description: "Use when writing, editing, or reviewing any code in this project. Covers language, framework conventions, project structure, and how to run and test the app."
applyTo: "**"
---

# URL Shortener — Project Instructions

## Stack

- **Language**: Python 3.13+
- **Web framework**: FastAPI (async handlers, Pydantic v2 request bodies)
- **Database**: SQLite via the stdlib `sqlite3` module — no ORM
- **Server**: Uvicorn (ASGI)
- **Testing**: pytest + `fastapi.testclient.TestClient` + `httpx`
- **Dependency management**: `uv` with `pyproject.toml` (no `requirements.txt`)

## Project Layout

```
main.py            # entire application: DB helpers, encoders, FastAPI app + routes
pyproject.toml     # project metadata and dependencies
static/
  index.html       # single-page frontend — vanilla HTML/CSS/JS, no framework
tests/
  conftest.py      # adds project root to sys.path
  test_main.py     # all tests live here
```

Keep the flat layout. Do **not** introduce packages, sub-modules, or new top-level files unless explicitly asked.

## Running the Project

```bash
# Install dependencies (uses uv)
uv sync

# Start the dev server (reloads on file change)
uv run uvicorn main:app --reload

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_main.py::test_shorten_returns_short_code_and_url -v
```

## Coding Conventions

### Python style

- Follow PEP 8; use type hints on all function signatures.
- Use `list[str]`, `dict[str, int]` (lowercase generics, Python 3.10+ style) — not `List`, `Dict`.
- Prefer `Path` from `pathlib` over raw string paths.
- Section separators use the existing comment style:
  ```python
  # ---------------------------------------------------------------------------
  # Section name
  # ---------------------------------------------------------------------------
  ```

### FastAPI patterns

- Route handlers are `async def`.
- Request bodies use a dedicated `BaseModel` subclass (e.g., `ShortenRequest`).
- Raise `HTTPException` with an appropriate status code and a `detail` string on errors.
- Register all API routes **before** mounting `StaticFiles`; the static mount is always last.

### Database

- Use the `get_db()` helper to obtain a connection; always use it as a context manager (`with get_db() as conn`).
- Raw SQL only — no SQLAlchemy, no ORMs.
- `conn.row_factory = sqlite3.Row` is set in `get_db()`; access columns by name.

### Base62 encoding

- `encode(n: int) -> str` and `decode(s: str) -> int` are pure functions in `main.py`.
- `decode` must raise `ValueError` for characters not in `BASE62`.

### Frontend (`static/index.html`)

- Vanilla HTML/CSS/JS — no build step, no framework, no external CDN dependencies.
- CSS custom properties (`--var`) are used for theming; light/dark modes via `[data-theme="dark"]`.
- Keep all frontend logic inside `static/index.html`.

## Testing Conventions

- Every new endpoint or helper function **must** have a corresponding test.
- Tests use the `client` fixture from `conftest.py` / `test_main.py`, which patches `main.DB_PATH` to a `tmp_path` database.
- Test function names follow the pattern `test_<what>_<expected_outcome>` (e.g., `test_lookup_returns_404_for_missing_code`).
- Do **not** use `mock.patch` for the DB path — use `monkeypatch.setattr(main, "DB_PATH", ...)` as already established.
- Pure-function tests (encode/decode) do not need the `client` fixture.

## Security Notes

- Validate and decode short codes defensively — always catch `ValueError`/`KeyError` from `decode()` and raise `HTTPException(404)`.
- Use parameterised SQL queries (`?` placeholders) — never interpolate user input into SQL strings.
- The `normalize_code` helper strips full URLs down to the code segment before decoding; use it in any route that accepts a code.
