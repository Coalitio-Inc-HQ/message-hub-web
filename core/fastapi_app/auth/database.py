from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship
from sqlalchemy import String,Boolean,CheckConstraint,text,ForeignKey,JSON

from core.database.database import engine

import asyncio

from typing import Annotated

from datetime import datetime

from core.database.database import get_session

str_256=Annotated[str,256]

class Base(DeclarativeBase):
    type_annotation_map={
        str_256: String(256)
    }


class User(Base):
    __tablename__ = "user"
    id:Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str_256] = mapped_column(CheckConstraint("name != ''"))
    email:Mapped[str_256]= mapped_column(CheckConstraint("email LIKE '%@%.%'"),unique=True,index=True,nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user_id:Mapped[int] = mapped_column(unique=True)

async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)

