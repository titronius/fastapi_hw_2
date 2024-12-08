from fastapi import HTTPException
from sqlalchemy import select
from models import ORM_CLS, ORM_OBJECT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def add_item(session: AsyncSession, item: ORM_OBJECT):
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        if err.orig.pgcode == "23505":
            raise HTTPException(status_code=409, detail="Item already exists")
        raise err


async def get_item(session: AsyncSession, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJECT:
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(status_code=404, detail="item not found")
    return orm_obj

async def get_items(session: AsyncSession, orm_cls: ORM_CLS, item_params: dict) -> ORM_OBJECT:
    query = select(orm_cls).filter_by(**item_params)
    result = await session.execute(query)
    advertisements = result.scalars().all()
    if not advertisements:
        raise HTTPException(status_code=404, detail="items not found")
    return advertisements

async def delete_item(session: AsyncSession, orm_cls: ORM_CLS, item_id: int):
    orm_obj = await get_item(session, orm_cls, item_id)
    await session.delete(orm_obj)
    await session.commit()
