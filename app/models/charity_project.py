from sqlalchemy import CheckConstraint, Column, Integer, String

from app.core.base import BaseModel


NAME_MIN_LENGTH = 5
NAME_MAX_LENGTH = 100
DESCRIPTION_MIN_LENGTH = 10
FULL_AMOUNT_MIN = 1


class CharityProject(BaseModel):
    """Модель целевого проекта."""

    __tablename__ = "charityproject"

    name = Column(String(NAME_MAX_LENGTH), unique=True, nullable=False)
    description = Column(String, nullable=False)
    full_amount = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            f'LENGTH(name) BETWEEN {NAME_MIN_LENGTH} AND {NAME_MAX_LENGTH}',
            name='check_name_length'
        ),
        CheckConstraint(
            f'LENGTH(description) >= {DESCRIPTION_MIN_LENGTH}',
            name='check_description_length'
        ),
        CheckConstraint(
            f'full_amount > {FULL_AMOUNT_MIN - 1}',
            name='check_full_amount_positive'
        ),
    )
