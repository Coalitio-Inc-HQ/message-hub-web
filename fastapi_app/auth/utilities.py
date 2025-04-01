import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from core.config_reader import config

from datetime import timezone 
import datetime 

from database.database_engine import AsyncSession

from fastapi_app.auth.auth_schemes import *
from database.database_schemes import *
from sqlalchemy import select
from database.utilities import select_data_one_or_none_quer

from core.redis import redis

def chek_jwt(jwt_str: str) -> Any:
    """
    Проверяет валидность jwt.
    """
    payload = jwt.decode(jwt_str, config.SECRET_AUTH, algorithms=["HS256"])
    if payload["exp"]<datetime.datetime.now(timezone.utc).timestamp():
        raise InvalidTokenError("Токен истёк")
    return payload


async def chek_jwt_and_get_user(jwt_str: str, db_session: AsyncSession) -> ExtUserDTO | None:
    """
    Проверяет пользователя и jwt.
    """
    payload = chek_jwt(jwt_str)
    use_redis = True

    try:
        user = await get_user_cache(payload["user_id"])
    except:
        user = None
        use_redis = False
    if not user:
        user: ExtUserDTO = await select_data_one_or_none_quer(db_session, ExtUserDTO, 
            select(UserORM, RoleORM.id.label("role_id"), RoleORM.name.label("role_name"), RoleORM.permissions.label("role_permissions")).join(RoleORM, isouter=True)
            .where(UserORM.id == payload["user_id"]))
        
        if use_redis:
            try:
                await set_user_cache(user)
            except:
                pass

    return user


def chek_permission(path: str, user: ExtUserDTO) -> bool:
    """
    Проверяет разрешение.
    chek_permission(user.crate) истена если: 
    user.permissions:{
        "user":{
            "crate": true
        }
    }
    или это root пользователь.
    """
    if user.is_root:
        return True
    
    if not user.role_permissions:
        return False

    sp_path = path.split(".")

    node = user.role_permissions
    for key in sp_path:
        if key in node:
            node = node[key]
        else:
            return False
    return node == True


def get_update_fields(object: BaseModel) -> dict:
    """
    Возращяет поля подлежащие обновлению.
    (Поле не подлежит обновлению если в нём содержится объект типа NullUpdate)
    """
    res = {}
    for key, value in object.model_dump().items():
        if not isinstance(value, NullUpdate):
            res[key]=value
    return res


async def set_user_cache(user: ExtUserDTO):
    """
    Записывает пользователя в кеш
    """
    await redis.set(f"user_{user.id}", user.model_dump_json(), config.CACHE_USER_MINUTES)


async def get_user_cache(user_id: int)-> ExtUserDTO | None:
    """
    Читает пользователя из кеша
    """
    res = await redis.get(f"user_{user_id}")
    if res:
        res = ExtUserDTO.model_validate_json(res)
    return res 

async def delete_user_cache_by_role_id(role_id: int):
    """Удаляет кеш пользователей с указанным role_id"""
    cursor = 0

    while True:
        cursor, keys = await redis.scan(cursor, match="user_*", count=100)
        
        for key in keys:
            user_data = await redis.get(key)
            if user_data:
                user = ExtUserDTO.model_validate_json(user_data)
                if user.role_id == role_id:
                    redis.delete(key)
        
        if cursor == 0:
            break
    