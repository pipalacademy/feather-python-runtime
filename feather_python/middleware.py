from functools import wraps

from feather_python.errors import BaseFeatherError


def handle_feather_errors(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except BaseFeatherError as e:
            title, message, status_code = e.title, e.message, e.status_code
            return {
                "error": title,
                "message": message,
            }, status_code

    return wrapper
