from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.application.services.catogory import NewsCategoryService
from src.db import get_async_session
from src.models.filters import UserFilter


class FiltersSchema(BaseModel):
    category: int | None = None
    subcategories: list[int] | None = None
    companies: list[str] | None = None
    locations: list[str] | None = None
    names: list[str] | None = None
    priority: list[int] | None = None


class UserFilterCreateRequest(BaseModel):
    user_id: int
    name: str
    filters: FiltersSchema


router = APIRouter()


@router.post("", response_model=UserFilter)
async def create_user_filter(
    payload: UserFilterCreateRequest,
    session: AsyncSession = Depends(get_async_session),
):
    user_filter = UserFilter(
        user_id=payload.user_id,
        name=payload.name,
        filters=payload.filters.model_dump(exclude_none=True, mode="json"),
    )

    session.add(user_filter)
    await session.commit()
    await session.refresh(user_filter)

    return user_filter


@router.get("/categories", response_model=UserFilter)
async def get_categories(
    session: AsyncSession = Depends(get_async_session),
):
    service = NewsCategoryService()
    await service.on_load(session=session)
    await service.g


@router.get("/subcategories", response_model=UserFilter)
async def get_subcategories(
    payload: UserFilterCreateRequest,
    session: AsyncSession = Depends(get_async_session),
):
    pass
