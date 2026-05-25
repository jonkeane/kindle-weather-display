import datetime
from pathlib import Path
import time


def current_local_datetime():
    return datetime.datetime.fromtimestamp(time.mktime(time.localtime()))


def fileChecker(path, refreshInterval, now=None):
    path = Path(path)
    if not path.is_file():
        return "create"

    if now is None:
        now_timestamp = time.time()
    elif isinstance(now, datetime.datetime):
        now_timestamp = now.timestamp()
    else:
        now_timestamp = float(now)

    if now_timestamp - path.stat().st_mtime > refreshInterval:
        return "create"
    return "useOld"
