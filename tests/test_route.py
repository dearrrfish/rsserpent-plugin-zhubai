from starlette.testclient import TestClient


def test_route(client: TestClient) -> None:
    """Test `rsserpent_plugin_zhubai.route`."""
    response = client.get("/zhubai/designscenes")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/xml"
    assert response.text.count("Design Scenes Weekly") == 1
