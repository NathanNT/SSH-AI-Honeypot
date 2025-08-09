import paramiko

ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"

def _clear_and_print(chan: paramiko.Channel, prompt: str, new_text: str, prev_len: int):
    chan.send("\r")
    chan.send(prompt + (" " * prev_len))
    chan.send("\r" + prompt)
    chan.send(new_text)

def read_line_interactive(chan: paramiko.Channel, prompt: str, history_items: list[str]) -> str:
    chan.send(prompt)
    buf_chars: list[str] = []
    hist_index = len(history_items)
    last_render_len = 0

    esc_stage = 0
    while True:
        try:
            data = chan.recv(1024)
        except Exception:
            return "__CONN_CLOSED__"
        if not data:
            return "__CONN_CLOSED__"

        text = data.decode("utf-8", errors="ignore")
        i = 0
        while i < len(text):
            ch = text[i]

            if esc_stage == 0 and ch == "\x1b":
                esc_stage = 1; i += 1; continue
            elif esc_stage == 1:
                if ch == "[":
                    esc_stage = 2
                else:
                    esc_stage = 0
                i += 1; continue
            elif esc_stage == 2:
                if ch == "A":
                    if hist_index > 0:
                        hist_index -= 1
                        replacement = history_items[hist_index]
                        prev_len = len(buf_chars)
                        buf_chars = list(replacement)
                        _clear_and_print(chan, prompt, replacement, prev_len)
                        last_render_len = len(replacement)
                elif ch == "B":
                    if hist_index < len(history_items):
                        hist_index += 1
                        replacement = history_items[hist_index] if hist_index < len(history_items) else ""
                        prev_len = len(buf_chars)
                        buf_chars = list(replacement)
                        _clear_and_print(chan, prompt, replacement, prev_len)
                        last_render_len = len(replacement)
                esc_stage = 0
                i += 1; continue

            if ch in ("\r", "\n"):
                chan.send("\r\n")
                return "".join(buf_chars)

            if ch in ("\x7f", "\b"):
                if buf_chars:
                    buf_chars.pop()
                    chan.send("\b \b")
                i += 1; continue

            if ch == "\x03":
                chan.send("^C\r\n")
                return "__CTRL_C__"

            if ch == "\x04":
                return "__CTRL_D__"

            buf_chars.append(ch)
            chan.send(ch)
            last_render_len = len(buf_chars)
            i += 1
