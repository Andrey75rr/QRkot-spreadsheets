from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud import donation_crud
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import process_investments

router = APIRouter(prefix="/donation", tags=["donations"])


@router.get("/", response_model=list[DonationFullInfoDB])
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_superuser),
):
    """Получить список всех пожертвований. Только для суперпользователей."""
    return await donation_crud.get_all(session)


@router.post("/", response_model=DonationDB, response_model_exclude_none=True)
async def create_donation(
    donation_data: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Создать новое пожертвование. Только для авторизованных пользователей."""
    new_donation = await donation_crud.create_donation(
        donation_data, user.id, session
    )
    await process_investments(session)
    return new_donation


@router.get(
    "/my",
    response_model=list[DonationDB],
    response_model_exclude_none=True
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Получить список своих пожертвований. Для авториз. пользователей."""
    return await donation_crud.get_user_donations(user.id, session)
