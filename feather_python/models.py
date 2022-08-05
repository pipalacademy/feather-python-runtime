from enum import Enum
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

from werkzeug.datastructures import FileStorage

from feather_python.errors import (
    IncorrectJSONError,
    UnsupportedContentTypeError,
)


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
        elif request.mimetype == "application/json":
            if raw_files := request.json.get("files"):
                files = {
                    filename: create_filestorage(filename, content)
                    for filename, content in raw_files.items()
                }
            else:
                raise IncorrectJSONError()
        elif request.mimetype == "application/x-www-form-urlencoded":
            code = next(iter(request.form.keys()))
        elif request.mimetype in {"text/plain", "text/python", ""}:
            code = request.data.decode("utf-8")
        else:
            raise UnsupportedContentTypeError()

        args = cls.get_args_from_header(
            request.headers.get(RunRequest.ARGS_HEADER, "")
        )
        env = cls.get_env_from_header(
            request.headers.get(RunRequest.ENV_HEADER, "")
        )
        entrypoint = cls.get_entrypoint_from_header(
            request.headers.get(RunRequest.ENTRYPOINT_HEADER, "")
        )

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

    @classmethod
    def get_entrypoint_from_header(cls, header_value: str) -> Union[str, None]:
        return header_value or None


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
