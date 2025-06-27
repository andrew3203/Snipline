from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class Referral(SQLModel, metadata=metadata, table=True):
    __tablename__ = "referral"

    id: int = Field(primary_key=True, description="Unique ID of the referral")
    referrer_id: int | None = Field(
        default=None, foreign_key="user.id", index=True, description="Referring user ID"
    )
    referred_id: int | None = Field(
        default=None,
        foreign_key="user.id",
        index=True,
        description="Referred user ID (author)",
    )
    source: str | None = Field(default=None, description="Source name")
    created_at: datetime = Field(
        description="Date of referral",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    is_paid: bool = Field(description="Whether the referred user became a paying user")


class ReferralReward(SQLModel, metadata=metadata, table=True):
    __tablename__ = "referral_reward"

    id: int = Field(primary_key=True, description="Unique ID of the reward")
    referal_count: int = Field(description="Number of referrs")
    reward_plan_id: int = Field(
        foreign_key="subscription_plan.id", description="Rewarded subscription plan ID"
    )


class UserReferralReward(SQLModel, metadata=metadata, table=True):
    __tablename__ = "user_referral_reward"

    id: int = Field(primary_key=True, description="Unique ID of the reward")
    user_id: int = Field(foreign_key="user.id", description="User receiving the reward")
    reward_id: int = Field(
        foreign_key="referral_reward.id", description="Rewarded plan ID"
    )
    created_at: datetime = Field(
        description="Date reward was granted",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
