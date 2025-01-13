from sqladmin import Admin, ModelView
from database.database_engine import engine
from database.database_schemes import AdminUser, User as Us
from fastapi_app.admin.auth import AdminAuth, Admin
from fastapi_app.main_client.main_client_requests import register_user

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def install_admin(app):

    admin = Admin(app, engine, authentication_backend=AdminAuth("123"))

    class UserAdmin(ModelView, model=AdminUser):
        column_list = [AdminUser.id, AdminUser.login, AdminUser.hashed_password]

        async def insert_model(self, request, data):
            data["hashed_password"] = pwd_context.hash(data["hashed_password"])
            return await super().insert_model(request, data)

        async def update_model(self, request, pk, data):
            data["hashed_password"] = pwd_context.hash(data["hashed_password"])
            return await super().update_model(request, pk, data)
        
    class User(ModelView, model=Us):
        column_exclude_list = [Us.id]

        async def insert_model(self, request, data):
            data["hashed_password"] = pwd_context.hash(data["hashed_password"])

            main_register = await register_user(data["name"])
            data["id"] = main_register["user_id"]

            return await super().insert_model(request, data)

        async def update_model(self, request, pk, data):
            data["hashed_password"] = pwd_context.hash(data["hashed_password"])
            return await super().update_model(request, pk, data)

    admin.add_view(UserAdmin)
    admin.add_view(User)