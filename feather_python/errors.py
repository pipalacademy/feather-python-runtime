class BaseFeatherError(Exception):
    title: str
    message: str
    status_code: int


class CodeNotFoundError(BaseFeatherError):
    title = "Code not found"
    message = "Expected code in the request data but couldn't find it there."
    status_code = 400


class IncorrectJSONError(BaseFeatherError):
    title = "Incorrect JSON schema"
    message = (
        "The JSON data submitted doesn't have required fields"
        " (or the desired type). Please verify with documentation."
    )
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


class InvalidFilepathError(BaseFeatherError):
    title = "Invalid filepath"
    message = "Filepath goes outside the expected directory"
    status_code = 400


class UnsupportedContentTypeError(BaseFeatherError):
    title = "Unsupported content type"
    message = (
        "The content type of request is not supported."
        " Please check documentation for supported formats"
    )
    status_code = 415
