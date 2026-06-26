from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test_urls.db"
    monkeypatch.setattr(main, "DB_PATH", db_path)

    with TestClient(main.app) as test_client:
        yield test_client


def test_base62_encode_decode_round_trip():
    values = [0, 1, 9, 10, 35, 36, 61, 62, 63, 3843, 99999]

    for value in values:
        encoded = main.encode(value)
        decoded = main.decode(encoded)
        assert decoded == value


def test_base62_decode_invalid_character_raises():
    with pytest.raises(ValueError):
        main.decode("+")


def test_shorten_returns_short_code_and_url(client: TestClient):
    response = client.post("/shorten", json={"url": "https://example.com/page"})

    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["short_code"]
    assert data["short_url"].endswith(f"/{data['short_code']}")


def test_lookup_returns_original_url_json(client: TestClient):
    create_response = client.post("/shorten", json={"url": "https://example.com/lookup"})
    code = create_response.json()["short_code"]

    lookup_response = client.get(f"/lookup/{code}")

    assert lookup_response.status_code == 200
    assert lookup_response.json() == {"url": "https://example.com/lookup"}


def test_lookup_returns_404_for_missing_code(client: TestClient):
    response = client.get("/lookup/zzzzzz")

    assert response.status_code == 404
    assert response.json()["detail"] == "Short URL not found"


def test_redirect_endpoint_redirects_to_original_url(client: TestClient):
    create_response = client.post("/shorten", json={"url": "https://example.com/redirect"})
    code = create_response.json()["short_code"]

    redirect_response = client.get(f"/{code}", follow_redirects=False)

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/redirect"
