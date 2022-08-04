from flask import request

from io import BytesIO

from feather_python.models import RunRequest, RunRequestMode


def test_get_runrequest_from_flask_request_with_multipart(app):
    filename = "test.py"
    content = "Hello, world!"

    with app.test_request_context(
        "/runtimes/python",
        method="POST",
        data={filename: (BytesIO(content.encode("utf-8")), filename)},
    ):
        run_request = RunRequest.from_request(request)

        assert run_request.code is None
        assert run_request.mode == RunRequestMode.FILES
        assert len(run_request.files) == 1 and filename in run_request.files

        file = run_request.files[filename]
        assert file.filename == filename
        assert file.stream.read().decode("utf-8") == content


def test_get_runrequest_from_flask_request_with_multipart_and_multiple_files(
    app,
):
    test_files = {
        "test.py": "Hello, world!",
        "test2.py": "content of test2.py",
        "test3.txt": "content of test3.txt",
    }

    with app.test_request_context(
        "/runtimes/python",
        method="POST",
        data={
            filename: (BytesIO(content.encode("utf-8")), filename)
            for filename, content in test_files.items()
        },
    ):
        run_request = RunRequest.from_request(request)

        assert run_request.code is None
        assert run_request.mode == RunRequestMode.FILES
        assert len(run_request.files) == 3

        for filename in test_files:
            file = run_request.files[filename]
            expected_content = test_files[filename]
            assert file.filename == filename
            assert file.stream.read().decode("utf-8") == expected_content


def test_get_runrequest_from_flask_request_with_json(app):
    filename = "test.py"
    content = """print("Hello from inside a test, world!")"""

    with app.test_request_context(
        "/runtimes/python",
        method="POST",
        json={"files": {filename: content}},
    ):
        run_request = RunRequest.from_request(request)

        assert run_request.code is None
        assert run_request.mode == RunRequestMode.FILES
        assert len(run_request.files) == 1 and filename in run_request.files

        file = run_request.files[filename]
        assert file.filename == filename
        assert file.stream.read().decode("utf-8") == content


def test_get_runrequest_from_flask_request_with_json_and_multiple_files(app):
    test_files = {
        "test.py": "Hello, world!",
        "test2.py": "content of test2.py",
        "test3.txt": "content of test3.txt",
    }

    with app.test_request_context(
        "/runtimes/python",
        method="POST",
        json={
            "files": {
                filename: content for filename, content in test_files.items()
            }
        },
    ):
        run_request = RunRequest.from_request(request)

        assert run_request.code is None
        assert run_request.mode == RunRequestMode.FILES
        assert len(run_request.files) == 3

        for filename in test_files:
            file = run_request.files[filename]
            expected_content = test_files[filename]
            assert file.filename == filename
            assert file.stream.read().decode("utf-8") == expected_content


def test_get_runrequest_from_flask_request_with_code(app):
    code = """print("Hello from inside a test, world!")"""

    with app.test_request_context(
        "/runtimes/python", method="POST", data=code
    ):
        run_request = RunRequest.from_request(request)

        assert run_request.files is None
        assert run_request.mode == RunRequestMode.CODE
        assert run_request.code == code
