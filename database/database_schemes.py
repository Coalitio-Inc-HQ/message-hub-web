from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, CheckConstraint


from typing import Annotated

from .database_engine import get_session

str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(CheckConstraint("name != ''"))
    email: Mapped[str_256] = mapped_column(CheckConstraint("email LIKE '%@%.%'"), unique=True, index=True,
                                           nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AdminUser(Base):
    __tablename__ = "admin_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str_256] = mapped_column(CheckConstraint("login != ''"))
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)

async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
