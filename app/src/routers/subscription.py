from datetime import UTC, datetime, timedelta
from fastapi import Depends, HTTPException, Query, APIRouter
from src.models import SubscriptionPlan, UserSubscription
from src.db import get_async_session
from sqlmodel import select, and_, col
from sqlmodel.ext.asyncio.session import AsyncSession
from src.schema.subscription import UserSubscriptionCreateModel

router = APIRouter()


@router.get("", response_model=dict)
async def get_supscription(
    user_id: int = Query(description="user id"),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    model_raw = await session.exec(
        select(UserSubscription).where(
            and_(
                UserSubscription.user_id == user_id,
                col(UserSubscription.is_active).is_(True),
            )
        )
    )
    model = model_raw.one_or_none()
    if not model:
        return {}
    return model.model_dump(mode="json")


@router.post("", response_model=dict)
async def create_supscription(
    data: UserSubscriptionCreateModel,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    model_raw = await session.exec(
        select(SubscriptionPlan).where(SubscriptionPlan.id == data.plan_id)
    )
    model = model_raw.one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Not found")

    item = UserSubscription(
        **data.model_dump(),
        start_date=datetime.now(UTC),
        end_date=datetime.now(UTC) + timedelta(days=model.days_duration),
        is_active=True,
    )
    session.add(item)
    await session.commit()
    return item.model_dump(mode="json")


@router.get("/list", response_model=list[dict])
async def subscription_plan_list(
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    model_raw = await session.exec(select(SubscriptionPlan))
    models = model_raw.all()
    if not models:
        raise HTTPException(status_code=404, detail="Not found")
    return [m.model_dump(mode="json") for m in models]
