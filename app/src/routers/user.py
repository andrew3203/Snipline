from datetime import UTC, datetime
from fastapi import Depends, APIRouter, Query, HTTPException
from src.models import User
from src.models.filters import UserFilter
from src.db import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, col
from src.models.referral import Referral
from src.models.subscription import UserSubscription
from src.schema.user import UserCreateModel

router = APIRouter()


@router.post("", response_model=dict)
async def create_user(
    data: UserCreateModel,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    model = User(
        **data.model_dump(),
        created_at=datetime.now(UTC),
        active_at=datetime.now(UTC),
    )
    session.add(model)
    await session.commit()
    return model.model_dump(mode="json")


@router.get("", response_model=dict)
async def get_user_info(
    user_id: int = Query(description="User id"),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(detail="User not found", status_code=404)
    filter_raw = await session.exec(
        select(UserFilter).where(UserFilter.user_id == user_id)
    )
    subsriptions_raw = await session.exec(
        select(UserSubscription).where(
            and_(
                UserSubscription.user_id == user_id,
                col(UserSubscription.is_active).is_(True),
            )
        )
    )
    subsription = subsriptions_raw.first()
    query = select(
        func.count(Referral.referred_id).label("total_referred"),
        func.count().filter(Referral.is_paid).label("paid_referred"),
    ).where(Referral.referrer_id == user_id)

    result = await session.exec(query)
    total_referred, paid_referred = result.one()
    return {
        "user": user.model_dump(mode="json"),
        "filters": [f.model_dump(mode="json") for f in filter_raw.all()],
        "subsriptions": subsription.model_dump(mode="json") if subsription else {},
        "referral": {
            "total_referred": total_referred,
            "paid_referred": paid_referred,
        },
    }
