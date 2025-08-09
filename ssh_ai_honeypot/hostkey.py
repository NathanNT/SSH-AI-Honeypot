import os
import paramiko
from .config import HOSTKEY_PATH, DEBUG

def load_or_create_hostkey(path: str) -> paramiko.RSAKey:
    if os.path.exists(path):
        return paramiko.RSAKey(filename=path)
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(path)
    if DEBUG: print(f"[hostkey] New server key created at: {path}")
    return key

HOST_KEY = load_or_create_hostkey(HOSTKEY_PATH)
