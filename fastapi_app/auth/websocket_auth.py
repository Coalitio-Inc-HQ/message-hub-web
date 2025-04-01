import logging

from fastapi import WebSocket, HTTPException

from fastapi_app.auth.utilities import chek_jwt, chek_jwt_and_get_user
from database.database_engine import AsyncSession, get_session
from fastapi_app.auth.auth_schemes import *

from typing import Any

logger = logging.getLogger()

async def websocket_auth_verify_jwt(websocket: WebSocket, token: str, db_session: AsyncSession) -> Any:
    try:
        return chek_jwt(token)
    except:
        await websocket.close(code=1008, reason="Ошибка аутентификации")
        raise HTTPException(status_code=401)


async def websocket_auth_base(websocket: WebSocket, token: str, db_session: AsyncSession) -> ExtUserDTO:
    try: 
        user = await chek_jwt_and_get_user(token, db_session)
        if user:
            return user
        else:
            raise Exception()
    except:
        await websocket.close(code=1008, reason="Пользователь не активен")
        raise HTTPException(status_code=401)


async def websocket_auth_active(websocket: WebSocket, token: str, db_session: AsyncSession) -> ExtUserDTO:
    user = await websocket_auth_base(token, db_session)
    if not user.is_active:
        await websocket.close(code=1008, reason="Пользователь не активен")
        raise HTTPException(status_code=401)
    else:
        return user