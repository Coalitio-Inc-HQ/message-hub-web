import logging

from fastapi_app.auth.user_manager import get_user_manager
from fastapi_app.auth.auth import get_jwt_strategy
from fastapi import WebSocket, Depends, HTTPException
from database.database_schemes import User

logger = logging.getLogger()

async def websocket_auth_base(websocket: WebSocket,token: str, user_manager=Depends(get_user_manager)):
    try:
        user = await (get_jwt_strategy().read_token(token, user_manager))
    except:
        await websocket.accept()
        await websocket.close(code=1008, reason="Ошибка аутентификации1")
        raise HTTPException(status_code=401)
    # User is authenticated, you can also check if he is active
    if user and user.is_active:
        return user

    # The credentials are invalid, expired, or the user does not exist or inactive
    await websocket.accept()
    await websocket.close(code=1008, reason="Ошибка аутентификации2")
    raise HTTPException(status_code=401)
    # return None


async def websocket_auth_active(websocket: WebSocket, user: User = Depends(websocket_auth_base)):
    if not user.is_active:
        await websocket.accept()
        await websocket.close(code=1008, reason="Пользователь не активен")
        raise HTTPException(status_code=401)
    else:
        return user