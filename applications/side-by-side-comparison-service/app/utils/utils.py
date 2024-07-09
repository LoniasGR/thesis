import os
from fastapi import Request


def envOrDefault(variable: str, default: str) -> str:
    ret: str | None = os.getenv(variable)
    if ret is None:
        return default
    else:
        return ret


def getHost(headers: Request.headers) -> str:
    host = headers["Host"]
    if "x-forwared-for" in headers:
        host = headers["x-forwared-for"]
    return host
