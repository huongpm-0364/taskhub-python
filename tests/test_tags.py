def test_create_tag(client):
    response = client.post("/api/tags/", json={"name": "backend"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "backend"


def test_get_tag_not_found(client):
    response = client.get("/api/tags/999")
    assert response.status_code == 404


def test_list_tags(client):
    client.post("/api/tags/", json={"name": "backend"})
    client.post("/api/tags/", json={"name": "urgent"})

    response = client.get("/api/tags/")
    assert response.status_code == 200
    assert len(response.json()) == 2
