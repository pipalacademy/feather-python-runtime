from io import BytesIO

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


def test_incorrect_json_error(client):
    json_data = {"main.py": "this main.py should be under a 'files' key"}

    response = client.post(
        endpoint,
        json=json_data,
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Incorrect JSON schema"


def test_code_not_found_error_with_form_urlencoded(client):
    response = client.post(endpoint, data="")

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Code not found"


def test_code_not_found_error_with_textplain(client):
    response = client.post(
        endpoint, headers={"Content-Type": "text/python"}, data=""
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Code not found"


def test_code_not_found_error_with_json(client):
    response = client.post(
        endpoint,
        json={
            "files": {},
        },
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Code not found"


def test_code_not_found_error_with_multipart(client):
    response = client.post(
        endpoint,
        headers={"Content-Type": "multipart/form-data"},
        data={},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Code not found"


def test_entrypoint_not_found_with_explicit_entrypoint(client):
    response = client.post(
        endpoint,
        headers={"x-feather-entrypoint": "does_not_exist.py"},
        data={"main.py": (BytesIO(b"this is main.py"), "main.py")},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Entrypoint not found"


def test_entrypoint_not_found_with_default_entrypoint(client):
    response = client.post(
        endpoint,
        data={"not_main.py": (BytesIO(b"this is not main.py"), "not_main.py")},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Entrypoint not found"


def test_entrypoint_not_found_with_default_entrypoint_and_filename_mismatch(
    client,
):
    response = client.post(
        endpoint,
        data={"not_main.py": (BytesIO(b"this is not main.py"), "main.py")},
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Entrypoint not found"


def test_invalid_filepath_error_when_filepath_is_relative(client):
    response = client.post(
        endpoint,
        json={
            "files": {
                "main.py": "print('hello, world!')",
                "../foo.py": "this shouldn't be here",
            }
        },
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid filepath"


def test_invalid_filepath_error_when_filepath_is_at_root(client):
    response = client.post(
        endpoint,
        json={
            "files": {
                "main.py": "print('hello, world!')",
                "/foo.py": "this shouldn't be here",
            }
        },
    )

    assert response.status_code == 400
    assert "error" in response.json
    assert "message" in response.json
    assert response.json["error"] == "Invalid filepath"
