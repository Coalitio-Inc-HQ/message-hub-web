from fastapi_users.authentication import JWTStrategy
from fastapi_users.authentication import AuthenticationBackend

from core.config_reader import config

from .user_manager import get_user_manager
from database.database_schemes import User
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import BearerTransport

SECRET = config.SECRET_AUTH


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)
