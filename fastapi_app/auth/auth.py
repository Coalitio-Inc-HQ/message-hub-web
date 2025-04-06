import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from database.database_schemes import *
from sqlalchemy import select
from fastapi_app.auth.auth_schemes import *

from database.database_engine import get_session, AsyncSession
from database.utilities import insert_data, select_data_one_or_none_quer, select_data_arr, update_data, select_data_one_or_none

from fastapi import APIRouter, Depends, HTTPException, Body, Response

from fastapi_app.main_client.main_client_requests import register_user

from passlib.context import CryptContext

from core.config_reader import config

from datetime import timezone 
import datetime 

from fastapi_app.auth.utilities import chek_permission, get_update_fields, set_user_cache, delete_user_cache_by_role_id
from fastapi_app.auth.http_auth import http_auth_active

from core.redis import redis

import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

user_router = APIRouter()
role_router = APIRouter()

@router.post(path="/login")
async def login_user(response: Response, email: str = Body(), password: str = Body(), db_session: AsyncSession=Depends(get_session)):
    """
    Аутентификация
    """
    user: ExtUserDTO =  await select_data_one_or_none_quer(db_session, ExtUserDTO, 
            select(UserORM, RoleORM.id.label("role_id"), RoleORM.name.label("role_name"), RoleORM.permissions.label("role_permissions")).join(RoleORM, isouter=True)
            .where(UserORM.email == email))

    if pwd_context.verify(password, user.hashed_password):
        return {
                "jwt": jwt.encode(
                        {
                            "user_id": user.id, 
                            "exp": (datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
                        },
                        key=config.SECRET_AUTH,
                        algorithm="HS256",
                    ),
                "userInfo": user,
            }
    else:
        raise HTTPException(401)


@user_router.post(path="/create")
async def create_user(register_info: UserCreateDTO, db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Создаёт нового пользователя
    """
    if not chek_permission("user.create", user):
        raise HTTPException(403, user.model_dump())

    main_register = await register_user(register_info.name, register_info.icon_url)

    res = await insert_data(db_session, UserORM,
                    data={
                        "id": main_register["user_id"],
                        "name":register_info.name,
                        "email":register_info.email,
                        "hashed_password": pwd_context.hash(register_info.password),
                        "is_active": True,
                        "is_root": False,
                        "icon_url": register_info.icon_url,
                        "role_id": register_info.role_id,
                        # "is_completed_tutorial": False,
                        "settings": {}
                        },
                    )
    
    return OutExtUserDTO.model_validate(
        {
            "id": main_register["user_id"],
            "name":register_info.name,
            "email":register_info.email,
            "is_active": True,
            "is_root": False,
            "icon_url": register_info.icon_url,
            "role_id": register_info.role_id,
            # "is_completed_tutorial": False,
            "settings": {}
            },
        )


@user_router.post(path="/info")
async def user_info(temp: str = Body(default=None), db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Метод для получения сведений о пользователе и проверки валидности токена.
    """
    return user


@user_router.post(path="/list")
async def list_user(temp: str = Body(default=None), db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Получает пользователей
    """
    if not chek_permission("user.list", user):
        raise HTTPException(403, user.model_dump())


    return await select_data_arr(db_session, UserORM, OutExtUserDTO)


self_update_filds = {"name", "email", "password", "icon_url", "settings"} # Перечень полей разрещённых для обновления пользователем самому себе.
@user_router.post(path="/update")
async def update_user(update_user: UserUpdateDTO, db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Обновляет пользователя
    """
    updated_filds = get_update_fields(update_user)
    updated_filds.pop("id")

    if "password" in updated_filds:
        updated_filds["hashed_password"] = pwd_context.hash(updated_filds["password"])
        updated_filds.pop("password")

    can_self_update = True # Содержит только поля разрезённые для обноления самому себе
    for key, value in updated_filds.items():
        if not key in self_update_filds:
            can_self_update = False

    if can_self_update and update_user.id == user.id or chek_permission("user.update", user):
        await update_data(db_session, UserORM, UserORM.id == update_user.id, **updated_filds)

        # Реакция на обновление пользователя
        new_user = await select_data_one_or_none_quer(db_session, ExtUserDTO, 
            select(UserORM, RoleORM.id.label("role_id"), RoleORM.name.label("role_name"), RoleORM.permissions.label("role_permissions")).join(RoleORM, isouter=True)
            .where(UserORM.id == user.id))
        await set_user_cache(new_user)
        #

        return {"status":"ok"}
    else:
        raise HTTPException(403, user.model_dump())


@user_router.post(path="/settings/set")
async def set_settings(key: str, value: Any, db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Устанавливает ключ в настройках пользователя
    """
    user.settings[key] = value
    await update_data(db_session, UserORM, UserORM.id == update_user.id, settings=user.settings)

    # Событие обновления настроек?
    
    return {"status":"ok"}


@user_router.post(path="/password/chenge/init")
async def init_chenge_password_user(user_id: int = Body(), temp: str = Body(default=None), db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Иницирует смену пароля пользователя по сслке.
    """
    if not chek_permission("user.password.chenge.init", user):
        raise HTTPException(403, user.model_dump())

    last_token = await redis.get(f"password.chenge.init.{user_id}")

    if last_token:
        return {"token": last_token}
    else:
        token = secrets.token_urlsafe(256)
        await redis.set(f"password.chenge.init.{user_id}",token, ex=config.ACCESS_CHENGE_PASSWORD_TOKEN_EXPIRE_MINUTES)
        return {"token": token, "user_id": user_id}


@user_router.post(path="/password/chenge/execute")
async def init_chenge_password_user(user_id: int = Body(), token: str = Body(), password: str = Body(),  db_session: AsyncSession=Depends(get_session)):
    """
    Завершает смену пароля пользователя по сслке.
    """
    rdis_token = await redis.get(f"password.chenge.init.{user_id}")
    if rdis_token==token:
        await update_data(db_session, UserORM, UserORM.id == user_id, hashed_password = pwd_context.hash(password))
        await redis.delete(f"password.chenge.init.{user_id}")
        return {"status": "ok"}
    else:
        raise HTTPException(401)


@role_router.post(path="/create")
async def create_role(role: RoleCreateDTO = Body(), db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Создаёт роль
    """
    if not chek_permission("role.create", user):
        raise HTTPException(403, user.model_dump())

    res = await insert_data(db_session, RoleORM,
                data={
                    "name":role.name,
                    "permissions":role.permissions,
                    "is_hide": False,
                    },
                    return_atr=["id"]
                )
    return RoleDTO(id=res["id"], name=role.name, permissions=role.permissions, is_hide=False)


@role_router.post(path="/list")
async def create_role(temp: str = Body(default=None), db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Получает список ролей
    """
    if not chek_permission("role.list", user):
        raise HTTPException(403, user.model_dump())

    res = await select_data_arr(db_session, RoleORM, RoleDTO, RoleORM.is_hide==False)

    return res


@role_router.post(path="/update")
async def update_role(update_role: RoleUpdateDTO, db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Обновляет роль.
    """
    if not chek_permission("role.update", user):
        raise HTTPException(403, user.model_dump())

    updated_filds = get_update_fields(update_role)
    updated_filds.pop("id")

    await update_data(db_session, RoleORM, RoleORM.id == update_role.id, **updated_filds)

    # Реакция на обновление роли
    await delete_user_cache_by_role_id(update_role.id)
    #

    return await select_data_one_or_none(db_session, RoleORM, RoleDTO, RoleORM.id == update_role.id)

@role_router.post(path="/delete")
async def delete_role(role_ids: list[int], db_session: AsyncSession=Depends(get_session), user: ExtUserDTO = Depends(http_auth_active)):
    """
    Удаляет роли.
    """
    if not chek_permission("role.delete", user):
        raise HTTPException(403, user.model_dump())
    
    users = await select_data_arr(db_session, UserORM, UserDTO, UserORM.role_id.in_(role_ids), UserORM.is_active==True)

    find_roles = set()
    for us in users:
        find_roles.add(us.role_id)
    
    if find_roles:
        raise HTTPException(422, {"fail_delete_roles": list(find_roles)})
    
    await update_data(db_session, RoleORM, RoleORM.id.in_(role_ids), **{"is_hide":True})

    return {"status": "ok"}

router.include_router(user_router, prefix="/user")
router.include_router(role_router, prefix="/role")