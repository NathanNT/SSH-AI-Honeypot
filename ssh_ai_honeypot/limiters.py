import time
import threading
from collections import deque
from typing import Deque, Dict, Tuple

class AuthAttemptGate:
    def __init__(self, required_attempts: int, reset_window_sec: int):
        self.required = max(1, required_attempts)
        self.window = max(1, reset_window_sec)
        self._lock = threading.Lock()
        self._attempts: Dict[str, Tuple[int, float]] = {}

    def register_attempt(self, ip: str) -> Tuple[int, bool]:
        now = time.time()
        with self._lock:
            count, last = self._attempts.get(ip, (0, 0.0))
            if now - last > self.window:
                count = 0
            count += 1
            self._attempts[ip] = (count, now)
            allowed = (count >= self.required)
            return count, allowed

class CommandRateLimiter:
    def __init__(self, max_commands: int, window_sec: int):
        self.max = max(1, max_commands)
        self.window = max(1, window_sec)
        self._lock = threading.Lock()
        self._events: Dict[str, Deque[float]] = {}

    def allow(self, ip: str) -> bool:
        now = time.time()
        with self._lock:
            dq = self._events.setdefault(ip, deque())
            while dq and now - dq[0] > self.window:
                dq.popleft()
            if len(dq) >= self.max:
                return False
            dq.append(now)
            return True

class BanManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._bans: Dict[str, float] = {}

    def ban(self, ip: str, duration_sec: int):
        until = time.time() + max(1, duration_sec)
        with self._lock:
            self._bans[ip] = until

    def is_banned(self, ip: str) -> bool:
        now = time.time()
        with self._lock:
            until = self._bans.get(ip)
            if not until:
                return False
            if now >= until:
                del self._bans[ip]
                return False
            return True

    def remaining(self, ip: str) -> int:
        with self._lock:
            until = self._bans.get(ip, 0.0)
            return int(max(0.0, until - time.time()))
