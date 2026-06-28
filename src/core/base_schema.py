from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic_extra_types import pendulum_dt


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    created: pendulum_dt.DateTime | None = None
    updated: pendulum_dt.DateTime | None = None
    deleted: pendulum_dt.DateTime | None = None
