import os
import subprocess
import tempfile

from flask import Flask, request


BASE_TEMPDIR_PATH = os.getenv("FEATHER_BASE_TEMPDIR_PATH", "/tmp/")
DEFAULT_ENTRYPOINT = "main.py"
PYTHON_EXECUTABLE_PATH = "python3"
SUBPROCESS_TIMEOUT = 30  # seconds

app = Flask("feather-runtime-python")


@app.route("/runtime/python", methods=["GET", "POST"])
def run():
    with tempfile.TemporaryDirectory(dir=BASE_TEMPDIR_PATH) as tempdir:
        for filepath, file in request.files.items():
            final_filepath = os.path.join(tempdir, filepath)
            file.save(final_filepath)

        executable_file = os.path.join(tempdir, DEFAULT_ENTRYPOINT)
        command = [PYTHON_EXECUTABLE_PATH, executable_file]
        proc = subprocess.run(command, capture_output=True, timeout=SUBPROCESS_TIMEOUT)
        output = proc.stdout if proc.stdout else proc.stderr

    return output
