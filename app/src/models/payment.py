from sqlmodel import Field, SQLModel, Column, TEXT
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa
from datetime import datetime

from src.models.config import metadata


class Discount(SQLModel, metadata=metadata, table=True):
    __tablename__ = "discount"

    id: int = Field(
        primary_key=True, index=True, description="Unique ID of the discount"
    )
    type: str = Field(description="Type of discount: fixed or percent")
    value: float = Field(description="Discount value (fixed amount or percent)")
    name: str = Field(description="Label or description of the discount")


class PaymentMethod(SQLModel, metadata=metadata, table=True):
    __tablename__ = "payment_method"

    id: int = Field(primary_key=True, description="Unique ID of the payment method")
    type: str = Field(
        description="Type of payment method: telegram or crypto", index=True
    )
    name: str = Field(description="Name of the payment method")


class Payment(SQLModel, metadata=metadata, table=True):
    __tablename__ = "payment"

    id: int = Field(
        primary_key=True, index=True, description="Unique ID of the payment"
    )
    user_id: int = Field(
        foreign_key="user.id", index=True, description="User who made the payment"
    )
    amount_usd: float = Field(description="Amount paid in USD")
    method_id: int = Field(
        foreign_key="payment_method.id", index=True, description="Payment method used"
    )
    is_confirmed: bool = Field(description="Whether the payment is confirmed")
    details: dict = Field(
        sa_column=Column(postgresql.JSONB(astext_type=TEXT()), nullable=False),
        description="Additional payment details",
    )
    created_at: datetime = Field(
        description="Date and time of the payment",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
