import logging
from collections.abc import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .json import json

from config.settings import settings

DATABASE_URL = str(settings.ASYNC_DATABASE_URL)

logger = logging.getLogger(__name__)
engine = AsyncEngine(
    create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        json_serializer=json.dumps,
        json_deserializer=json.loads,
        pool_size=30,
        pool_timeout=10,
    )
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=True,
)  # type: ignore


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    except SQLAlchemyError as e:
        logger.error(f"DB Error {str(e)}")
        raise HTTPException(
            status_code=500, detail={"code": 500, "msg": "DB error", "detail": str(e)}
        ) from e


async def get_async_session_t() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker.begin() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    except SQLAlchemyError as e:
        logger.error(f"DB Error t {str(e)}")
        raise HTTPException(
            status_code=500, detail={"code": 500, "msg": "DB error t", "detail": str(e)}
        ) from e
