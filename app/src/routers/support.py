from datetime import UTC, datetime
from fastapi import Depends, HTTPException, Query, APIRouter
from src.models import Support
from src.db import get_async_session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schema.support import SupportCreate, SupportUpdate

router = APIRouter()


@router.post("", response_model=dict)
async def save_msg(
    data: SupportCreate,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    model = Support(**data.model_dump(), created_at=datetime.now(UTC))
    session.add(model)
    await session.commit()
    return model.model_dump(mode="json")


@router.put("", response_model=dict)
async def update_msg(
    data: SupportUpdate,
    id: int = Query(description="Support id"),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    model_raw = await session.exec(select(Support).where(Support.id == id))
    model = model_raw.one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Not found")
    model.answer = data.answer
    model.answered_at = datetime.now(UTC)
    session.add(model)
    await session.commit()
    return model.model_dump(mode="json")
