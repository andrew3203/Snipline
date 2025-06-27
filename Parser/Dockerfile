FROM --platform=linux/amd64 python:3.11.6-slim-bookworm as python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    apt-transport-https \
    ca-certificates

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.84/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64


RUN apt-get update && apt-get install -y \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    libwebp-dev \
    tcl-dev tk-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем только pyproject.toml и uv.lock (если есть) — чтобы использовать кеш
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости (без установки самого проекта)
ENV UV_SYSTEM_PYTHON=1
RUN UV_COMPILE_BYTECODE=1 uv sync --frozen --no-editable --no-install-project


# Копируем остальной код
COPY . .

# Устанавливаем сам проект
RUN UV_COMPILE_BYTECODE=1 uv sync --frozen --no-editable

# Опционально: удаляем pycache и временные файлы
RUN find . -type d -name "__pycache__" -exec rm -r {} + || true
