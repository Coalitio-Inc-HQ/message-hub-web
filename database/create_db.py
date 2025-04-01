from database.database_schemes import Base
from database.database_engine import engine
from sqlalchemy import insert, select, func
from passlib.context import CryptContext
from database.database_schemes import UserORM
from fastapi_app.main_client.main_client_requests import register_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        res = await conn.execute(select(func.count(UserORM.id)).where(UserORM.is_root==True))
        res = res.scalar()
        
        if res == 0:
           main_register = await register_user("Администратор", None)

           await conn.execute(insert(UserORM).values(
                        id = main_register["user_id"],
                        name = "Администратор",
                        email = "admin@admin.admin",
                        hashed_password = pwd_context.hash("A1234567!"),
                        is_active = True,
                        is_root = True,
                        icon_url = None,
                        role_id = None,
                        settings={},
                    ))

