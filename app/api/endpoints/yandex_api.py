from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.core.yandex_client import YandexDiskClient, get_yandex_client
from app.crud import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
    summary="Создать Excel-отчёт на Яндекс Диске",
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        yandex_client: YandexDiskClient = Depends(get_yandex_client),
) -> str:
    """Создаёт Excel-отчёт по закрытым проектам и загружает на Яндекс Диск."""
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )

    if not projects:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Нет закрытых проектов для формирования отчёта"
        )

    try:
        return await create_simple_report(projects, yandex_client)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании отчёта: {str(e)}"
        )
