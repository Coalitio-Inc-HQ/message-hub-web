from sqlalchemy import Column, String, BigInteger, BLOB, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config_reader import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
    # login = Column(String, index=True)
    # password = Column(BLOB)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

engine = create_async_engine(config.DATABASE_URL, echo=config.ECHO)
async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_user(name):
    async with async_session() as session:
        async with session.begin():
            new_user = User(name=name)
            session.add(new_user)
        await session.commit()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_db_and_tables())
