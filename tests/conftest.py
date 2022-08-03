import pytest

from feather_python.app import app as feather_app


@pytest.fixture()
def app():
    return feather_app


@pytest.fixture()
def client(app):
    return app.test_client()


def get_run_endpoint():
    return "/runtimes/python"
