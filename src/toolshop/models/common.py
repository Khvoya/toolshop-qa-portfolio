from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class ErrorResponse(ApiModel):
    message: str | None = None
    error: str | None = None


class Page[ItemT](ApiModel):
    current_page: int = Field(ge=1)
    data: list[ItemT]
    last_page: int = Field(ge=1)
    per_page: int = Field(ge=1)
    total: int = Field(ge=0)
