from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.user import User
from app.schemas.donation import (
    DonationCreate,
    DonationCreateResponse,
    DonationDB,
)
from app.services.investment import distribute_investments

router = APIRouter()


@router.post(
    "/",
    response_model=DonationCreateResponse,
    response_model_exclude_none=True,
)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    new_donation = await donation_crud.create(donation_in, session, user)
    sources = await charity_project_crud.get_not_fully_invested(session)
    changed = distribute_investments(target=new_donation, sources=sources)
    session.add_all(changed)
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    "/",
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    return await donation_crud.get_multi(session)


@router.get(
    "/my",
    response_model=list[DonationCreateResponse],
    response_model_exclude_none=True,
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    return await donation_crud.get_by_user(session=session, user=user)
