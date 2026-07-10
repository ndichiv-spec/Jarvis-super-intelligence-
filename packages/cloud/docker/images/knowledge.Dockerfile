# syntax=docker/dockerfile:1
FROM python:3.13-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group knowledge

FROM base AS production

COPY --from=builder /app/.venv /app/.venv
COPY packages/knowledge/src /app/src
COPY packages/core/src /app/src/core

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8400

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8400/health || exit 1

CMD ["uvicorn", "jarvis_knowledge.app:app", "--host", "0.0.0.0", "--port", "8400"]
