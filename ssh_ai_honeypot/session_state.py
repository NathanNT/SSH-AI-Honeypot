import os
from typing import Optional, Dict, Any, List

class SessionState:
    def __init__(self, username: str = "user"):
        self.username = username
        self.cwd = f"/home/{username}"
        self.fs: Dict[str, Dict[str, Any]] = {
            "/": {"type": "dir"},
            "/home": {"type": "dir"},
            self.cwd: {"type": "dir"},
            "/etc": {"type": "dir"},
            "/etc/hostname": {"type": "file", "content": "honeypot\n", "mode": "0644"},
            "/etc/os-release": {"type": "file", "content": 'NAME="Debian GNU/Linux"\nVERSION="12 (bookworm)"\n', "mode": "0644"},
        }
        self.installed = {"bash","sh","python","nano","vi","vim","ls","cd","pwd","cat",
                          "chmod","rm","mkdir","touch","echo","wget","curl","tar","unzip"}
        self.history: List[Dict[str, str]] = []

    def _norm(self, path: str) -> str:
        if not path.startswith("/"):
            path = os.path.normpath(os.path.join(self.cwd, path))
        return path.replace("\\","/")

    def exists(self, p: str) -> bool:
        return self._norm(p) in self.fs

    def is_dir(self, p: str) -> bool:
        return self.fs.get(self._norm(p), {}).get("type") == "dir"

    def is_file(self, p: str) -> bool:
        return self.fs.get(self._norm(p), {}).get("type") == "file"

    def ls(self, path: str) -> list[str]:
        path = self._norm(path)
        if not self.is_dir(path):
            return []
        pref = path if path.endswith("/") else path + "/"
        names = []
        for p in self.fs:
            if p.startswith(pref) and p != path:
                name = p[len(pref):].split("/")[0]
                if name and name not in names:
                    names.append(name)
        return sorted(names)

    def mkdir_p(self, path: str):
        path = self._norm(path)
        parts = [p for p in path.split("/") if p]
        cur = ""
        for part in parts:
            cur += "/" + part
            if cur not in self.fs:
                self.fs[cur] = {"type":"dir"}

    def write_file(self, path: str, content: str, mode="0644"):
        path = self._norm(path)
        parent = os.path.dirname(path)
        self.mkdir_p(parent)
        self.fs[path] = {"type":"file","content":content, "mode":mode}

    def read_file(self, path: str) -> Optional[str]:
        path = self._norm(path)
        if self.is_file(path):
            return self.fs[path]["content"]
        return None

    def rm(self, path: str):
        path = self._norm(path)
        if self.is_file(path):
            del self.fs[path]

    def chmod_exec(self, path: str):
        path = self._norm(path)
        if self.is_file(path):
            self.fs[path]["mode"] = "0755"

    def state_prompt(self) -> str:
        files_here = " ".join(self.ls(self.cwd)) or "(empty)"
        return (
            f"user={self.username} cwd={self.cwd}\n"
            f"installed={','.join(sorted(self.installed))}\n"
            f"ls(cwd)={files_here}\n"
            f"history(last 5)={[h['cmd'] for h in self.history[-5:]]}"
        )
