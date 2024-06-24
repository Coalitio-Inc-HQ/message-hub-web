from pydantic import BaseModel

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class Chat(BaseModel):
    id: int
    user_id: int
    chat_id: int

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    chat_id: int
    user_id: int

class Message(MessageBase):
    id: int
    chat_id: int
    user_id: int

    class Config:
        orm_mode = True
