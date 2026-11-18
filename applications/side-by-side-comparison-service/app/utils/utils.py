import os


def envOrDefault(variable: str, default: str) -> str:
    ret: str | None = os.getenv(variable)
    if ret is None:
        return default
    else:
        return ret


def getHost(headers) -> str:
    host = headers["Host"]
    if "x-forwarded-for" in headers:
        host = headers["x-forwarded-for"]
    return host


def shouldPrint(condition):
    def output(text):
        if condition:
            print(text)

    return output
