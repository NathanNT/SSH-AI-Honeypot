import os

HOST = os.environ.get("HONEY_HOST", "0.0.0.0")
PORT = int(os.environ.get("HONEY_PORT", "2222"))
PROMPT = os.environ.get("HONEY_PROMPT", "$ ")
WELCOME = "Welcome to the fake SSH server!\r\n"
HOSTKEY_PATH = os.environ.get("HONEY_HOSTKEY", "server_host_rsa.key")
DEBUG = os.environ.get("HONEY_DEBUG", "1") == "1"

LOG_DIR = os.environ.get("HONEY_LOG_DIR", "logs")
LOG_PATH = os.environ.get("HONEY_LOG_PATH", os.path.join(LOG_DIR, "commands.log"))
LOG_AUTH_PATH = os.environ.get("HONEY_LOG_AUTH_PATH", os.path.join(LOG_DIR, "auth.log"))
os.makedirs(LOG_DIR, exist_ok=True)

ACCESS_AFTER_ATTEMPTS = int(os.environ.get("HONEY_ACCESS_AFTER_ATTEMPTS", "1"))
ATTEMPT_RESET_WINDOW_SEC = int(os.environ.get("HONEY_ATTEMPT_RESET_WINDOW_SEC", "600"))

RATE_MAX_COMMANDS = int(os.environ.get("HONEY_RATE_MAX_COMMANDS", "100"))
RATE_WINDOW_SEC = int(os.environ.get("HONEY_RATE_WINDOW_SEC", "60"))

BAN_DURATION_SEC = int(os.environ.get("HONEY_BAN_DURATION_SEC", "300"))
