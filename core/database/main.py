import asyncio

from sqlalchemy import Column, String, BigInteger, BLOB, insert,select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import  AsyncSession

from .database import session_factory, engine
from core.fastapi_app.schemes import UserDTO

Base = declarative_base()


class UserORM(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(128))

    hash_password = Column(String(1024))
    login = Column(String(128), index=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"  # Состояние объекта


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def save_user(session: AsyncSession, id: int, name: str, hash_password: str, login) -> None:
    """
    Сохранение пользователя в БД.
    """
    session.add(UserORM(id=id, name=name, hash_password=hash_password, login=login))
    await session.commit()


async def get_user_by_id(session:AsyncSession, id: int) -> UserDTO:
    """
    Получение пользователя из БД по индентификатору.
    """
    res = await session.execute(select(UserORM).where(UserORM.id==id))
    res_orm = res.scalar()
    if res_orm:
        return UserDTO.model_validate(res_orm,from_attributes=True)


async def get_user_by_login(session:AsyncSession, login: str) -> UserDTO:
    """
    Получение пользователя из БД по login.
    """
    res = await session.execute(select(UserORM).where(UserORM.login==login))
    res_orm = res.scalar()
    if res_orm:
        return UserDTO.model_validate(res_orm,from_attributes=True)


async def main():
    await init_models()


if __name__ == '__main__':
    asyncio.run(main())
