import asyncio

from sqlalchemy import Column, String, BigInteger, BLOB, insert
from sqlalchemy.ext.declarative import declarative_base

from database import session_factory, engine

Base = declarative_base()


class UserORM(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)

    # login = Column(String, index=True)
    # password = Column(blob, index=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"  # Состояние объекта


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_models()


if __name__ == '__main__':
    asyncio.run(main())
