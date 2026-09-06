from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar
from app.database.models import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: int) -> T | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[T]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def get_paginated(self, limit: int, offset: int) -> list[T]:
        result = await self.session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()