from pydantic_extra_types import pendulum_dt

from src.core.base_schema import BaseSchema


class EventFeedSchema(BaseSchema):
    host_user_id: str = "api-user"
    title: str
    description: str | None = None
    status: str = "draft"
    start_time: pendulum_dt.DateTime | None = None
    end_time: pendulum_dt.DateTime | None = None
