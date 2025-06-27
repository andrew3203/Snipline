"""
Gunicorn config.
Base on:
https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/docker-images/gunicorn_conf.py
"""

import multiprocessing
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings


class GunicornConfig(BaseSettings):
    """GunicornConfig"""

    HOST: str = "0.0.0.0"
    PORT: str = "8000"
    GUNICORN_BIND: str | None = None
    GUNICORN_WORKERS_PER_CORE: int = 1
    GUNICORN_MAX_WORKERS: int = 1
    GUNICORN_WEB_CONCURRENCY: Annotated[int, Field(strict=True, gt=-1)] = 0
    GUNICORN_GRACEFUL_TIMEOUT: int = 120
    GUNICORN_TIMEOUT: int = 60
    GUNICORN_KEEP_ALIVE: int = 10
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = Field(default=True)

    @property
    def logging_path(self) -> str:
        return "logging.ini" if self.DEBUG else "logging_production.ini"


gunicor_settings = GunicornConfig()


host = gunicor_settings.HOST
port = gunicor_settings.PORT
bind_env = gunicor_settings.GUNICORN_BIND

bind = bind_env if bind_env else f"{host}:{port}"

workers_per_core = gunicor_settings.GUNICORN_WORKERS_PER_CORE
max_workers = gunicor_settings.GUNICORN_MAX_WORKERS
web_concurrency = gunicor_settings.GUNICORN_WEB_CONCURRENCY

cores = multiprocessing.cpu_count()
default_web_concurrency = workers_per_core * cores + 1

web_concurrency = min(max(int(default_web_concurrency), 2), max_workers)

graceful_timeout = gunicor_settings.GUNICORN_GRACEFUL_TIMEOUT
timeout = gunicor_settings.GUNICORN_TIMEOUT
keepalive = gunicor_settings.GUNICORN_KEEP_ALIVE
use_loglevel = gunicor_settings.LOG_LEVEL

loglevel = use_loglevel
workers = web_concurrency
worker_tmp_dir = "/dev/shm"
logconfig = gunicor_settings.logging_path
