from database.database_schemes import Base
from database.database_engine import engine
from sqlalchemy import insert, select
from passlib.context import CryptContext
from database.database_schemes import AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        if not (await conn.execute(select(AdminUser).where(AdminUser.login=="admin"))).one_or_none():
            await conn.execute(insert(AdminUser).values(login="admin", hashed_password=pwd_context.hash("adminA1234567!")))
