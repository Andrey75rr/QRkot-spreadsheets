from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation


class CRUDDonation(CRUDBase):
    """CRUD для операций с пожертвованиями."""

    async def get_open_donations(
        self,
        session: AsyncSession,
    ):
        """Получить открытые (не полностью распределённые) пожертвования."""
        result = await session.execute(
            select(Donation).where(
                Donation.fully_invested.is_(False)
            ).order_by(Donation.create_date)
        )
        return result.scalars().all()

    async def get_user_donations(
        self,
        user_id: int,
        session: AsyncSession,
    ):
        """Получить все пожертвования конкретного пользователя."""
        result = await session.execute(
            select(Donation).where(Donation.user_id == user_id)
        )
        return result.scalars().all()

    async def create_donation(self, donation_data, user_id, session):
        """Создать новое пожертвование и сохранить в БД."""
        data = donation_data.model_dump()
        data['comment'] = data.get('comment') or None
        new_donation = Donation(**data, user_id=user_id)
        session.add(new_donation)
        await session.commit()
        await session.refresh(new_donation)
        return new_donation


donation_crud = CRUDDonation(Donation)
