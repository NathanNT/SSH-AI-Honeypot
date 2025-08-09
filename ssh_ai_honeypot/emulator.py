import os, re, shlex, time
from .session_state import SessionState

def emulate_locally(cmd: str, st: SessionState):
    try:
        args = shlex.split(cmd)
    except Exception:
        return None
    if not args:
        return "\r\n"

    if args[0] == "cd":
        target = args[1] if len(args) > 1 else f"/home/{st.username}"
        target = st._norm(target)
        if st.is_dir(target):
            st.cwd = target
            return ""
        else:
            return f"bash: cd: {args[1] if len(args)>1 else ''}: No such file or directory\r\n"

    if args[0] == "pwd":
        return st.cwd + "\r\n"

    if args[0] == "ls":
        path = st.cwd if len(args)==1 else args[-1]
        if path.startswith("-"):
            path = st.cwd
        items = st.ls(path)
        if not items:
            return ""
        return "  ".join(items) + "\r\n"

    if args[0] == "cat" and len(args) >= 2:
        out = []
        for p in args[1:]:
            content = st.read_file(p)
            if content is None:
                out.append(f"cat: {p}: No such file or directory")
            else:
                out.append(content.rstrip("\n"))
        return ("\r\n".join(out) + "\r\n") if out else ""

    if args[0] == "touch" and len(args) >= 2:
        for p in args[1:]:
            if st.exists(p):
                continue
            st.write_file(p, "")
        return ""

    if args[0] == "mkdir" and len(args) >= 2:
        targets = [a for a in args[1:] if not a.startswith("-")]
        for d in targets:
            st.mkdir_p(d)
        return ""

    if args[0] == "rm" and len(args) >= 2:
        for p in args[1:]:
            st.rm(p)
        return ""

    if args[0] == "chmod" and len(args) >= 3 and ("+x" in args[1] or "755" in args[1]):
        for p in args[2:]:
            st.chmod_exec(p)
        return ""

    if args[0] == "echo" and ">" in cmd:
        m = re.search(r"echo\s+(.*)\s*>\s*(\S+)", cmd, re.DOTALL)
        if m:
            data, path = m.group(1), m.group(2)
            data = data.strip().strip("'").strip('\"')
            st.write_file(path, data + "\n")
            return ""
        return ""

    if args[0] == "wget" and len(args) >= 2:
        url = args[-1]
        filename = os.path.basename(url) or "index.html"
        if "?" in filename:
            filename = filename.split("?")[0] or "index.html"
        fullpath = st._norm(filename)
        size = 15360
        st.write_file(fullpath, f"FAKE_CONTENT from {url}\n", "0644")
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        out = (
            f"--{now}--  {url}\n"
            f"Resolving {url.split('/')[2]}... 127.0.0.1\n"
            f"Connecting to {url.split('/')[2]}|127.0.0.1|:443... connected.\n"
            "HTTP request sent, awaiting response... 200 OK\n"
            f"Length: {size} (15K) [application/octet-stream]\n"
            f"Saving to: ‘{filename}’\n\n"
            f"{filename}        100%[{size}/{size}]   1.2M/s   in 0.01s\n\n"
            f"{now} (1.2 MB/s) - ‘{filename}’ saved [{size}/{size}]\n"
        )
        return out.replace("\n", "\r\n")

    if args[0] == "curl" and len(args) >= 2:
        url = args[-1]
        out_file = None
        if "-o" in args:
            try:
                out_file = args[args.index("-o") + 1]
            except Exception:
                pass
        elif "-O" in args:
            out_file = os.path.basename(url) or "index.html"

        if out_file:
            st.write_file(out_file, f"FAKE_CONTENT from {url}\n", "0644")
            return ""

        html = "<!doctype html><html><head><title>OK</title></head><body>hello</body></html>\n"
        return html.replace("\n", "\r\n")

    return None
