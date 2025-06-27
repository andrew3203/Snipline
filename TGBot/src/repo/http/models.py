from pydantic import BaseModel
from datetime import datetime
from typing import Any, Literal


# -------------------------------
# User
# -------------------------------
class UserInfo(BaseModel):
    id: int
    username: str | None = None
    name: str | None = None
    lang: str
    location: str | None = None
    tz: str | None
    is_active: bool
    current_plan_id: int | None = None
    created_at: datetime
    active_at: datetime


class UserFilterItem(BaseModel):
    id: int
    user_id: int
    name: str
    filters: dict[str, int | str | list | None]


class ReferralInfo(BaseModel):
    total_referred: int
    paid_referred: int
    bonus_months: int = 0


class SubscriptionInfo(BaseModel):
    id: int
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    promo_offer_id: int | None = None
    payment_id: int | None = None


class FullUserResponse(BaseModel):
    user: UserInfo
    filters: list[UserFilterItem]
    subsriptions: SubscriptionInfo | dict  # dict → если subsription = None
    referral: ReferralInfo

# -------------------------------
# Filter
# -------------------------------

class UserFilterResponse(BaseModel):
    id: int
    user_id: int
    name: str
    filters: dict[str, Any]


# -------------------------------
# Support
# -------------------------------

class SupportResponse(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str | None = None


# -------------------------------
# Referral
# -------------------------------

class ReferralResponse(BaseModel):
    id: int
    referrer_id: int | None = None
    referred_id: int | None = None
    source: str | None = None
    created_at: datetime
    is_paid: bool


# -------------------------------
# Subscription
# -------------------------------

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    payment_id: int | None = None
    promo_offer_id: int | None = None


class SubscriptionPlanResponse(BaseModel):
    id: int
    name: str
    price: float
    currency: str
    description: str | None = None


# -------------------------------
# Payment
# -------------------------------

class CreatePaymentResponse(BaseModel):
    payment_id: int | str | None = None
    status: Literal["pending", "completed", "failed"] | str | None = None
    additional_info: dict[str, Any] | None = None
