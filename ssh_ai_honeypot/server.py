import socket, threading

import paramiko
from .config import HOST, PORT, PROMPT, WELCOME, DEBUG, ACCESS_AFTER_ATTEMPTS, ATTEMPT_RESET_WINDOW_SEC, RATE_MAX_COMMANDS, RATE_WINDOW_SEC, BAN_DURATION_SEC
from .hostkey import HOST_KEY
from .ssh_server_iface import SSHServer
from .session_state import SessionState
from .emulator import emulate_locally
from .ai_backend import ai_shell_response
from .io_terminal import read_line_interactive
from .logging_utils import log_command
from .limiters import AuthAttemptGate, CommandRateLimiter, BanManager

STOP_EVENT = threading.Event()
LISTEN_SOCK = None

AUTH_GATE = AuthAttemptGate(required_attempts=ACCESS_AFTER_ATTEMPTS, reset_window_sec=ATTEMPT_RESET_WINDOW_SEC)
CMD_LIMITER = CommandRateLimiter(max_commands=RATE_MAX_COMMANDS, window_sec=RATE_WINDOW_SEC)
BAN_MANAGER = BanManager()

def handle_client(client_socket: socket.socket, client_ip: str):
    if BAN_MANAGER.is_banned(client_ip):
        try:
            client_socket.close()
        except Exception:
            pass
        return

    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)
    server = SSHServer(client_ip=client_ip, auth_gate=AUTH_GATE)

    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        if DEBUG: print("SSH handshake failed")
        transport.close(); return

    chan = transport.accept(20)
    if chan is None:
        if DEBUG: print("No channel opened.")
        transport.close(); return

    username = getattr(server, "username", None) or "user"
    state = SessionState(username=username)

    def rate_exceeded_action(channel: paramiko.Channel):
        BAN_MANAGER.ban(client_ip, BAN_DURATION_SEC)
        remaining = BAN_MANAGER.remaining(client_ip)
        try:
            channel.send(f"Rate limit exceeded. You are temporarily banned for {remaining} seconds.\r\n")
        except Exception:
            pass
        try:
            channel.close()
        except Exception:
            pass

    try:
        if server.exec_command is not None:
            cmd = server.exec_command.strip()
            if not CMD_LIMITER.allow(client_ip):
                rate_exceeded_action(chan)
                return
            log_command(client_ip=client_ip, username=state.username, mode="exec", command=cmd)
            local = emulate_locally(cmd, state)
            out = local if local is not None else ai_shell_response(cmd, state.state_prompt())
            chan.send(out or "")
            return

        chan.send(WELCOME)

        while True:
            history_cmds = [h["cmd"] for h in state.history]
            line = read_line_interactive(chan, PROMPT, history_cmds)
            if line in ("__CONN_CLOSED__", "__CTRL_D__", "__CTRL_C__"):
                chan.send("Bye!\r\n"); break

            cmd = line.strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit", "logout"):
                chan.send("Bye!\r\n"); break

            if not CMD_LIMITER.allow(client_ip):
                rate_exceeded_action(chan)
                break

            log_command(client_ip=client_ip, username=state.username, mode="interactive", command=cmd)

            local = emulate_locally(cmd, state)
            if local is None:
                ai_out = ai_shell_response(cmd, state.state_prompt())
                out = ai_out if ai_out is not None else ""
            else:
                out = local

            trimmed = out.replace("\r\n", "\n")
            state.history.append({"cmd": cmd, "out": trimmed[:2000]})
            chan.send(out)

    except Exception as e:
        if DEBUG: print(f"Error: {e}")
    finally:
        try: chan.close()
        except Exception: pass
        transport.close()

def _signal_handler(sig, frame):
    print("\n[!] Signal received, stopping the server...")
    STOP_EVENT.set()
    global LISTEN_SOCK
    if LISTEN_SOCK:
        try: LISTEN_SOCK.close()
        except Exception: pass

def start_server():
    global LISTEN_SOCK
    LISTEN_SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    LISTEN_SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    LISTEN_SOCK.bind((HOST, PORT))
    LISTEN_SOCK.listen(100)
    LISTEN_SOCK.settimeout(1.0)
    print(f"Fake SSH server started on {HOST}:{PORT} (Ctrl+C to stop)")
    try:
        while not STOP_EVENT.is_set():
            try:
                client, addr = LISTEN_SOCK.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            client_ip = addr[0]
            print(f"[+] Connection from {addr}")
            t = threading.Thread(target=handle_client, args=(client, client_ip), daemon=True)
            t.start()
    finally:
        try: LISTEN_SOCK.close()
        except Exception: pass
        print("[*] Server stopped.")

if __name__ == "__main__":
    import signal as _signal
    _signal.signal(_signal.SIGINT, _signal_handler)
    try: _signal.signal(_signal.SIGTERM, _signal_handler)
    except Exception: pass
    start_server()
