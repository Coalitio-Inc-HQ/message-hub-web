from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, CheckConstraint, ForeignKey, JSON

from typing import Annotated, Any

from .database_engine import get_session

str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }


class UserORM(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(CheckConstraint("name != ''"))
    email: Mapped[str_256] = mapped_column(CheckConstraint("email LIKE '%@%.%'"), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_root: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    icon_url: Mapped[str|None] = mapped_column(String(256))

    role_id: Mapped[int | None] = mapped_column(ForeignKey("role.id"), nullable=True)

    settings: Mapped[dict] = mapped_column(JSON, default={})


class RoleORM(Base):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(CheckConstraint("name != ''"))
    permissions: Mapped[Any] = mapped_column(JSON)

    is_hide: Mapped[bool]
