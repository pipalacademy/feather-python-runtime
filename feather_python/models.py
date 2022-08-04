from enum import Enum
from io import BytesIO
from typing import Any, Dict, List, Optional

from werkzeug.datastructures import FileStorage

from feather_python.errors import UnsupportedContentTypeError


class RunRequestMode(Enum):
    CODE = "code"
    FILES = "files"


class RunRequest:
    ARGS_HEADER = "x-feather-args"
    ENV_HEADER = "x-feather-env"
    ENTRYPOINT_HEADER = "x-feather-entrypoint"

    def __init__(
        self,
        code: Optional[str] = None,
        files: Optional[Dict[str, FileStorage]] = None,
        entrypoint: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.code = code
        self.files = files
        self.entrypoint = entrypoint
        self.args = args
        self.env = env

    @property
    def mode(self) -> Enum:
        return RunRequestMode.FILES if self.files else RunRequestMode.CODE

    @classmethod
    def from_request(cls, request: "flask.Request") -> "RunRequest":
        code, files = None, None

        if request.mimetype == "multipart/form-data":
            files = dict(request.files)
        elif request.mimetype == "application/json" and (
            raw_files := request.json.get("files")
        ):
            files = {
                filename: create_filestorage(filename, content)
                for filename, content in raw_files.items()
            }
        elif request.mimetype == "application/x-www-form-urlencoded":
            code = next(iter(request.form.keys()))
        elif (
            request.mimetype in {"text/plain", "text/python"}
            or not request.mimetype
        ):
            code = request.data.decode("utf-8")
        else:
            raise UnsupportedContentTypeError()

        args = []
        if RunRequest.ARGS_HEADER in request.headers:
            args = cls.get_args_from_header(
                request.headers[RunRequest.ARGS_HEADER]
            )

        env = {}
        if RunRequest.ENV_HEADER in request.headers:
            env = cls.get_env_from_header(
                request.headers[RunRequest.ENV_HEADER]
            )

        entrypoint = None
        if RunRequest.ENTRYPOINT_HEADER in request.headers:
            entrypoint = request.headers[RunRequest.ENTRYPOINT_HEADER]

        return cls(
            code=code, files=files, args=args, env=env, entrypoint=entrypoint
        )

    @classmethod
    def get_args_from_header(cls, header_value: str) -> List[str]:
        return header_value.split(" ")

    @classmethod
    def get_env_from_header(cls, header_value: str) -> Dict[str, str]:
        return dict(
            assignment.split("=") for assignment in header_value.split(" ")
        )


class RunResponse:
    def __init__(
        self, status_code: int = None, stdout: str = None, stderr: str = None
    ) -> None:
        self.status_code = status_code
        self.stdout = stdout
        self.stderr = stderr


def create_filestorage(filename: str, content: str) -> FileStorage:
    bcontent = bytes(content, "utf-8")
    return FileStorage(stream=BytesIO(bcontent), filename=filename)
