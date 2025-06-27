import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from config.settings import app_configs, settings
from src.domain.exceptions import BaseException
from src.domain.shema.base import ExceptionData
from src.domain.utils.json import json
from src.repository.db import AsyncQdrantService
from src.routers import router

logging.config.fileConfig(settings.logging_path, disable_existing_loggers=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = AsyncQdrantService()
    await service.ensure_collection()
    yield


app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan, **app_configs)

json.set_fastapi_json()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origins_regex_list,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.cors_headers_list,
)


@app.exception_handler(BaseException)
async def core_error_handler(request: Request, exc: BaseException) -> ORJSONResponse:
    if exc.code == status.HTTP_400_BAD_REQUEST:
        detail = "Произошел некорректный запрос. Попробуйте заново."
    elif exc.code == status.HTTP_403_FORBIDDEN:
        detail = "У вас нет доступа к ресурсу."
    elif exc.code == status.HTTP_404_NOT_FOUND:
        detail = "Обьект не найден."
    else:
        detail = f"Произошла внутренняя ошибка. Код: {exc.code}."

    model = ExceptionData(code=exc.code, msg=exc.msg, detail=detail, data=exc.data)
    return ORJSONResponse(status_code=model.code, content=model.model_dump())


app.include_router(router)
