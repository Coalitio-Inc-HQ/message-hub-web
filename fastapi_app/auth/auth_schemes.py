from pydantic import Field, BaseModel
from typing import Any

class NullUpdate(BaseModel):
    """
    Объект данного класса говорит что обновлять поле не нужно.
    """
    pass

class UserCreateDTO(BaseModel):
    name: str = Field(max_length=256, pattern=".$")
    email: str = Field(max_length=256, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    password: str = Field(max_length=256, pattern="........$")

    icon_url: str | None = Field(max_length=256)

    role_id: int | None

class UserDTO(BaseModel):
    id: int
    name: str = Field(max_length=256, pattern=".$")
    email: str = Field(max_length=256, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    hashed_password: str = Field(max_length=1024)
    is_active: bool
    is_root: bool

    icon_url: str | None = Field(max_length=256)

    role_id: int | None

    settings: dict


class UserUpdateDTO(BaseModel):
    id: int
    name: str = Field(max_length=256, pattern=".$", default = NullUpdate)
    email: str = Field(max_length=256, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', default = NullUpdate)
    password: str = Field(max_length=256, pattern="........$", default = NullUpdate)
    is_active: bool  = NullUpdate
    is_root: bool  = NullUpdate

    icon_url: str | None = Field(max_length=256, default=NullUpdate)

    role_id: int | None  = NullUpdate


class ExtUserDTO(BaseModel):
    id: int
    name: str = Field(max_length=256, pattern=".$")
    email: str = Field(max_length=256, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    hashed_password: str = Field(max_length=1024)
    is_active: bool
    is_root: bool

    icon_url: str | None = Field(max_length=256)


    settings: dict

    role_id: int | None
    role_name: str | None = Field(max_length=256, pattern=".$")
    role_permissions: Any | None

class OutExtUserDTO(BaseModel):
    id: int
    name: str = Field(max_length=256, pattern=".$")
    email: str = Field(max_length=256, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    is_active: bool
    is_root: bool

    icon_url: str | None = Field(max_length=256)


    settings: dict

    role_id: int | None


class RoleCreateDTO(BaseModel):
    name: str = Field(max_length=256, pattern=".$")
    permissions: Any


class RoleDTO(BaseModel):
    id: int
    name: str = Field(max_length=256, pattern=".$")
    permissions: Any

    is_hide: bool

class RoleUpdateDTO(BaseModel):
    id: int
    name: str = Field(max_length=256, pattern=".$", default=NullUpdate)
    permissions: Any = NullUpdate