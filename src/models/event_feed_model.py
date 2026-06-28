import pendulum
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.base_model import BaseModel


class EventFeedModel(BaseModel):
    __tablename__ = "event_feeds"

    host_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    start_time: Mapped[pendulum.DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[pendulum.DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
