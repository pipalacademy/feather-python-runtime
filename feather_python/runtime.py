import contextlib
import os
import subprocess
import tempfile

from feather_python.models import RunRequestMode, RunResponse


class PythonRuntime:
    def __init__(self, python_path, base_tempdir_path, entrypoint, timeout):
        self.python_path = python_path
        self.base_tempdir_path = base_tempdir_path
        self.entrypoint = entrypoint
        self.timeout = timeout

    def run(self, run_request: "RunRequest") -> RunResponse:
        with self.setup_fs(run_request) as tempdir:
            command = self.get_command(
                tempdir=tempdir, args=run_request.args or []
            )
            proc = subprocess.run(
                command, capture_output=True, timeout=self.timeout
            )

        return RunResponse(
            status_code=proc.returncode,
            stdout=proc.stdout.decode("utf-8"),
            stderr=proc.stderr.decode("utf-8"),
        )

    def run_tests(self, test_request: "TestRequest") -> "TestResponse":
        pass

    @contextlib.contextmanager
    def setup_fs(self, run_request: "RunRequest"):
        with tempfile.TemporaryDirectory(
            dir=self.base_tempdir_path
        ) as tempdir:
            if run_request.mode == RunRequestMode.FILES:
                for filepath, file in run_request.files.items():
                    final_filepath = os.path.join(tempdir, filepath)
                    file.save(final_filepath)
            else:
                filepath = os.path.join(tempdir, self.entrypoint)
                with open(filepath, "w") as f:
                    f.write(run_request.code)

            yield tempdir

    def get_command(self, tempdir, args=None):
        executable_file = os.path.join(tempdir, self.entrypoint)
        command = [self.python_path, executable_file] + (args or [])
        return command
