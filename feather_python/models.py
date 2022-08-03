from enum import Enum
from io import BytesIO
from typing import Dict, Optional

from werkzeug.datastructures import FileStorage


class RunRequestMode(Enum):
    CODE = "code"
    FILES = "files"


class RunRequest:
    def __init__(
        self,
        code: Optional[str] = None,
        files: Optional[Dict[str, FileStorage]] = None,
        entrypoint: Optional[str] = None,
    ) -> None:
        self.code = code
        self.files = files
        self.entrypoint = entrypoint

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
        elif request.form:
            code = next(iter(request.form.keys()))
        elif request.data:
            code = request.data.decode("utf-8")
        else:
            # TODO: raise custom exception
            raise Exception("unsupported method")

        return cls(code=code, files=files)


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
