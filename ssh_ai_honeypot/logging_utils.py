import json
from datetime import datetime, timezone
from .config import LOG_PATH, LOG_AUTH_PATH, DEBUG

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def log_command(*, client_ip: str, username: str, mode: str, command: str):
    rec = {"ts": _now_iso(), "client_ip": client_ip, "username": username, "mode": mode, "command": command}
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        if DEBUG:
            print(f"[log] Failed to write command log: {e}")

def log_auth_attempt(*, client_ip: str, username: str, attempt: int, allowed: bool, required_attempts: int):
    rec = {"ts": _now_iso(), "client_ip": client_ip, "username": username, "attempt": attempt, "allowed": allowed, "required_attempts": required_attempts}
    try:
        with open(LOG_AUTH_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        if DEBUG:
            print(f"[log] Failed to write auth log: {e}")
