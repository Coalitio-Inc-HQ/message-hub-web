from core.fastapi_app.auth.user_manager import get_user_manager
from core.fastapi_app.auth.auth import get_jwt_strategy
from fastapi import WebSocket,Depends,HTTPException
from core.fastapi_app.auth.database import User
async def websocket_auth_base(websocket: WebSocket, user_manager=Depends(get_user_manager)):
    try:
        cookie = websocket.cookies['fastapiusersauth']
        user = await (get_jwt_strategy().read_token(cookie, user_manager))
    except:
        await websocket.accept()
        await websocket.close(code=1008,reason="Ошибка аутентификации")
        raise HTTPException(status_code=401)
    # User is authenticated, you can also check if he is active
    if user and user.is_active:
        return user

    # The credentials are invalid, expired, or the user does not exist or inactive
    await websocket.accept()
    await websocket.close(code=1008, reason="Ошибка аутентификации")
    raise HTTPException(status_code=401)
    # return None


async def websocket_auth_actve(websocket: WebSocket,user:User = Depends(websocket_auth_base)):
    if not User.is_active:
        await websocket.accept()
        await websocket.close(code=1008, reason="Пользователь не активен")
        raise HTTPException(status_code=401)
    else:
        return user

