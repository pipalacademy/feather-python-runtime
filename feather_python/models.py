from enum import Enum
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

from werkzeug.datastructures import FileStorage

from feather_python.errors import (
    CodeNotFoundError,
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
    def mode(self) -> RunRequestMode:
        return RunRequestMode.FILES if self.files else RunRequestMode.CODE

    @classmethod
    def from_request(cls, request: "flask.Request") -> "RunRequest":
        file_getter = cls._get_files_getter(request.mimetype)
        code_getter = cls._get_code_getter(request.mimetype)
        if not file_getter and not code_getter:
            raise UnsupportedContentTypeError()

        files = file_getter and file_getter(request)
        code = code_getter and code_getter(request)

        args = cls._get_args(request.headers.get(RunRequest.ARGS_HEADER, ""))
        env = cls._get_env(request.headers.get(RunRequest.ENV_HEADER, ""))
        entrypoint = cls._get_entrypoint(
            request.headers.get(RunRequest.ENTRYPOINT_HEADER, "")
        )

        return cls(
            code=code, files=files, args=args, env=env, entrypoint=entrypoint
        )

    @classmethod
    def _get_files_getter(cls, mimetype: str):
        getters = {
            "application/json": cls._get_files_from_json,
            "multipart/form-data": cls._get_files_from_multipart,
        }
        return getters.get(mimetype)

    @classmethod
    def _get_code_getter(cls, mimetype: str):
        getters = {
            "application/x-www-form-urlencoded": cls._get_code_from_formdata,
            "text/plain": cls._get_code_from_plaintext,
            "text/python": cls._get_code_from_plaintext,
            "": cls._get_code_from_plaintext,
        }
        return getters.get(mimetype)

    @staticmethod
    def _get_files_from_json(
        request: "flask.Request",
    ) -> Dict[str, FileStorage]:
        if "files" in request.json:
            raw_files = request.json["files"]
            files = {
                str(filename): create_filestorage(filename, content)
                for filename, content in raw_files.items()
            }
        else:
            raise IncorrectJSONError()

        if not files:
            raise CodeNotFoundError()

        return files

    @staticmethod
    def _get_files_from_multipart(
        request: "flask.Request",
    ) -> Dict[str, FileStorage]:
        files = dict(request.files)
        if not files:
            raise CodeNotFoundError()

        return files

    @staticmethod
    def _get_code_from_formdata(request: "flask.Request") -> str:
        try:
            return next(iter(request.form.keys()))
        except StopIteration:
            raise CodeNotFoundError()

    @staticmethod
    def _get_code_from_plaintext(request: "flask.Request") -> str:
        code = request.data.decode("utf-8")
        if not code:
            raise CodeNotFoundError()

        return code

    @staticmethod
    def _get_args(header_value: str) -> List[str]:
        return header_value and header_value.split(" ") or []

    @staticmethod
    def _get_env(header_value: str) -> Dict[str, str]:
        assignments = header_value and header_value.split(" ") or []

        # env_list: [[key1, val1], [key2, val2], [key3, val3], ...]
        env_list = [
            assignment.split("=", maxsplit=1)
            for assignment in assignments
            if "=" in assignment
        ]

        return dict(env_list)

    @staticmethod
    def _get_entrypoint(header_value: str) -> Union[str, None]:
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
