from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_projects_by_completion_rate(
        self, session: AsyncSession
    ):
        projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = projects.scalars().all()
        return sorted(
            projects,
            key=lambda project: project.close_date - project.create_date,
        )


charity_project_crud = CRUDCharityProject(CharityProject)
