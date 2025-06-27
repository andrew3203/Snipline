import base64
from uuid import uuid4
from typing import Any


from src.repository.http import HttpRepo
from config.settings import settings


class YooKassaClient(HttpRepo):
    YOOKASSA_URL = "https://api.yookassa.ru/v3/payments"

    async def create_payment(
        self,
        user_id: int,
        subscription_plan_id: int,
        plan_name: str,
        price_usd: float,
        currency: str = "RUB",
    ) -> dict[str, Any]:
        credentials = f"{settings.YOOKASSA_SHOP_ID}:{settings.YOOKASSA_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {credentials}",
            "Idempotence-Key": str(uuid4()),
            "Content-Type": "application/json",
        }

        data = {
            "amount": {"value": f"{price_usd:.2f}", "currency": currency},
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YOOKASSA_RETURN_URL,
            },
            "description": f"Покупка подписки {plan_name}",
            "metadata": {
                "user_id": user_id,
                "subscription_plan_id": subscription_plan_id,
            },
        }

        return await self.post(
            headers=headers,
            url=self.YOOKASSA_URL,
            data=data,
        )
