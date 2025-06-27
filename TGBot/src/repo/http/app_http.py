from .http import HttpRepo
from .models import (
    FullUserResponse,
    UserFilterResponse,
    SupportResponse,
    ReferralResponse,
    CreatePaymentResponse,
    SubscriptionResponse,
    SubscriptionPlanResponse,
)


class AppHttpRepo(HttpRepo):
    def __init__(self):
        self.url = "http://app:8000"
        self.headers = {"Content-Type": "application/json"}

    # --- User ---
    async def create_user(
        self,
        id: int,
        lang: str,
        username: str | None = None,
        name: str | None = None,
        location: str | None = None,
        tz: str | None = None,
        is_active: bool = True,
        **kwargs,
    ) -> dict:
        data = {
            "id": id,
            "lang": lang,
            "username": username,
            "name": name,
            "location": location,
            "tz": tz,
            "is_active": is_active,
        }
        response = await self.post(
            headers=self.headers, url=f"{self.url}/user", data=data, **kwargs
        )
        return response

    async def get_user(self, user_id: int, **kwargs) -> FullUserResponse:
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/user?user_id={user_id}",
            **kwargs,
        )
        return FullUserResponse.model_validate(response)

    # --- Report ---
    async def get_news_count(
        self,
        user_id: int,
        filter_id: int,
        date_from: str | None = None,
        **kwargs,
    ) -> int:
        params = {"user_id": user_id, "filter_id": filter_id}
        if date_from:
            params["date_from"] = date_from
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/report/news-count",
            params=params,
            **kwargs,
        )
        return response

    async def get_news_report(
        self,
        user_id: int,
        filter_id: int,
        answer_lang: str,
        date_from: str | None = None,
        **kwargs,
    ) -> str:
        params = {
            "user_id": user_id,
            "filter_id": filter_id,
            "answer_lang": answer_lang,
        }
        if date_from:
            params["date_from"] = date_from
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/report/report",
            params=params,
            **kwargs,
        )
        return response

    async def get_news_question(
        self,
        user_id: int,
        question: str,
        filter_id: int,
        answer_lang: str,
        date_from: str | None = None,
        **kwargs,
    ) -> str:
        params = {
            "user_id": user_id,
            "question": question,
            "filter_id": filter_id,
            "answer_lang": answer_lang,
        }
        if date_from:
            params["date_from"] = date_from
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/report/question",
            params=params,
            **kwargs,
        )
        return response

    async def get_news_rag_question(
        self,
        user_id: int,
        question: str,
        answer_lang: str,
        **kwargs,
    ) -> str:
        params = {
            "user_id": user_id,
            "question": question,
            "answer_lang": answer_lang,
        }
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/report/question/rag",
            params=params,
            **kwargs,
        )
        return response

    # --- Filter ---
    async def create_filter(
        self,
        user_id: int,
        name: str,
        filters: dict,
        **kwargs,
    ) -> UserFilterResponse:
        data = {
            "user_id": user_id,
            "name": name,
            "filters": filters,
        }
        response = await self.post(
            headers=self.headers,
            url=f"{self.url}/filter",
            data=data,
            **kwargs,
        )
        return UserFilterResponse.model_validate(response)

    # --- Support ---
    async def send_support_msg(
        self,
        user_id: int,
        question: str,
        **kwargs,
    ) -> SupportResponse:
        data = {"user_id": user_id, "question": question}
        response = await self.post(
            headers=self.headers,
            url=f"{self.url}/support",
            data=data,
            **kwargs,
        )
        return SupportResponse.model_validate(response)

    async def update_support_msg(
        self,
        support_id: int,
        answer: str,
        **kwargs,
    ) -> SupportResponse:
        data = {"answer": answer}
        response = await self.put(
            headers=self.headers,
            url=f"{self.url}/support?id={support_id}",
            data=data,
            **kwargs,
        )
        return SupportResponse.model_validate(response)

    # --- Referral ---
    async def create_referral(
        self,
        referrer_id: int,
        referred_id: int | None = None,
        source: str | None = None,
        **kwargs,
    ) -> ReferralResponse:
        data = {
            "referrer_id": referrer_id,
            "referred_id": referred_id,
            "source": source,
        }
        response = await self.post(
            headers=self.headers,
            url=f"{self.url}/referral/referral",
            data=data,
            **kwargs,
        )
        return ReferralResponse.model_validate(response)

    # --- Payment ---
    async def create_payment(
        self,
        user_id: int,
        subscription_plan_id: int,
        payment_method_id: int,
        currency: str = "RUB",
        **kwargs,
    ) -> CreatePaymentResponse:
        data = {
            "user_id": user_id,
            "subscription_plan_id": subscription_plan_id,
            "payment_method_id": payment_method_id,
            "currency": currency,
        }
        response = await self.post(
            headers=self.headers,
            url=f"{self.url}/payment/create",
            data=data,
            **kwargs,
        )
        return CreatePaymentResponse.model_validate(response)

    # --- Subscription ---
    async def get_subscription(self, user_id: int, **kwargs) -> SubscriptionResponse:
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/subscription",
            params={"user_id": user_id},
            **kwargs,
        )
        return SubscriptionResponse.model_validate(response)

    async def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        payment_id: int | None,
        promo_offer_id: int | None = None,
        **kwargs,
    ) -> SubscriptionResponse:
        data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "payment_id": payment_id,
            "promo_offer_id": promo_offer_id,
        }
        response = await self.post(
            headers=self.headers,
            url=f"{self.url}/subscription",
            data=data,
            **kwargs,
        )
        return SubscriptionResponse.model_validate(response)

    async def get_subscription_plans(self, **kwargs) -> list[SubscriptionPlanResponse]:
        response = await self.get(
            headers=self.headers,
            url=f"{self.url}/subscription/list",
            **kwargs,
        )
        return [SubscriptionPlanResponse.model_validate(plan) for plan in response]
