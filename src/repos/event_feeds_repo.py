from sqlalchemy import select

from src.core.base_repo import BaseRepo
from src.models.event_feed_model import EventFeedModel


class EventFeedRepo(BaseRepo[EventFeedModel]):
    def __init__(self, session):
        super().__init__(session, EventFeedModel)

    async def list(self, limit: int = 100, offset: int = 0) -> list[EventFeedModel]:
        query = (
            select(EventFeedModel)
            .where(EventFeedModel.deleted.is_(None))
            .order_by(EventFeedModel.created.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
