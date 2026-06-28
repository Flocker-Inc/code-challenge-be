from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from src.auth import verify_api_key
from src.models.event_feed_model import EventFeedModel
from src.repos.event_feeds_repo import EventFeedRepo
from src.schemas.event_feed_schema import EventFeedSchema
from src.session import get_async_session

router = APIRouter(prefix="/event_feeds", tags=["event_feeds"], dependencies=[Depends(verify_api_key)])


@router.get("/", response_model=list[EventFeedSchema])
async def list_event_feeds(request: Request, limit: int = 100, offset: int = 0):
    async with get_async_session() as session:
        repo = EventFeedRepo(session)
        feeds = await repo.list(limit=limit, offset=offset)
        return [EventFeedSchema.model_validate(f) for f in feeds]


@router.get("/{feed_id}", response_model=EventFeedSchema)
async def get_event_feed(feed_id: UUID, request: Request):
    async with get_async_session() as session:
        repo = EventFeedRepo(session)
        feed = await repo.get_by_id(feed_id)
        if not feed:
            raise HTTPException(status_code=404, detail="EventFeed not found")
        return EventFeedSchema.model_validate(feed)


@router.post("/", response_model=EventFeedSchema, status_code=201)
async def create_event_feed(feed_data: EventFeedSchema, request: Request):
    async with get_async_session() as session:
        repo = EventFeedRepo(session)
        feed_model = EventFeedModel(**feed_data.model_dump(exclude={"id", "created", "updated", "deleted"}))
        created = await repo.create(feed_model)
        return EventFeedSchema.model_validate(created)


@router.put("/{feed_id}", response_model=EventFeedSchema)
async def update_event_feed(feed_id: UUID, feed_data: EventFeedSchema, request: Request):
    async with get_async_session() as session:
        repo = EventFeedRepo(session)
        update_dict = feed_data.model_dump(exclude_unset=True, exclude={"id", "created"})
        updated = await repo.update(feed_id, update_dict)
        if not updated:
            raise HTTPException(status_code=404, detail="EventFeed not found")
        return EventFeedSchema.model_validate(updated)


@router.delete("/{feed_id}")
async def delete_event_feed(feed_id: UUID, request: Request):
    async with get_async_session() as session:
        repo = EventFeedRepo(session)
        success = await repo.delete(feed_id)
        if not success:
            raise HTTPException(status_code=404, detail="EventFeed not found")
        return {"message": "deleted"}
