from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class SubscriptionPlan(SQLModel, metadata=metadata, table=True):
    __tablename__ = "subscription_plan"

    id: int = Field(
        primary_key=True, index=True, description="Unique ID of the subscription plan"
    )
    price_usd: float = Field(description="Monthly price in USD")
    days_duration: int = Field(description="Duration of subscription in days")


class UserSubscription(SQLModel, metadata=metadata, table=True):
    __tablename__ = "user_subscription"

    id: int = Field(primary_key=True, description="Unique ID of the subscription")
    user_id: int = Field(foreign_key="user.id", description="User ID")
    plan_id: int = Field(
        foreign_key="subscription_plan.id", description="Subscribed plan ID"
    )
    start_date: datetime = Field(
        description="Start date of subscription",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    end_date: datetime = Field(
        description="End date of subscription",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    is_active: bool = Field(description="Whether the subscription is active")
    promo_offer_id: int | None = Field(
        default=None, foreign_key="promo_offer.id", description="Applied promo offer ID"
    )
    payment_id: int | None = Field(
        foreign_key="payment.id", description="Associated payment ID"
    )
