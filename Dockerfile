FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ssh_ai_honeypot ./ssh_ai_honeypot
COPY run.py README.md .env.example .env .gitignore docker-compose.yml ./
RUN mkdir -p logs && touch logs/.gitkeep

EXPOSE 2222
CMD ["python", "-m", "ssh_ai_honeypot.server"]
