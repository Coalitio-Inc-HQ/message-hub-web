from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[int]):
    id: int
    name: str = Field(max_length=256, pattern=".$")
    email: str = Field(max_length=256)
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    user_id: int


class UserCreate(schemas.CreateUpdateDictModel):
    name: str = Field(max_length=256, pattern=".$")
    email: str = Field(max_length=256)
    password: str = Field(max_length=256, pattern="........$")


class UserUpdate(schemas.BaseUserUpdate):
    password: str = Field(max_length=256, pattern="........$")
    email: str = Field(max_length=256)
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None
