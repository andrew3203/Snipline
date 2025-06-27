from fastapi import Request, APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta, UTC
from sqlmodel import select, and_

from src.db import get_async_session
from src.models import (
    Payment,
    SubscriptionPlan,
    UserSubscription,
    Referral,
    ReferralReward,
    UserReferralReward,
)

router = APIRouter()


@router.post("/webhook/yookassa")
async def handle_yookassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    payload = await request.json()
    event_type = payload.get("event")
    payment_id = payload.get("object", {}).get("id")

    if not payment_id or not event_type:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    # Найдём наш Payment по details->id
    result = await session.exec(
        select(Payment).where(Payment.details["id"].as_string() == payment_id)
    )
    payment = result.first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if event_type == "payment.succeeded":
        payment.is_confirmed = True
        await session.commit()
        await session.refresh(payment)

        user_id = payment.user_id
        plan_id = payment.details["metadata"]["subscription_plan_id"]
        plan = await session.get(SubscriptionPlan, plan_id)

        now = datetime.now(UTC)
        end = now + timedelta(days=plan.days_duration)

        # Создаём подписку
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=now,
            end_date=end,
            is_active=True,
            payment_id=payment.id,
        )
        session.add(subscription)

        # Проверяем, был ли он приглашён
        referral_result = await session.exec(
            select(Referral).where(
                and_(Referral.referred_id == user_id, Referral.is_paid.is_(False))
            )
        )
        referral = referral_result.first()
        if referral:
            referral.is_paid = True
            await session.commit()
            await session.refresh(referral)

            # Считаем, сколько платящих людей у пригласившего
            count_result = await session.exec(
                select(Referral).where(
                    and_(
                        Referral.referrer_id == referral.referrer_id,
                        Referral.is_paid.is_(True),
                    )
                )
            )
            paid_referrals = count_result.all()
            paid_count = len(paid_referrals)

            # Проверяем наличие награды
            reward_result = await session.exec(
                select(ReferralReward).where(ReferralReward.referal_count <= paid_count)
            )
            rewards = reward_result.all()
            if rewards:
                # Берём максимальную подходящую награду
                reward = max(rewards, key=lambda r: r.referal_count)

                # Проверяем, выдавалась ли уже такая награда этому пользователю
                existing = await session.exec(
                    select(UserReferralReward).where(
                        and_(
                            UserReferralReward.user_id == referral.referrer_id,
                            UserReferralReward.reward_id == reward.id,
                        )
                    )
                )
                if not existing.first():
                    # Выдаём награду
                    new_reward = UserReferralReward(
                        user_id=referral.referrer_id,
                        reward_id=reward.id,
                        created_at=datetime.now(UTC),
                    )
                    session.add(new_reward)
                    print(
                        f"✅ Referrer {referral.referrer_id} получил награду {reward.reward_plan_id}"
                    )
                    await session.commit()

    elif event_type == "payment.canceled":
        # Можно логировать отмену
        print(f"❌ Платёж {payment_id} был отменён")

    return {"status": "ok"}
