# SSH AI Honeypot

Honeypot SSH with local emulation, optional AI-generated output, logging, arrow-history, access-after-attempts, per-IP rate limit, and temporary IP ban.

## Quick
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m ssh_ai_honeypot.server
```

## Docker
```bash
docker build -t ssh-ai-honeypot:latest .
docker compose up -d
```

## Env
See `.env.example` for all variables.
