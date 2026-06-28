import uuid

import pendulum
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid6 import uuid7


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
    created: Mapped[pendulum.DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: pendulum.now("UTC")
    )
    updated: Mapped[pendulum.DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: pendulum.now("UTC"),
        onupdate=lambda: pendulum.now("UTC"),
    )
    deleted: Mapped[pendulum.DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        self.deleted = pendulum.now("UTC")

    def restore(self) -> None:
        self.deleted = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted is not None
