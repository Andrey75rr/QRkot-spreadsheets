from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


NAME_MIN_LENGTH = 5
NAME_MAX_LENGTH = 100
DESCRIPTION_MIN_LENGTH = 10


class CharityProjectCreate(BaseModel):
    """Схема для создания проекта."""

    model_config = ConfigDict(extra='forbid')
    name: str = Field(
        ...,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    description: str = Field(..., min_length=DESCRIPTION_MIN_LENGTH)
    full_amount: int = Field(..., gt=0)


class CharityProjectUpdate(BaseModel):
    """Схема для обновления проекта."""

    model_config = ConfigDict(extra='forbid')
    name: Optional[str] = Field(
        None,
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH
    )
    description: Optional[str] = Field(None, min_length=DESCRIPTION_MIN_LENGTH)
    full_amount: Optional[int] = Field(None, gt=0)


class CharityProjectDB(CharityProjectCreate):
    """Схема проекта из БД."""

    id: int
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: datetime
    close_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
