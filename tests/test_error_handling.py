def test_unhandled_exception_returns_generic_500_without_leaking_details(client, monkeypatch):
    from fastapi.testclient import TestClient

    from app.main import app
    from app.services import tag

    def boom(*args, **kwargs):
        raise RuntimeError("some secret internal detail")

    monkeypatch.setattr(tag, "get_tags", boom)

    # `client` (raise_server_exceptions=True, the default) re-raises the original
    # exception in the test instead of returning it as a response — deliberately, so a
    # real bug surfaces immediately in every other test. This one test's whole point is
    # to see the actual production response our handler builds, so it needs a client
    # that behaves like a real deployment and lets the response through instead.
    lenient_client = TestClient(app, raise_server_exceptions=False)
    response = lenient_client.get("/api/tags/")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


def test_cors_preflight_allows_configured_origin(client):
    response = client.options(
        "/api/tags/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_does_not_allow_unlisted_origin(client):
    response = client.options(
        "/api/tags/",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
