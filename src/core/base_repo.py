from typing import Any, Generic, TypeVar
from uuid import UUID

import pendulum
from sqlalchemy.ext.asyncio import AsyncSession

from .base_model import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepo(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: type[T]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, entity_id: UUID) -> T | None:
        result = await self.session.get(self.model_class, entity_id)
        return result if result and result.deleted is None else None

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity_id: UUID, update_data: dict[str, Any]) -> T | None:
        entity = await self.get_by_id(entity_id)
        if not entity:
            return None
        for key, value in update_data.items():
            setattr(entity, key, value)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        entity.deleted = pendulum.now("UTC")
        return True
