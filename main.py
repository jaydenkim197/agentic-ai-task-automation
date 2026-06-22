import fcntl
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
LOCK_FILE = Path("/private/tmp/agentic-ai-bot.lock")
os.chdir(PROJECT_ROOT)

from bot.discord_bot import run_bot  # noqa: E402


def acquire_single_instance_lock():
    lock_handle = LOCK_FILE.open("w")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_handle.close()
        return None
    lock_handle.write(str(os.getpid()))
    lock_handle.flush()
    return lock_handle


if __name__ == "__main__":
    instance_lock = acquire_single_instance_lock()
    if instance_lock is None:
        print("Another Agentic AI bot instance is already running.")
    else:
        run_bot()
