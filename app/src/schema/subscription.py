from pydantic import BaseModel, Field


class UserSubscriptionCreateModel(BaseModel):
    user_id: int = Field(description="User ID")
    plan_id: int = Field(description="Subscribed plan ID")
    promo_offer_id: int | None = Field(
        default=None, foreign_key="promo_offer.id", description="Applied promo offer ID"
    )
    payment_id: int | None = Field(
        foreign_key="payment.id", description="Associated payment ID"
    )
