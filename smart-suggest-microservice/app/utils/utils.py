import os

def envOrDefault(variable: str, default: str) -> str:
     ret: str | None = os.getenv(variable)
     if ret is None:
          return default
     else:
          return ret
