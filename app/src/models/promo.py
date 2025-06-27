from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class PromoOfferRule(SQLModel, metadata=metadata, table=True):
    __tablename__ = "promo_offer_rule"

    id: int = Field(primary_key=True, description="Unique ID of the promo offer")
    discount_id: int = Field(foreign_key="discount.id", description="Discount ID")
    plan_id: int = Field(
        foreign_key="subscription_plan.id", description="User prev plan ID"
    )
    new_plan_id: int = Field(
        foreign_key="subscription_plan.id", description="New user plan ID"
    )
    minutes_duration: int = Field(description="Minutes duration of offer")
    expire_days: int = Field(description="Number of days after user plan expired")


class PromoOffer(SQLModel, metadata=metadata, table=True):
    __tablename__ = "promo_offer"

    id: int = Field(primary_key=True, description="Unique ID of the promo offer")
    user_id: int = Field(foreign_key="user.id", description="User receiving the offer")
    discount_id: int = Field(foreign_key="discount.id", description="Discount ID")
    plan_id: int = Field(
        foreign_key="subscription_plan.id", description="Current active plan ID"
    )
    expires_at: datetime = Field(
        description="Expiration date of the offer",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    is_used: bool = Field(description="Whether the offer was used")
    created_at: datetime = Field(
        description="Date the offer was created",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
