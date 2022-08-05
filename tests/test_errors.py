from tests.conftest import get_run_endpoint


endpoint = get_run_endpoint()


def test_unsupported_content_type(client):
    response = client.post(
        endpoint,
        headers={"content-type": "unsupported/type"},
        data="something random",
    )

    assert response.status_code == 415
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Unsupported content type"


def test_incorrect_json_error(client, run_endpoint):
    json_data = {"main.py": "this main.py should be under a 'files' key"}

    response = client.post(
        endpoint,
        json=json_data,
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid input"


def test_code_not_found_error_with_form_urlencoded(client):
    response = client.post(endpoint, data="")

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid input"


def test_code_not_found_error_with_textplain(client):
    response = client.post(
        endpoint, headers={"Content-Type": "text/python"}, data=""
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid input"


def test_code_not_found_error_with_json(client):
    response = client.post(
        endpoint,
        json={},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid input"


def test_code_not_found_error_with_multipart(client):
    response = client.post(
        endpoint,
        headers={"Content-Type": "multipart/form-data"},
        data={},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid input"
