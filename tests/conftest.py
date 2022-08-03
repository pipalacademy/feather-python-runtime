import pytest

from feather_python.app import app as feather_app


@pytest.fixture()
def app():
    yield feather_app
