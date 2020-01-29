_RESPONSE_HEADERS_VAR = None
try:
    import contextvars

    _RESPONSE_HEADERS_VAR = contextvars.ContextVar(
        "response_headers", default={}
    )
except ImportError:
    pass


def set_response_headers(headers: dict):
    if _RESPONSE_HEADERS_VAR is not None:
        _RESPONSE_HEADERS_VAR.get().update(headers)
    else:
        print(
            "This feature < set_response_headers > only works with python 3.7"
        )


def get_response_headers():
    if _RESPONSE_HEADERS_VAR is not None:
        return _RESPONSE_HEADERS_VAR.get()
    return {}
