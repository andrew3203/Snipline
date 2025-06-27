from pydantic import BaseModel, Field


class SupportCreate(BaseModel):
    user_id: int = Field(description="User who asked the question")
    question: str = Field(description="User's question")


class SupportUpdate(BaseModel):
    answer: str = Field(description="Answer provided by")
