import paramiko
from .logging_utils import log_auth_attempt

class SSHServer(paramiko.ServerInterface):
    def __init__(self, *, client_ip: str, auth_gate):
        super().__init__()
        self.exec_command = None
        self.client_ip = client_ip
        self.auth_gate = auth_gate
        self._last_username = "user"

    @property
    def username(self):
        return self._last_username

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        self._last_username = username or "user"
        attempt_index, allowed = self.auth_gate.register_attempt(self.client_ip)
        log_auth_attempt(client_ip=self.client_ip, username=self._last_username, attempt=attempt_index, allowed=allowed, required_attempts=self.auth_gate.required)
        return paramiko.AUTH_SUCCESSFUL if allowed else paramiko.AUTH_FAILED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_exec_request(self, channel, command):
        try:
            self.exec_command = command.decode("utf-8", errors="ignore")
        except Exception:
            self.exec_command = str(command)
        return True

    def check_channel_signal_request(self, channel, signal_name):
        if signal_name in ("INT", "TERM", "KILL"):
            try:
                channel.send("^C\r\nBye!\r\n")
                channel.close()
            except Exception:
                pass
        return True
