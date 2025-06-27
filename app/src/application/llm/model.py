from pydantic import BaseModel, Field


class LLMResp(BaseModel):
    category: str = Field(description="category")
    subcategories: list[str] = Field(description="subcategories")
    summary: str = Field(description="summary")
    importance: int = Field(description="importance")
    companies: list[str] = Field(description="companies", default=[])
    locations: list[str] = Field(description="locations", default=[])
    names: list[str] = Field(description="names", default=[])
