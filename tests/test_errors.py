def test_unsupported_content_type(client):
    response = client.post(
        "/runtimes/python",
        headers={"Content-Type": "unsupported/type"},
        data="something random",
    )

    assert response.status_code == 415
    assert "error" in response.json
    assert "message" in response.json
