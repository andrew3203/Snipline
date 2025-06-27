from fastapi import APIRouter, Depends
from pydantic import BaseModel, model_validator
from datetime import datetime, UTC
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import get_async_session
from src.models.referral import Referral

router = APIRouter(prefix="/referral")


class ReferralCreateRequest(BaseModel):
    referrer_id: int
    referred_id: int | None = None
    source: str | None = None

    @model_validator(mode="after")
    def validate_referral_target(cls, values):
        if not values.get("referred_id") and not values.get("source"):
            raise ValueError("Either 'referred_id' or 'source' must be provided.")
        return values


@router.post("", response_model=Referral)
async def create_referral(
    payload: ReferralCreateRequest,
    session: AsyncSession = Depends(get_async_session),
):
    # Optional: validate that referrer/referred users exist in DB
    # Example: await session.get(User, payload.referrer_id)

    referral = Referral(
        referrer_id=payload.referrer_id,
        referred_id=payload.referred_id,
        source=payload.source,
        created_at=datetime.now(UTC),
        is_paid=False,
    )

    session.add(referral)
    await session.commit()
    await session.refresh(referral)

    return referral
