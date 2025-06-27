FROM python:3.11.6-slim-bullseye as python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get -y upgrade && apt-get install --no-install-recommends -y build-essential libpq-dev libpq5

COPY pyproject.toml uv.lock* ./

ENV UV_SYSTEM_PYTHON=1
RUN UV_COMPILE_BYTECODE=1 uv sync --frozen --no-editable --no-install-project

WORKDIR /app

RUN addgroup --system fastapi \
    && adduser --system --ingroup fastapi fastapi

COPY . .

RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/*

COPY . .
