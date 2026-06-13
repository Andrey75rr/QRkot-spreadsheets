from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationCreate(BaseModel):
    """Схема для создания пожертвования."""

    model_config = ConfigDict(extra='forbid')
    full_amount: int = Field(..., gt=0)
    comment: str = ""


class DonationDB(BaseModel):
    """Схема пожертвования для обычного пользователя."""

    id: int
    full_amount: int
    comment: Optional[str] = None
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    """Схема пожертвования с полной информацией (только для суперполь.)."""

    user_id: int
    invested_amount: int = 0
    fully_invested: bool = False
    close_date: Optional[datetime] = None
