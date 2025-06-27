from fastapi import FastAPI
from config.settings import settings
import logging.config
from src.routers import router

logging.config.fileConfig(settings.logging_path, disable_existing_loggers=False)


app = FastAPI()

app.include_router(router)
