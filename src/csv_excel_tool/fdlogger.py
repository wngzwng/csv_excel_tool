import os
import sys
from datetime import datetime

class FdLogger:
    def __init__(self, fd=None, level="INFO", timestamp=True):
        # 默认写到 stderr
        self.fd = fd if fd is not None else sys.stderr.fileno()
        self.level = level
        self.timestamp = timestamp

    def _write(self, level, msg):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else ""
        line = f"[{t}] [{level}] {msg}\n" if self.timestamp else f"[{level}] {msg}\n"
        os.write(self.fd, line.encode("utf-8"))

    def info(self, msg):
        if self.level in ("INFO", "DEBUG"):
            self._write("INFO", msg)

    def debug(self, msg):
        if self.level == "DEBUG":
            self._write("DEBUG", msg)

    def error(self, msg):
        self._write("ERROR", msg)
