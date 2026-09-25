from app.core.constants import TAGS_CACHE_KEY


def test_list_tags_populates_cache(client, fake_cache):
    client.post("/api/tags/", json={"name": "backend"})

    assert TAGS_CACHE_KEY not in fake_cache
    response = client.get("/api/tags/")
    assert response.status_code == 200
    assert TAGS_CACHE_KEY in fake_cache


def test_list_tags_second_call_is_served_from_cache(client, fake_cache):
    client.post("/api/tags/", json={"name": "backend"})
    client.get("/api/tags/")  # warms the cache

    # Mutate the cached payload directly to prove the second call reads it back,
    # instead of re-querying the DB (which would still show "backend" only).
    cached = fake_cache[TAGS_CACHE_KEY]
    import json

    payload = json.loads(cached)
    payload.append({"id": 999, "name": "from-cache-only"})
    fake_cache[TAGS_CACHE_KEY] = json.dumps(payload)

    response = client.get("/api/tags/")
    names = [tag["name"] for tag in response.json()]
    assert "from-cache-only" in names


def test_create_tag_invalidates_cache(client, fake_cache):
    client.post("/api/tags/", json={"name": "backend"})
    client.get("/api/tags/")  # warms the cache
    assert TAGS_CACHE_KEY in fake_cache

    client.post("/api/tags/", json={"name": "urgent"})
    assert TAGS_CACHE_KEY not in fake_cache

    response = client.get("/api/tags/")
    names = {tag["name"] for tag in response.json()}
    assert names == {"backend", "urgent"}


def test_list_tags_pagination_applies_to_cached_data(client):
    for name in ["a", "b", "c", "d"]:
        client.post("/api/tags/", json={"name": name})
    client.get("/api/tags/")  # warm the cache

    response = client.get("/api/tags/", params={"skip": 1, "limit": 2})
    assert [tag["name"] for tag in response.json()] == ["b", "c"]
