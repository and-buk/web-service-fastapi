from typing import Any

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from web.app.models import UserInfo


async def create_user_info_in_db(
    session: AsyncSession,
    user_name: str,
    first_name: str,
    second_name: str,
    email: str,
    password: str,
):
    """."""
    query = (
        insert(UserInfo)
        .values(
            user_name=user_name,
            first_name=first_name,
            second_name=second_name,
            email=email,
            hashed_password=password,
        )
        .returning(UserInfo)
    )
    result = await session.execute(query)
    await session.commit()
    user_data = result.one()
    return user_data.user_name, user_data.id, user_data.created_at


async def get_user_by_username(session: AsyncSession, user_name):
    query = select(UserInfo).where(UserInfo.user_name == user_name)
    result = await session.execute(query)
    data = result.scalars().one_or_none()
    await session.commit()
    return data


async def get_user_by_email(session: AsyncSession, email: str):
    query = select(UserInfo).where(UserInfo.email == email)
    result = await session.execute(query)
    data = result.scalars().one_or_none()
    await session.commit()
    return data


async def update_user_info(user_name: str, session: AsyncSession, **kwargs: Any):
    """."""
    query = update(UserInfo).where(UserInfo.user_name == user_name).values(**kwargs).returning(UserInfo)
    result = await session.execute(query)
    await session.commit()
    user_data = result.one()
    return user_data
