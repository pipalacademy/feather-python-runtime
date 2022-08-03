import textwrap
from collections import namedtuple
from io import BytesIO

from tests.conftest import get_run_endpoint

endpoint = get_run_endpoint()

FakeMultipleFilesData = namedtuple(
    "FakeMultipleFilesData", ["files", "expected_output"]
)
FakeMultipleFilesWithErrorData = namedtuple(
    "FakeMultipleFilesWithErrorData", ["files", "expected_in_output"]
)
FakeCodeData = namedtuple("FakeCodeData", ["code", "expected_output"])
FakeCodeWithErrorData = namedtuple(
    "FakeCodeWithErrorData", ["code", "expected_in_output"]
)


def test_run_with_code_without_headers(client):
    code, expected_output = get_fake_data_with_code()
    response = client.post(endpoint, data=code)

    assert response.status_code == 200
    assert response.text == expected_output


def test_run_with_code_with_form_content_type(client):
    code, expected_output = get_fake_data_with_code()
    response = client.post(
        endpoint,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=code,
    )

    assert response.status_code == 200
    assert response.text == expected_output


def test_run_with_multiple_files_as_multipart(client):
    fake_data = get_fake_data_with_multiple_files()
    files = fake_data.files
    expected_output = fake_data.expected_output

    data = {
        filename: (BytesIO(content.encode("utf-8")), filename)
        for filename, content in files.items()
    }

    response = client.post(endpoint, data=data)

    assert response.status_code == 200
    assert response.text == expected_output


def test_run_with_multiple_files_as_json(client):
    fake_data = get_fake_data_with_multiple_files()
    files = fake_data.files
    expected_output = fake_data.expected_output

    response = client.post(endpoint, json={"files": files})

    assert response.status_code == 200
    assert response.text == expected_output


def test_run_with_multiple_files_that_errors(client):
    fake_data = get_fake_data_with_multiple_files_that_errors()
    files, expected_in_output = fake_data

    data = {
        filename: (BytesIO(content.encode("utf-8")), filename)
        for filename, content in files.items()
    }

    response = client.post(endpoint, data=data)

    assert response.status_code == 200
    assert expected_in_output in response.text


def test_run_with_code_that_errors(client):
    fake_data = get_fake_data_with_code_that_errors()
    code, expected_in_output = fake_data.code, fake_data.expected_in_output

    response = client.post(endpoint, data=code)

    assert response.status_code == 200
    assert expected_in_output in response.text


def get_fake_data_with_multiple_files():
    files = {
        "code.py": textwrap.dedent(
            """
        def code():
            print("hi from code.py")
        """
        ),
        "main.py": textwrap.dedent(
            """
        from code import code

        code()
        """
        ),
    }
    expected_output = "hi from code.py\n"

    return FakeMultipleFilesData(files=files, expected_output=expected_output)


def get_fake_data_with_code():
    code = 'print("hello, world!")\n'
    expected_output = "hello, world!\n"
    return FakeCodeData(code=code, expected_output=expected_output)


def get_fake_data_with_code_that_errors():
    code = textwrap.dedent(
        """
    raise Exception("test exception")
    """
    )
    expected_in_output = "Exception: test exception"

    return FakeCodeWithErrorData(
        code=code, expected_in_output=expected_in_output
    )


def get_fake_data_with_multiple_files_that_errors():
    files = {
        "code.py": textwrap.dedent(
            """
        def code():
            raise Exception("test exception")
        """
        ),
        "main.py": textwrap.dedent(
            """
        from code import code

        code()
        """
        ),
    }
    expected_in_output = "test exception\n"

    return FakeMultipleFilesWithErrorData(
        files=files, expected_in_output=expected_in_output
    )
