from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from passlib.context import CryptContext
from database.database_engine import AsyncSession, session_factory
from sqlalchemy import select
from database.database_schemes import AdminUser
import jwt
from core.config_reader import config
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        async with session_factory() as conn:
            user = (await conn.execute(select(AdminUser).where(AdminUser.login==username))).scalar_one_or_none()

            if not user:
                return False

            is_valid = pwd_context.verify(password, user.hashed_password)

            if is_valid:
                request.session.update({
                    "token": jwt.encode(payload={
                        "user_id": user.id, "time": str(datetime.datetime.now())
                        },key=config.SECRET_AUTH)
                    })

                return True
            else:
                return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        try:
            jwt.decode(token, config.SECRET_AUTH, ["HS256"])
        except:
            return False

        return True

