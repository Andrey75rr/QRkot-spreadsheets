from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    """CRUD для операций с благотворительными проектами."""

    async def get_by_name(
        self,
        name: str,
        session: AsyncSession,
    ):
        """Получить проект по названию."""
        result = await session.execute(
            select(CharityProject).where(CharityProject.name == name)
        )
        return result.scalar_one_or_none()

    async def get_open_projects(
        self,
        session: AsyncSession,
    ):
        """Получить открытые (не полностью инвестированные) проекты."""
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False)
            ).order_by(CharityProject.create_date)
        )
        return result.scalars().all()

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ):
        """Получить закрытые проекты, отсортированные по скорости сбора."""
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = result.scalars().all()
        return sorted(
            projects,
            key=lambda p: (p.close_date - p.create_date)
        )

    async def update_project(
        self,
        project: CharityProject,
        update_data: dict,
        session: AsyncSession,
    ) -> CharityProject:
        """Обновить поля проекта и сохранить изменения в БД."""
        if "full_amount" in update_data:
            project.full_amount = update_data.pop("full_amount")
            if project.invested_amount >= project.full_amount:
                project.fully_invested = True
                project.close_date = datetime.now()

        for key, value in update_data.items():
            setattr(project, key, value)

        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project


charity_project_crud = CRUDCharityProject(CharityProject)