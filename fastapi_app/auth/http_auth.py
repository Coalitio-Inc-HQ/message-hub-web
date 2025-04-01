import logging

from fastapi import Depends, HTTPException, Body

from fastapi_app.auth.utilities import chek_jwt, chek_jwt_and_get_user
from database.database_engine import AsyncSession, get_session
from fastapi_app.auth.auth_schemes import *

from typing import Any

logger = logging.getLogger()

async def http_auth_verify_jwt(token: str = Body(), db_session: AsyncSession=Depends(get_session))-> Any:
    try:
        return chek_jwt(token)
    except:
        raise HTTPException(status_code=401)


async def http_auth_base(token: str = Body(), db_session: AsyncSession=Depends(get_session)) -> ExtUserDTO:
    try: 
        user = await chek_jwt_and_get_user(token, db_session)
        if user:
            return user
        else:
            raise HTTPException(status_code=401)
    except:
        raise HTTPException(status_code=401)


async def http_auth_active(user: ExtUserDTO = Depends(http_auth_base)) -> ExtUserDTO:
    if not user.is_active:
        raise HTTPException(status_code=401)
    else:
        return user