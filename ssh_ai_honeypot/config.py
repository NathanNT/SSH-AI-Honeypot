import os

def _load_env_from_dotenv():
    try:
        # Preferred python-dotenv
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv(), override=False)
    except Exception:
        # Fallback tiny loader read local .env if exists
        for candidate in (os.path.join(os.getcwd(), ".env"),
                          os.path.join(os.path.dirname(__file__), ".env")):
            if os.path.exists(candidate):
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip()
                            # don't override existing env vars
                            os.environ.setdefault(k, v)
                except Exception:
                    pass
                break

_load_env_from_dotenv()

HOST = os.environ.get("HONEY_HOST", "0.0.0.0")
PORT = int(os.environ.get("HONEY_PORT", "2222"))
PROMPT = os.environ.get("HONEY_PROMPT", "$ ")
WELCOME = "Welcome to the fake SSH server!\r\n"
HOSTKEY_PATH = os.environ.get("HONEY_HOSTKEY", "server_host_rsa.key")
DEBUG = os.environ.get("HONEY_DEBUG", "1") == "1"

LOG_DIR = os.environ.get("HONEY_LOG_DIR", "logs")
LOG_PATH = os.path.join(LOG_DIR, os.environ.get("HONEY_LOG_PATH", "logs/commands.log").split("/", 1)[-1]) \
    if os.path.isabs(LOG_DIR) else os.environ.get("HONEY_LOG_PATH", os.path.join(LOG_DIR, "commands.log"))
LOG_AUTH_PATH = os.environ.get("HONEY_LOG_AUTH_PATH", os.path.join(LOG_DIR, "auth.log"))
os.makedirs(LOG_DIR, exist_ok=True)

ACCESS_AFTER_ATTEMPTS = int(os.environ.get("HONEY_ACCESS_AFTER_ATTEMPTS", "1"))
ATTEMPT_RESET_WINDOW_SEC = int(os.environ.get("HONEY_ATTEMPT_RESET_WINDOW_SEC", "600"))

RATE_MAX_COMMANDS = int(os.environ.get("HONEY_RATE_MAX_COMMANDS", "100"))
RATE_WINDOW_SEC = int(os.environ.get("HONEY_RATE_WINDOW_SEC", "60"))

BAN_DURATION_SEC = int(os.environ.get("HONEY_BAN_DURATION_SEC", "300"))

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-nano")
SYSTEM_PROMPT = os.environ.get(
    "HONEY_SYSTEM_PROMPT",
    "You are a cooperative Linux terminal. Respond only with raw command output, never explanations."
)
WELCOME = os.environ.get(
    "HONEY_WELCOME",
    "Welcome to the fake SSH server!\r\n"
)