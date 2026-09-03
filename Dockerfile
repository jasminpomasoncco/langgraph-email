# syntax=docker/dockerfile:1

FROM python:3.11-slim

# uv: fast, reproducible installs from uv.lock
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    # Cloud Run's filesystem is read-only except /tmp
    CHROMA_PERSIST_DIR=/tmp/chroma_db \
    # Gmail creds come from Secret Manager files mounted via --set-secrets
    GMAIL_ALLOW_INTERACTIVE_AUTH=false \
    GMAIL_CREDENTIALS_FILE=/secrets/credentials.json \
    GMAIL_TOKEN_FILE=/secrets/token.json

WORKDIR /app

# 1) Dependencies only - cached unless pyproject.toml / uv.lock change
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 2) Project source + install the package itself
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 8080

# Cloud Run injects $PORT (defaults to 8080); fall back to 8080 for local runs
CMD ["sh", "-c", "uvicorn langgraph_gmail.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
