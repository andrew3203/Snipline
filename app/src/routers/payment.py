from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, UTC

from src.db import get_async_session
from src.models import Payment, PaymentMethod, SubscriptionPlan
from pydantic import BaseModel
from src.repository.yookassa import YooKassaClient

router = APIRouter()


class CreatePaymentRequest(BaseModel):
    user_id: int
    subscription_plan_id: int
    payment_method_id: int
    currency: str = "RUB"


@router.post("/create")
async def create_payment(
    payload: CreatePaymentRequest,
    session: AsyncSession = Depends(get_async_session),
):
    plan = await session.get(SubscriptionPlan, payload.subscription_plan_id)
    method = await session.get(PaymentMethod, payload.payment_method_id)
    if not plan or not method:
        raise HTTPException(
            status_code=404, detail="Invalid subscription plan or payment method"
        )

    yookassa = YooKassaClient()
    payment_data = await yookassa.create_payment(
        user_id=payload.user_id,
        subscription_plan_id=payload.subscription_plan_id,
        plan_name=plan.name,
        price_usd=plan.price_usd,
        currency=payload.currency,
    )

    payment = Payment(
        user_id=payload.user_id,
        amount_usd=plan.price_usd,
        method_id=payload.payment_method_id,
        is_confirmed=False,
        details=payment_data,
        created_at=datetime.now(UTC),
    )

    session.add(payment)
    await session.commit()
    await session.refresh(payment)

    return {
        "payment_id": payment.id,
        "confirmation_url": payment_data["confirmation"]["confirmation_url"],
    }
