import os

from flask import Flask, request
from flask_cors import CORS

from feather_python.middleware import handle_feather_errors
from feather_python.models import RunRequest
from feather_python.runtime import PythonRuntime


BASE_TEMPDIR_PATH = os.getenv("FEATHER_BASE_TEMPDIR_PATH", "/tmp/")
DEFAULT_ENTRYPOINT = "main.py"
PYTHON_EXECUTABLE_PATH = "python3"
SUBPROCESS_TIMEOUT = 30  # seconds

app = Flask("feather_python")
CORS(
    app,
    allow_headers=["x-feather-args", "x-feather-env", "x-feather-entrypoint"],
)


@app.route("/runtimes/python", methods=["GET", "POST"])
@handle_feather_errors
def run():
    """
    Response behavior:
    stdout if exit code was 0 (OK), else the stderr output as
    text/plain
    """

    run_request = RunRequest.from_request(request)
    runtime = PythonRuntime(
        python_path=PYTHON_EXECUTABLE_PATH,
        base_tempdir_path=BASE_TEMPDIR_PATH,
        default_entrypoint=DEFAULT_ENTRYPOINT,
        timeout=SUBPROCESS_TIMEOUT,
    )

    run_response = runtime.run(run_request)

    return (
        run_response.stdout
        if run_response.status_code == 0
        else run_response.stderr
    )
