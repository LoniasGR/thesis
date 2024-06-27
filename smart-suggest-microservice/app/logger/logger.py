import logging
import uvicorn


class CustomLogger(logging.Logger):
    FORMAT = "%(levelprefix)s %(message)s"

    def __init__(self, name: str, level: int = logging.DEBUG) -> None:
        super().__init__(name, level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(uvicorn.logging.DefaultFormatter(self.FORMAT))
        self.addHandler(ch)
