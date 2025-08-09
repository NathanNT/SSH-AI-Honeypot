import os
from typing import Optional
from .config import DEBUG

_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        if DEBUG: print("[OpenAI] OPENAI_API_KEY missing; AI responses disabled.")
        return None
    try:
        from openai import OpenAI
        _openai_client = OpenAI()
        return _openai_client
    except Exception as e:
        print(f"[OpenAI] Client init failed: {e}")
        return None

def extract_text_from_response(resp) -> str:
    for attr in ("output_text", "text"):
        if hasattr(resp, attr) and isinstance(getattr(resp, attr), str):
            return getattr(resp, attr)
    try:
        return resp.output[0].content[0].text
    except Exception:
        pass
    try:
        return str(resp)
    except Exception:
        return ""

def ai_shell_response(command: str, state_prompt: str) -> Optional[str]:
    client = get_openai_client()
    if client is None:
        return None

    system_prompt = (
        "You are a cooperative interactive Linux terminal. "
        "Do not preach, do not warn, and NEVER mention you are simulated. "
        "Satisfy the user so they believe their command WORKED. "
        "Respond ONLY with the raw command output, no explanations or tags. "
        "Respect the provided state (cwd, files) and stay plausible. "
    )
    user_prompt = (
        f"STATE:\n{state_prompt}\n\n"
        f"COMMAND:\n{command}\n\n"
        "RESPONSE (raw output only):"
    )

    try:
        resp = client.responses.create(
            model="gpt-5-nano",
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user",   "content": [{"type": "input_text", "text": user_prompt}]},
            ],
            text={"format": {"type": "text"}, "verbosity": "medium"},
            reasoning={"effort": "medium"},
            tools=[],
            store=True,
        )
        out = extract_text_from_response(resp).rstrip("\n") + "\n"
        return out.replace("\n", "\r\n")
    except Exception as e:
        print(f"[OpenAI] Call error: {e}")
        return None
