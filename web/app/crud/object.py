from typing import List

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from web.app.models import InboxInfo


async def create_object_info_in_db(session: AsyncSession, data: List[InboxInfo]) -> None:
    """."""
    session.add_all(data)
    await session.commit()


async def get_object_info_from_db(session: AsyncSession, object_name: str) -> InboxInfo.registration_datetime:
    """."""
    query = select(InboxInfo).filter(InboxInfo.filename == object_name)
    result = await session.execute(query)
    data = result.scalars().one()
    await session.commit()
    return data.registration_datetime


async def delete_all_objects_from_db(session: AsyncSession, group_obj_id: str, user_name: str) -> None:
    """."""
    query = (
        f"DELETE FROM inbox WHERE DATE(registration_datetime) = " f"'{group_obj_id}' " f"AND owner_id = '{user_name}'"
    )
    await session.execute(text(query))
    await session.commit()


async def delete_one_object_from_db(session: AsyncSession, obj_name: str) -> None:
    """."""
    query = delete(InboxInfo).filter(InboxInfo.filename == obj_name)
    await session.execute(query)
    await session.commit()
