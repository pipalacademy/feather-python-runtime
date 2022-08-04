class BaseFeatherError(Exception):
    title: str
    message: str
    status_code: int


class CodeNotFoundError(BaseFeatherError):
    title = "Invalid input"
    message = "Code not found"
    status_code = 400


class IncorrectJSONError(BaseFeatherError):
    title = "Invalid input"
    message = "Incorrect schema for JSON. Please verify with documentation."
    status_code = 400


class EntrypointNotFoundError(BaseFeatherError):
    title = "Entrypoint not found"
    message = (
        "An entrypoint file should be present with name `main.py`"
        " (or the filepath set with `x-feather-entrypoint` header)."
    )
    status_code = 400


class InvalidFilenameError(BaseFeatherError):
    title = "Invalid filename"
    message = "Filename has invalid characters"
    status_code = 400


class UnsupportedContentTypeError(BaseFeatherError):
    title = "Unsupported content type"
    message = (
        "The content type of request is not supported."
        " Please check documentation for supported formats"
    )
    status_code = 415
